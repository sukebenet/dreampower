from PIL import Image
import numpy as np
import cv2
import torchvision.transforms as transforms
import torch
import io
import os
import functools

class DataLoader():

	def __init__(self, opt, cv_img):
		super(DataLoader, self).__init__()

		self.dataset = Dataset()
		self.dataset.initialize(opt, cv_img)

		self.dataloader = torch.utils.data.DataLoader(
			self.dataset,
			batch_size=opt.batchSize,
			shuffle=not opt.serial_batches,
			num_workers=int(opt.nThreads))

	def load_data(self):
		return self.dataloader

	def __len__(self):
		return 1

class Dataset(torch.utils.data.Dataset):
	def __init__(self):
		super(Dataset, self).__init__()

	def initialize(self, opt, cv_img):
		self.opt = opt
		self.root = opt.dataroot

		self.A = Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))
		self.dataset_size = 1
	
	def __getitem__(self, index):        

		transform_A = get_transform(self.opt)
		A_tensor = transform_A(self.A.convert('RGB'))

		B_tensor = inst_tensor = feat_tensor = 0

		input_dict = {'label': A_tensor, 'inst': inst_tensor, 'image': B_tensor, 
					  'feat': feat_tensor, 'path': ""}

		return input_dict

	def __len__(self):
		return 1    

class DeepModel(torch.nn.Module):

	def initialize(self, opt):

		self.opt = opt

		self.gpu_ids = [] #FIX CPU

		self.netG = self.__define_G(opt.input_nc, opt.output_nc, opt.ngf, opt.netG, 
									  opt.n_downsample_global, opt.n_blocks_global, opt.n_local_enhancers, 
									  opt.n_blocks_local, opt.norm, self.gpu_ids)        

		# load networks
		self.__load_network(self.netG)
	
	def inference(self, label, inst):
		
		# Encode Inputs        
		input_label, inst_map, _, _ = self.__encode_input(label, inst, infer=True)

		# Fake Generation
		input_concat = input_label        
		
		with torch.no_grad():
			fake_image = self.netG.forward(input_concat)

		return fake_image
	
	# helper loading function that can be used by subclasses
	def __load_network(self, network):

		save_path = os.path.join(self.opt.checkpoints_dir)

		network.load_state_dict(torch.load(save_path))

	def __encode_input(self, label_map, inst_map=None, real_image=None, feat_map=None, infer=False):             
		if (len(self.gpu_ids) > 0): 
			input_label = label_map.data.cuda() #GPU
		else: 
			input_label = label_map.data #CPU
			
		return input_label, inst_map, real_image, feat_map

	def __weights_init(self, m):
		classname = m.__class__.__name__
		if classname.find('Conv') != -1:
			m.weight.data.normal_(0.0, 0.02)
		elif classname.find('BatchNorm2d') != -1:
			m.weight.data.normal_(1.0, 0.02)
			m.bias.data.fill_(0)

	def __define_G(self, input_nc, output_nc, ngf, netG, n_downsample_global=3, n_blocks_global=9, n_local_enhancers=1, 
				 n_blocks_local=3, norm='instance', gpu_ids=[]):    
		norm_layer = self.__get_norm_layer(norm_type=norm)         
		netG = GlobalGenerator(input_nc, output_nc, ngf, n_downsample_global, n_blocks_global, norm_layer)
		
		if len(gpu_ids) > 0:
			netG.cuda(gpu_ids[0])
		netG.apply(self.__weights_init)
		return netG

	def __get_norm_layer(self, norm_type='instance'):
		norm_layer = functools.partial(torch.nn.InstanceNorm2d, affine=False)
		return norm_layer

