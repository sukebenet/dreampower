# DreamPower

DreamPower allows you to use the power of your CPU or GPU to apply to photos a deep learning algorithm capable of predicting what a person's body would look like without clothes.

DreamPower is a CLI application, if you don't have command line knowledge please use [DreamTime](https://time.dreamnet.tech) for a friendly user interface.

# Differences with DeepNude

DreamPower is a [fork](https://en.wikipedia.org/wiki/Fork_(software_development)) of [deepnude_official](https://github.com/stacklikemind/deepnude_official) and therefore it relies on the source code of the original program to process the photos.

DreamPower stands out from DeepNude for having the following features:

- Processing with GPU (Transformation in seconds!)
- Multiple GPU support
- Support to transform animated GIFs
- Customization: size of boobs, pubic hair, etc.
- Constant updates!

> Most of these improvements are possible thanks to the community.

# Community

Join the social networks of DreamNet, the community interested in developing this technology in a more serious and real way. You can also join just to talk about the project, make friends or get help:

- [Discord](http://bit.ly/32nnbdb)

# Support

Developing DreamNet applications is time consuming! Help us accelerate development and offer better updates!

[![ko-fi](https://www.ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/R6R2ZSG3)

[![patreon](https://c5.patreon.com/external/logo/become_a_patron_button.png)](https://www.patreon.com/deepmanyy)

# License

See **LICENSE.md** for more details.

---

# Binaries

## Download

Download DreamPower is very easy! 2 files and you are ready. _(Get ready to download ~3GB)_

- [CLI](https://bit.ly/2KdqlYH): The command line interface (CLI), here you will find everything you need, just download the .zip file that fits your operating system.
- [Checkpoints](http://bit.ly/2JBP88o): This is the information that the transformation algorithm **requires**, if you do not have this file the application will not work. You only need to download it once, if you update DreamPower use this same file for checkpoints. (unless we tell you otherwise)

## Download Mirrors

- [CLI (MEGA)](https://bit.ly/2GD6aST)
- [CLI (MediaFire)](https://bit.ly/2LNjAQk)
- [Checkpoints (MEGA)](http://bit.ly/30GiSbh)
- [Checkpoints (MediaFire)](http://bit.ly/2Y0V6sO)

## Installation

- Create a folder on your computer, it can be anywhere you want it, call it `DreamPower` and inside it place the 2 zip files you have downloaded.
- Extract the file that contains the CLI, this should generate a folder called `cli`
- Extract the other file `checkpoints.zip` and move the extracted folder `checkpoints` inside `cli`.
- Ready! Now you can use the command line interface run the `cli/cli.exe` file from a console.

> When you update DreamPower it will only be necessary to download the file that contains the `CLI`, you can reuse the checkpoints (unless we tell you otherwise)


## GPU Processing Requirements

> If you do not have an NVIDIA or compatible graphics card you can use CPU processing.

- NVIDIA Graphics card with CUDA compatibility
- [Latest NVIDIA drivers](https://www.nvidia.com/Download/index.aspx)

---

# Development > Area only for developers!

> **If you are a developer:** Consider making a fork of the project and make PR of any improvement you can do, also join our server in [Discord](https://discord.gg/RjBSaND) where we have channels exclusively for development.

# Requirements

- [Python 3.6](https://www.python.org/downloads/release/python-368/)

# Prerequisite

Before you can launch the main alogirthm script you'll need to install certain packages in your **Python3** environment.

We've added a setup script for the supported OSes in the 'scripts' folder that will do this for you.

The following OSes are supported:
- Windows
- MacOS
- Ubuntu16
- Ubuntu
- Linux


# Launch the script

```
 python3 main.py --help
```

This will print out help on the parameters the algorithm accepts.

**The input image should be 512px * 512px in size.**

---

# How does DreamPower work?

DreamPower uses an interesting method to solve a typical AI problem, so it could be useful for researchers and developers working in other fields such as *fashion*, *cinema* and *visual effects*.

The algorithm uses a slightly modified version of the [pix2pixHD](https://github.com/NVIDIA/pix2pixHD) GAN architecture. If you are interested in the details of the network you can study this amazing project provided by NVIDIA.

A GAN network can be trained using both **paired** and **unpaired** dataset. Paired datasets get better results and are the only choice if you want to get photorealistic results, but there are cases in which these datasets do not exist and they are impossible to create. A database in which a person appears both naked and dressed, in the same position, is extremely difficult to achieve, if not impossible.

We overcome the problem using a *divide-et-impera* approach. Instead of relying on a single network, we divided the problem into 3 simpler sub-problems:

- 1. Generation of a mask that selects clothes
- 2. Generation of a abstract representation of anatomical attributes
- 3. Generation of the fake nude photo

## Original problem:

![Dress To Nude](readmeimgs/dress_to_nude.jpg?raw=true "Dress To Nude")

## Divide-et-impera problem:

![Dress To Mask](readmeimgs/dress_to_mask.jpg?raw=true "Dress To Mask")
![Mask To MaskDet](readmeimgs/mask_to_maskdet.jpg?raw=true "Mask To MaskDet")
![MaskDeto To Nude](readmeimgs/maskdet_to_nude.jpg?raw=true "MaskDeto To Nude")

This approach makes the construction of the sub-datasets accessible and feasible. Web scrapers can download thousands of images from the web, dressed and nude, and through photoshop you can apply the appropriate masks and details to build the dataset that solve a particular sub problem. Working on stylized and abstract graphic fields the construction of these datasets becomes a mere problem of hours working on photoshop to mask photos and apply geometric elements. Although it is possible to use some automations, the creation of these datasets still require great and repetitive manual effort.

# Computer Vision Optimization

To optimize the result, simple computer vision transformations are performed before each GAN phase, using OpenCV. The nature and meaning of these transformations are not very important, and have been discovered after numerous trial and error attempts.

Considering these additional transformations, the phases of the algorithm are the following:

- **dress -> correct** [OPENCV]
- **correct -> mask** [GAN]
- **mask -> maskref** [OPENCV]
- **maskref -> maskdet** [GAN]
- **maskdet -> maskfin** [OPENCV]
- **maskfin -> nude** [GAN]


![Transformations](readmeimgs/transformation.jpg?raw=true "Transformations")
