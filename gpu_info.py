import torch
import json


def get_info():
    has_cuda = torch.cuda.is_available()
    devices = []

    if has_cuda:
        count = torch.cuda.device_count()
        for i in range(count):
            devices.append(torch.cuda.get_device_name(i))

    return {
        "has_cuda": has_cuda,
        "devices": devices,
    }


def main(args):
    info = get_info()
    if args.json:
        data = json.dumps(info)
        print(data)
    else:
        print("Has Cuda: {}".format(info["has_cuda"]))
        for (i, device) in enumerate(info["devices"]):
            print("GPU {}: {}".format(i, device))
