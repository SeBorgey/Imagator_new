"""\file inference_esrgan.py

    Файл взят из отсюда https://github.com/xinntao/BasicSR
    и минимально переделан, чтобы интегрировать его в проект.
"""
import argparse
import cv2
import glob
import numpy as np
import os
import torch

from basicsr.archs.rrdbnet_arch import RRDBNet


def run_super_res(message):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--model_path',
        type=str,
        default=  # noqa: E251
        'ESRGAN/ESRGAN_PSNR_SRx4_DF2K_official-150ff491.pth'  # noqa: E501
    )
    parser.add_argument('--folder', type=str, default='images', help='input test image folder')
    args = parser.parse_args()

    device = torch.device('cuda')
    # set up model
    model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32)
    model.load_state_dict(torch.load(args.model_path)['params'], strict=True)
    model.eval()
    model = model.to(device)
    for idx, path in enumerate(sorted(glob.glob(os.path.join(args.folder, '*')))):
        img_name = os.path.splitext(os.path.basename(path))[0]
        print('Testing', idx, img_name)
        # read image
        img = cv2.imread(path, cv2.IMREAD_COLOR).astype(np.float32) / 255.
        img = torch.from_numpy(np.transpose(img[:, :, [2, 1, 0]], (2, 0, 1))).float()
        img = img.unsqueeze(0).to(device)
        # inference
        with torch.no_grad():
            output = model(img)
        # save image
        output = output.data.squeeze().float().cpu().clamp_(0, 1).numpy()
        output = np.transpose(output[[2, 1, 0], :, :], (1, 2, 0))
        output = (output * 255.0).round().astype(np.uint8)
        cv2.imwrite(f'images/{message.from_user.id}+_super_result.png', output)


if __name__ == '__main__':
    run_super_res()