##############################################################################
# Generator
##############################################################################
class GlobalGenerator(torch.nn.Module):
	def __init__(self, input_nc, output_nc, ngf=64, n_downsampling=3, n_blocks=9, norm_layer=torch.nn.BatchNorm2d, 
				 padding_type='reflect'):
		assert(n_blocks >= 0)
		super(GlobalGenerator, self).__init__()        
		activation = torch.nn.ReLU(True)        

		model = [torch.nn.ReflectionPad2d(3), torch.nn.Conv2d(input_nc, ngf, kernel_size=7, padding=0), norm_layer(ngf), activation]
		### downsample
		for i in range(n_downsampling):
			mult = 2**i
			model += [torch.nn.Conv2d(ngf * mult, ngf * mult * 2, kernel_size=3, stride=2, padding=1),
					  norm_layer(ngf * mult * 2), activation]

		### resnet blocks
		mult = 2**n_downsampling
		for i in range(n_blocks):
			model += [ResnetBlock(ngf * mult, padding_type=padding_type, activation=activation, norm_layer=norm_layer)]
		
		### upsample         
		for i in range(n_downsampling):
			mult = 2**(n_downsampling - i)
			model += [torch.nn.ConvTranspose2d(ngf * mult, int(ngf * mult / 2), kernel_size=3, stride=2, padding=1, output_padding=1),
					   norm_layer(int(ngf * mult / 2)), activation]
		model += [torch.nn.ReflectionPad2d(3), torch.nn.Conv2d(ngf, output_nc, kernel_size=7, padding=0), torch.nn.Tanh()]        
		self.model = torch.nn.Sequential(*model)
			
	def forward(self, input):
		return self.model(input)             
		
# Define a resnet block
class ResnetBlock(torch.nn.Module):
	def __init__(self, dim, padding_type, norm_layer, activation=torch.nn.ReLU(True), use_dropout=False):
		super(ResnetBlock, self).__init__()
		self.conv_block = self.__build_conv_block(dim, padding_type, norm_layer, activation, use_dropout)

	def __build_conv_block(self, dim, padding_type, norm_layer, activation, use_dropout):
		conv_block = []
		p = 0
		if padding_type == 'reflect':
			conv_block += [torch.nn.ReflectionPad2d(1)]
		elif padding_type == 'replicate':
			conv_block += [torch.nn.ReplicationPad2d(1)]
		elif padding_type == 'zero':
			p = 1
		else:
			raise NotImplementedError('padding [%s] is not implemented' % padding_type)

		conv_block += [torch.nn.Conv2d(dim, dim, kernel_size=3, padding=p),
					   norm_layer(dim),
					   activation]
		if use_dropout:
			conv_block += [torch.nn.Dropout(0.5)]

		p = 0
		if padding_type == 'reflect':
			conv_block += [torch.nn.ReflectionPad2d(1)]
		elif padding_type == 'replicate':
			conv_block += [torch.nn.ReplicationPad2d(1)]
		elif padding_type == 'zero':
			p = 1
		else:
			raise NotImplementedError('padding [%s] is not implemented' % padding_type)
		conv_block += [torch.nn.Conv2d(dim, dim, kernel_size=3, padding=p),
					   norm_layer(dim)]

		return torch.nn.Sequential(*conv_block)

	def forward(self, x):
		out = x + self.conv_block(x)
		return out

# Data utils:
def get_transform(opt, method=Image.BICUBIC, normalize=True):
	transform_list = []

	base = float(2 ** opt.n_downsample_global)
	if opt.netG == 'local':
		base *= (2 ** opt.n_local_enhancers)
	transform_list.append(transforms.Lambda(lambda img: __make_power_2(img, base, method)))

	transform_list += [transforms.ToTensor()]

	if normalize:
		transform_list += [transforms.Normalize((0.5, 0.5, 0.5),
												(0.5, 0.5, 0.5))]
	return transforms.Compose(transform_list)

def __make_power_2(img, base, method=Image.BICUBIC):
	ow, oh = img.size        
	h = int(round(oh / base) * base)
	w = int(round(ow / base) * base)
	if (h == oh) and (w == ow):
		return img
	return img.resize((w, h), method)

# Converts a Tensor into a Numpy array
# |imtype|: the desired type of the converted numpy array
def tensor2im(image_tensor, imtype=np.uint8, normalize=True):
	if isinstance(image_tensor, list):
		image_numpy = []
		for i in range(len(image_tensor)):
			image_numpy.append(tensor2im(image_tensor[i], imtype, normalize))
		return image_numpy
	image_numpy = image_tensor.cpu().float().numpy()
	if normalize:
		image_numpy = (np.transpose(image_numpy, (1, 2, 0)) + 1) / 2.0 * 255.0
	else:
		image_numpy = np.transpose(image_numpy, (1, 2, 0)) * 255.0      
	image_numpy = np.clip(image_numpy, 0, 255)
	if image_numpy.shape[2] == 1 or image_numpy.shape[2] > 3:        
		image_numpy = image_numpy[:,:,0]
	return image_numpy.astype(imtype)