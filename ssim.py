# -*- coding: utf-8 -*-
# Python3

import os
import sys
import warnings
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as SSIM




if __name__ == '__main__':

    # parse command args
    try:
        DIR1, FMT1, DIR2, FMT2 = sys.argv[1:5]
    except:
        print('Usage: python %s <DIR1> <FMT1> <DIR2> <FMT2>' % sys.argv[0])
        exit(-1)
    
    total_count, total_sz1, total_sz2, total_pixel, total_ssim = 0, 0, 0, 0, 0.0
    
    for fname in os.listdir(DIR1):
        if fname.endswith(FMT1):
            fname1 = DIR1 + os.path.sep + fname
            fname2 = DIR2 + os.path.sep + fname.replace(FMT1, FMT2)
            if os.path.isfile(fname1) and os.path.isfile(fname2):
                try:
                    sz1 = os.path.getsize(fname1)
                    sz2 = os.path.getsize(fname2)
                    with warnings.catch_warnings():
                        warnings.filterwarnings('ignore')
                        img1 = Image.open(fname1).convert('RGB')
                        img2 = Image.open(fname2).convert('RGB')
                    img1_map = np.array(np.asarray(img1), dtype=np.float64)
                    img2_map = np.array(np.asarray(img2), dtype=np.float64)
                    assert img1_map.shape == img2_map.shape
                except:
                    print('%s open failed!' % fname)
                    continue
                
                if img1_map.shape != img2_map.shape:
                    print('%s and %s size mismatch!' % (fname1, fname2) )
                    
                else:
                    ssim_r = SSIM(img1_map[:,:,0], img2_map[:,:,0], data_range=256.0)
                    ssim_g = SSIM(img1_map[:,:,1], img2_map[:,:,1], data_range=256.0)
                    ssim_b = SSIM(img1_map[:,:,2], img2_map[:,:,2], data_range=256.0)
                    
                    ssim = (ssim_r + ssim_g + ssim_b) / 3.0
                    
                    print('%s (%dB)  %s (%dB)  ratio=%.2f  ssim=%.5f' % (fname1, sz1, fname2, sz2, (sz1+1)/(sz2+1), ssim))
                    
                    total_count += 1
                    total_sz1 += sz1
                    total_sz2 += sz2
                    total_pixel += img1.width * img1.height
                    total_ssim += ssim * img1.width * img1.height
    
    print('\ntotal %d images: %s (%dB)  %s (%dB)  ratio=%.2f  ssim=%.5f\n' % (total_count, DIR1, total_sz1, DIR2, total_sz2, (total_sz1+1)/(total_sz2+1), (total_ssim+0.1)/(total_pixel+0.1)))


