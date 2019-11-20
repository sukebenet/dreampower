![](assets/dreampower.png)

[![Build Status](https://github.com/dreamnettech/dreampower/workflows/CI/CD/badge.svg)](https://github.com/dreamnettech/dreampower/actions)
[![GitHub All Releases](https://img.shields.io/github/downloads/dreamnettech/dreampower/total?logo=github&logoColor=white)](https://github.com/dreamnettech/dreampower/releases)

![GitHub](https://img.shields.io/github/license/dreamnettech/dreampower)
![GitHub top language](https://img.shields.io/github/languages/top/dreamnettech/dreampower)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/fcea261a567c47109419d0572160fecf)](https://www.codacy.com/app/kolessios/dreampower?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=dreamnettech/dreampower&amp;utm_campaign=Badge_Grade)
[![Maintainability](https://api.codeclimate.com/v1/badges/c8cd0a0f104820adc2ba/maintainability)](https://codeclimate.com/github/dreamnettech/dreampower/maintainability)

# DreamPower

DreamPower is a deep learning algorithm based on [DeepNude](https://github.com/stacklikemind/deepnude_official) with the ability to nudify photos of people.

DreamPower is a CLI application. If you have no experience in terminals you can use [DreamTime](https://time.dreamnet.tech), an easy way to use the power of DreamPower.

![](assets/preview.png)

> If you want to share or modify this software please do it for the same purpose as we do and always release the source code of your modifications. Read the [LICENSE](LICENSE) for more information.

## Better than DeepNude.

DreamPower is a fork of [deepnude_official](https://github.com/stacklikemind/deepnude_official) but with constant improvements from DreamNet developers and the world, we stand out for offering these features:

- GPU Processing (Transformation in ~10 seconds!)
- Multiple GPU support
- Multithreading
- Auto-resize, auto-rescale, etc
- Animated GIFs support
- Customization: size of boobs, pubic hair, etc.
- Constant updates!

## DreamNet

We are a community interested in developing decentralized applications free of censorship. Join our social networks or repositories:

- [Website](https://dreamnet.tech)
- [GitHub](https://github.com/dreamnettech)
- [NotABug](https://notabug.org/DreamNet)
- [GitGud](https://gitgud.io/dreamnet)

## Support

We work every day to offer new features and improvements to the program for free, support us financially to offer more constant and large updates!

[![patreon](https://img.shields.io/badge/become%20a%20patron-fb6c54?logo=patreon&logoColor=white&style=for-the-badge)](https://www.patreon.com/dreampower)

# 🎉 Releases

## Requirements

- 64 bits OS
- Windows 7 SP1/Windows 8/Windows 10 1803+
- Ubuntu 16.04+
- macOS Catalina 10.15+
- **8 GB** of RAM or more.

### GPU Processing

- NVIDIA GPU with minimum [3.5 CUDA compute capability.](https://developer.nvidia.com/cuda-gpus)
- [Latest NVIDIA drivers.](https://www.nvidia.com/Download/index.aspx)

> 👉 If you do not have an NVIDIA or compatible GPU you can use CPU processing.

## Download


[![GitHub All Releases](https://img.shields.io/github/downloads/dreamnettech/dreampower/total?logo=github&logoColor=white&style=for-the-badge&labelColor=181717&color=blue)](https://github.com/dreamnettech/dreampower/releases)
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fdreamnettech%2Fdreampower.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Fdreamnettech%2Fdreampower?ref=badge_shield)

## Installation

- Extract the file that contains the CLI, it can be anywhere you want it, this should generate a folder called `dreampower`
- Inside the folder called `dreampower` run the CLI executable `dreampower checkpoints download` to download the checkpoints.

> When you update DreamPower it will only be necessary to download the file that contains the `DreamPower`, you can reuse the checkpoints (unless we tell you otherwise)

## Using package manager

### Archlinux (AUR)

Available on the [Archlinux User Repository](https://aur.archlinux.org/) in two version:
* [dreampower](https://aur.archlinux.org/packages/dreampower) with CUDA Support
* [dreampower-cpu](https://aur.archlinux.org/packages/dreampower-cpu) with no CUDA Support

## Usage

In the command line terminal run:

```
dreampower run --help
```

This will print out help on the parameters the algorithm accepts.

> **The input image should be 512px * 512px in size** (parameters are provided to auto resize/scale your input).

---

# 💻 Development

## Requirements

- [CUDA 10.0](https://developer.nvidia.com/cuda-10.0-download-archive)
- [Python 3.5+](https://www.python.org/downloads/)

## Prerequisite

Before you can launch the main alogirthm script you'll need to install certain packages in your **Python3** environment.

We've added a setup script for the supported OSes in the 'scripts' folder that will do this for you.

The following OSes are supported:

- Windows
- MacOS
- Linux

## Launch the script

```
python3 main.py run --help
```

This will print out help on the parameters the algorithm accepts.

> **The input image should be 512px * 512px in size** (parameters are provided to auto resize / scale your input).

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

![Dress To Nude](assets/dress_to_nude.jpg?raw=true "Dress To Nude")

## Divide-et-impera problem:

![Dress To Mask](assets/dress_to_mask.jpg?raw=true "Dress To Mask")
![Mask To MaskDet](assets/mask_to_maskdet.jpg?raw=true "Mask To MaskDet")
![MaskDeto To Nude](assets/maskdet_to_nude.jpg?raw=true "MaskDeto To Nude")

This approach makes the construction of the sub-datasets accessible and feasible. Web scrapers can download thousands of images from the web, dressed and nude, and through photoshop you can apply the appropriate masks and details to build the dataset that solve a particular sub problem. Working on stylized and abstract graphic fields the construction of these datasets becomes a mere problem of hours working on photoshop to mask photos and apply geometric elements. Although it is possible to use some automations, the creation of these datasets still require great and repetitive manual effort.

## Computer Vision Optimization

To optimize the result, simple computer vision transformations are performed before each GAN phase, using OpenCV. The nature and meaning of these transformations are not very important, and have been discovered after numerous trial and error attempts.

Considering these additional transformations, the phases of the algorithm are the following:

- **dress -> correct** [OPENCV]
- **correct -> mask** [GAN]
- **mask -> maskref** [OPENCV]
- **maskref -> maskdet** [GAN]
- **maskdet -> maskfin** [OPENCV]
- **maskfin -> nude** [GAN]

![Transformations](assets/transformation.jpg?raw=true "Transformations")


## License
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fdreamnettech%2Fdreampower.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Fdreamnettech%2Fdreampower?ref=badge_large)