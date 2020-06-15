"""GAN Model."""
import functools
import os
from collections import OrderedDict

import cv2
import torch
from PIL import Image

from transform.gan.generator import GlobalGenerator, get_transform

class _RepeatSampler(object):
    """ Sampler that repeats forever.

    Args:
        sampler (Sampler)
    """

    def __init__(self, sampler):
        self.sampler = sampler

    def __iter__(self):
        while True:
            yield from iter(self.sampler)

class FastDataLoader(torch.utils.data.dataloader.DataLoader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        object.__setattr__(self, 'batch_sampler', _RepeatSampler(self.batch_sampler))
        self.iterator = super().__iter__()

    def __len__(self):
        return len(self.batch_sampler.sampler)

    def __iter__(self):
        for i in range(len(self)):
            yield next(self.iterator)

class DataLoader:
    """Dataset loader class."""

    def __init__(self, opt, cv_img):
        """
        Construct Data loader.

        :param opt: <Config> configuration to use
        :param cv_img: <RGB> image
        """
        super(DataLoader, self).__init__()

        self.dataset = Dataset()
        self.dataset.initialize(opt, cv_img)

        self.dataloader = FastDataLoader(
            self.dataset,
            batch_size=opt.batch_size,
            shuffle=not opt.serial_batches,
            num_workers=int(opt.n_threads),
        )

    def load_data(self):
        """
        Return loaded data.

        :return: <> loaded data
        """
        return self.dataloader

    def __len__(self):
        """
        Redefine  __len___ for DataLoader.

        :return: <int> 1
        """
        return 1


class Dataset(torch.utils.data.Dataset):
    """Dataset class."""

    def __init__(self):
        """Dataset Constructor."""
        super(Dataset, self).__init__()

    def initialize(self, opt, cv_img):
        """
        Initialize the Dataset.

        :param opt:
        :param cv_img:
        :return:
        """
        self.opt = opt

        self.A = Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))
        self.dataset_size = 1

    def __getitem__(self, index):
        """
        Redefine Dataset __getitem__.

        :param index:
        :return:
        """
        transform_a = get_transform(self.opt)
        a_tensor = transform_a(self.A.convert("RGB"))

        b_tensor = inst_tensor = feat_tensor = 0

        input_dict = {
            "label": a_tensor,
            "inst": inst_tensor,
            "image": b_tensor,
            "feat": feat_tensor,
            "path": "",
        }

        return input_dict

    def __len__(self):
        """
        Redefine  __len___ for Dataset.

        :return: <int> 1
        """
        return 1


class DeepModel():
    """Deep Model."""

    def initialize(self, opt, gpu_ids, checkpoints_dir):
        """
        Deep Model initialize.

        :param opt: <Config> configuration to use
        :param gpu_ids: <int[]|None> gpu id to use (None = cpu)
        :param checkpoints_dir: <string> path to the directoy where models are
        :return:
        """
        self.opt = opt
        self.checkpoints_dir = checkpoints_dir

        if gpu_ids is None:
            self.gpu_ids = []
        else:
            self.gpu_ids = gpu_ids

        self.net_g = self.__define_g(
            opt.input_nc,
            opt.output_nc,
            opt.ngf,
            opt.net_g,
            opt.n_downsample_global,
            opt.n_blocks_global,
            opt.n_local_enhancers,
            opt.n_blocks_local,
            opt.norm,
            self.gpu_ids,
        )

        # load networks
        self.__load_network(self.net_g)

    def inference(self, label, inst):
        """
        Infere an image.

        :param label: <> label
        :param inst: <> isnt
        :return: <RGB> image
        """
        # Encode Inputs
        input_label, _, _, _ = self.__encode_input(label, inst, infer=True)

        # Fake Generation
        input_concat = input_label

        with torch.no_grad():
            fake_image = self.net_g.forward(input_concat)

        return fake_image

    # helper loading function that can be used by subclasses
    def __load_network(self, network):

        save_path = os.path.join(self.checkpoints_dir)

        state_dict = torch.load(save_path)

        if len(self.gpu_ids) > 1:
            new_state_dict = OrderedDict()

            for k, v in state_dict.items():
                name = "module." + k  # add `module.`
                new_state_dict[name] = v
        else:
            new_state_dict = state_dict

        network.load_state_dict(new_state_dict)

    def __encode_input(
            self, label_map, inst_map=None, real_image=None, feat_map=None, infer=False
    ):
        if len(self.gpu_ids) > 0:
            input_label = label_map.data.cuda()  # GPU
        else:
            input_label = label_map.data  # CPU

        return input_label, inst_map, real_image, feat_map

    @staticmethod
    def __weights_init(m):
        classname = m.__class__.__name__
        if classname.find("Conv") != -1:
            m.weight.data.normal_(0.0, 0.02)
        elif classname.find("BatchNorm2d") != -1:
            m.weight.data.normal_(1.0, 0.02)
            m.bias.data.fill_(0)

    def __define_g(
            self,
            input_nc,
            output_nc,
            ngf,
            net_g,
            n_downsample_global=3,
            n_blocks_global=9,
            n_local_enhancers=1,
            n_blocks_local=3,
            norm="instance",
            gpu_ids=None,
    ):
        norm_layer = self.__get_norm_layer(norm_type=norm)

        # model
        net_g = GlobalGenerator(
            input_nc, output_nc, ngf, n_downsample_global, n_blocks_global, norm_layer
        )

        if len(gpu_ids) > 1:
            net_g = torch.nn.DataParallel(net_g, gpu_ids)

        if len(gpu_ids) > 0:
            net_g.cuda(gpu_ids[0])

        net_g.apply(self.__weights_init)

        return net_g

    @staticmethod
    def __get_norm_layer(norm_type="instance"):
        norm_layer = functools.partial(torch.nn.InstanceNorm2d, affine=False)
        return norm_layer
