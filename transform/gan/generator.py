"""GAN generator."""
import numpy as np
import torch
from PIL import Image
from torchvision import transforms as transforms


class GlobalGenerator(torch.nn.Module):
    """Global Generator."""

    def __init__(
            self,
            input_nc,
            output_nc,
            ngf=64,
            n_downsampling=3,
            n_blocks=9,
            norm_layer=torch.nn.BatchNorm2d,
            padding_type="reflect",
    ):
        """
        Global Generator Constructor.

        :param input_nc:
        :param output_nc:
        :param ngf:
        :param n_downsampling:
        :param n_blocks:
        :param norm_layer:
        :param padding_type:
        """
        if n_blocks < 0:
            raise AssertionError()
        super(GlobalGenerator, self).__init__()

        activation = torch.nn.ReLU(True)
        # activation = torch.nn.DataParallel(activation)

        model = [
            torch.nn.ReflectionPad2d(3),
            torch.nn.Conv2d(input_nc, ngf, kernel_size=7, padding=0),
            norm_layer(ngf),
            activation,
        ]
        # downsample
        for i in range(n_downsampling):
            mult = 2 ** i
            model += [
                torch.nn.Conv2d(
                    ngf * mult, ngf * mult * 2, kernel_size=3, stride=2, padding=1
                ),
                norm_layer(ngf * mult * 2),
                activation,
            ]

        # resnet blocks
        mult = 2 ** n_downsampling
        for _ in range(n_blocks):
            model += [
                ResnetBlock(
                    ngf * mult,
                    padding_type=padding_type,
                    activation=activation,
                    norm_layer=norm_layer,
                )
            ]

        # upsample
        for i in range(n_downsampling):
            mult = 2 ** (n_downsampling - i)
            model += [
                torch.nn.ConvTranspose2d(
                    ngf * mult,
                    int(ngf * mult / 2),
                    kernel_size=3,
                    stride=2,
                    padding=1,
                    output_padding=1,
                ),
                norm_layer(int(ngf * mult / 2)),
                activation,
            ]
        model += [
            torch.nn.ReflectionPad2d(3),
            torch.nn.Conv2d(ngf, output_nc, kernel_size=7, padding=0),
            torch.nn.Tanh(),
        ]

        self.model = torch.nn.Sequential(*model)
        # self.model = torch.nn.DataParallel(self.model)

    def forward(self, i):
        """
        Global Generator forward.

        :param i: <> input
        :return:
        """
        return self.model(i)


class ResnetBlock(torch.nn.Module):
    """Define a resnet block."""

    def __init__(
            self,
            dim,
            padding_type,
            norm_layer,
            activation=None,
            use_dropout=False,
    ):
        """
        Resnet Block constuctor.

        :param dim: <> dim
        :param padding_type: <> padding_type
        :param norm_layer: <> norm_layer
        :param activation: <> activation
        :param use_dropout: <> use_dropout
        """
        super(ResnetBlock, self).__init__()

        if activation is None:
            activation = torch.nn.ReLU(True)

        self.conv_block = self.__build_conv_block(
            dim, padding_type, norm_layer, activation, use_dropout
        )

    @staticmethod
    def __build_conv_block(
            dim, padding_type, norm_layer, activation, use_dropout
    ):
        conv_block = []
        p = 0
        conv_block, p = ResnetBlock.__increment_padding_conv_block(conv_block, p, padding_type)

        conv_block += [
            torch.nn.Conv2d(dim, dim, kernel_size=3, padding=p),
            norm_layer(dim),
            activation,
        ]
        if use_dropout:
            conv_block += [torch.nn.Dropout(0.5)]

        p = 0
        conv_block, p = ResnetBlock.__increment_padding_conv_block(conv_block, p, padding_type)
        conv_block += [
            torch.nn.Conv2d(dim, dim, kernel_size=3, padding=p),
            norm_layer(dim),
        ]

        return torch.nn.Sequential(*conv_block)

    @staticmethod
    def __increment_padding_conv_block(conv_block, p, padding_type):
        if padding_type == "reflect":
            conv_block += [torch.nn.ReflectionPad2d(1)]
        elif padding_type == "replicate":
            conv_block += [torch.nn.ReplicationPad2d(1)]
        elif padding_type == "zero":
            p = 1
        else:
            raise NotImplementedError("padding [%s] is not implemented" % padding_type)
        return conv_block, p

    def forward(self, x):
        """
        Resnet Block forward.

        :param x: <> input
        :return: <> out
        """
        out = x + self.conv_block(x)
        return out


def get_transform(opt, method=Image.BICUBIC, normalize=True):
    """
    Get transform list.

    :param opt: <Config> configuration
    :param method: <> transformation method used
    :param normalize: <boolean> if true normalization is enable
    :return:
    """
    transform_list = []

    base = float(2 ** opt.n_downsample_global)
    if opt.net_g == "local":
        base *= 2 ** opt.n_local_enhancers
    transform_list.append(
        transforms.Lambda(lambda img: make_power_2(img, base, method))
    )

    transform_list += [transforms.ToTensor()]

    if normalize:
        transform_list += [transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))]
    return transforms.Compose(transform_list)


def make_power_2(img, base, method=Image.BICUBIC):
    """
    Make power 2.

    :param img: <> image
    :param base: <> base
    :param method: <> method
    :return:
    """
    ow, oh = img.size
    h = int(round(oh / base) * base)
    w = int(round(ow / base) * base)
    if (h == oh) and (w == ow):
        return img
    return img.resize((w, h), method)


def tensor2im(image_tensor, imtype=np.uint8, normalize=True):
    """
    Convert a Tensor into a Numpy array.

    :param image_tensor: <> image tensor
    :param imtype: <imtype> the desired type of the converted numpy array
    :param normalize: <Boolean> if true normalization is enable
    :return:
    """
    if isinstance(image_tensor, list):
        return tesor2im_list(image_tensor, imtype, normalize)
    else:
        return tensor2im_not_list(image_tensor, imtype, normalize)


def tensor2im_not_list(image_tensor, imtype, normalize):
    image_numpy = image_tensor.cpu().float().numpy()
    image_numpy = tensor2im_normalize(image_numpy, normalize)
    image_numpy = np.clip(image_numpy, 0, 255)
    if image_numpy.shape[2] == 1 or image_numpy.shape[2] > 3:
        image_numpy = image_numpy[:, :, 0]
    return image_numpy.astype(imtype)


def tesor2im_list(image_tensor, imtype, normalize):
    image_numpy = []
    for i in image_tensor:
        image_numpy.append(tensor2im(i, imtype, normalize))
    return image_numpy


def tensor2im_normalize(image_numpy, normalize):
    if normalize:
        image_numpy = (np.transpose(image_numpy, (1, 2, 0)) + 1) / 2.0 * 255.0
    else:
        image_numpy = np.transpose(image_numpy, (1, 2, 0)) * 255.0
    return image_numpy
