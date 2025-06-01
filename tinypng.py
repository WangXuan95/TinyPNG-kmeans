# -*- coding: utf-8 -*-
# Python3

import os
import sys
import warnings
import numpy as np
from PIL import Image


IMCVT_EXECUTABLE_FILE_NAME_LINUX     = 'ImCvt'
IMCVT_EXECUTABLE_FILE_NAME_WINDOWS   = 'ImCvt.exe'
OPTIPNG_EXECUTABLE_FILE_NAME_LINUX   = 'optipng'
OPTIPNG_EXECUTABLE_FILE_NAME_WINDOWS = 'optipng.exe'
    

def inputImageAsRGBandSaveAsPPM (src_fname, dst_fname) :
    img = Image.open(src_fname)
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore')
        if img.mode in ['RGBA'] :
            arr_rgba = np.asarray(img)
            arr_rgb   = arr_rgba[:, :, :3].astype(np.float32)
            arr_alpha = arr_rgba[:, :,  3].astype(np.float32) / 255.0
            arr_rgb[:, :, 0] *= arr_alpha
            arr_rgb[:, :, 1] *= arr_alpha
            arr_rgb[:, :, 2] *= arr_alpha
            arr_rgb[:, :, 0] += (1.0 - arr_alpha) * 255.0
            arr_rgb[:, :, 1] += (1.0 - arr_alpha) * 255.0
            arr_rgb[:, :, 2] += (1.0 - arr_alpha) * 255.0
            arr_rgb = arr_rgb.clip(0.0, 255.9).astype(np.uint8)
        else :
            img_rgb = img.convert('RGB')
            arr_rgb = np.asarray(img_rgb)
    img.close()
    Image.fromarray(arr_rgb).save(dst_fname)


if __name__ == '__main__':
    
    # judge OS --------------------------------------------------------
    if   sys.platform.lower().startswith('win'):
        print('Windows')
        imcvt_executable_fname   =   IMCVT_EXECUTABLE_FILE_NAME_WINDOWS
        optipng_executable_fname = OPTIPNG_EXECUTABLE_FILE_NAME_WINDOWS
    elif sys.platform.lower().startswith('linux'):
        print('Linux')
        imcvt_executable_fname   =   IMCVT_EXECUTABLE_FILE_NAME_LINUX
        optipng_executable_fname = OPTIPNG_EXECUTABLE_FILE_NAME_LINUX
    else:
        print('current OS %s not support' % sys.platform)
        exit(1)
    
    # get the path executable files --------------------------------------------------------
    work_dir, _  = os.path.split(sys.argv[0])
    if work_dir == '' :
        imcvt_path   = os.path.join('.'     , imcvt_executable_fname)
        optipng_path = os.path.join(work_dir, optipng_executable_fname)
    else :
        imcvt_path   = os.path.join('.'     , imcvt_executable_fname)
        optipng_path = os.path.join(work_dir, optipng_executable_fname)
    
    # parse command args --------------------------------------------------------
    try :
        src_dir, dst_dir = sys.argv[1:3]
        if len(sys.argv) > 3 :
            quant = int(sys.argv[3])
        else :
            quant = 100
        quant = max(min(quant, 256), 2)
    except:
        print('Usage: python  %s  <source_directory>  <destination_directory>  [<quant(2~256)>]' % sys.argv[0])
        exit(1)
    print('source_directory      = %s' % src_dir )
    print('destination_directory = %s' % dst_dir )
    print('quant                 = %d' % quant   )
    print()
    
    # If dst_dir not exist, create it. If already exist, ask user whether to continue --------------------------------------------------------
    if os.path.isdir(dst_dir) :
        if input('warning: destination_directory %s already exist! continue? (y|n)' % dst_dir) != 'y':
            exit(1)
    else:
        os.makedirs(dst_dir)
    
    # for all files in src_dir, try to compress it, and save to dst_dir --------------------------------------------------------
    for fname in os.listdir(src_dir) :
        fname_prefix, _ = os.path.splitext(fname)
        src_fname = os.path.join(src_dir, fname)
        tmp_fname = os.path.join(dst_dir, (fname_prefix+'.ppm'))
        dst_fname = os.path.join(dst_dir, (fname_prefix+'.png'))
        
        try :
            inputImageAsRGBandSaveAsPPM(src_fname, tmp_fname)
        except :
            print('%s skip' % fname)
            continue
        
        command = f'{imcvt_path} -{quant} -f {tmp_fname} -o {dst_fname}'
        print(command)
        os.system(command)
        os.remove(tmp_fname)
        
        command = f'{optipng_path} -o5 {dst_fname}'
        print(command)
        os.system(command)

    