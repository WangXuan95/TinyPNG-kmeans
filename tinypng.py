# -*- coding: utf-8 -*-
# Python3

import os
import sys
import warnings
#import subprocess as sp
import numpy as np
from PIL import Image
from sklearn.cluster import MiniBatchKMeans



OPTIPNG_EXECUTABLE_FILE_NAME_LINUX   = 'optipng'
OPTIPNG_EXECUTABLE_FILE_NAME_WINDOWS = 'optipng.exe'
    


def loadImageFileAsRGBArray(fname) :
    img = Image.open(fname)
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
    return arr_rgb




def saveImageAsPalettePNGusingKMeans(quant, img_array2d, fname) :
    h, w, _ = img_array2d.shape
    
    kmeans_n_clusters = min(quant, w*h)
    
    img_array1d = img_array2d.reshape((-1,3))
    
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore')
        kmeans_res = MiniBatchKMeans(n_clusters=kmeans_n_clusters, init='k-means++', max_iter=100, batch_size=32768, compute_labels=True, random_state=0).fit(img_array1d)
    
    palette_array = (kmeans_res.cluster_centers_ + 0.5).clip(0.0, 255.9).astype(np.uint8)
    
    img_palette_array1d = palette_array[kmeans_res.labels_]
    
    img_palette_array2d = img_palette_array1d.reshape(img_array2d.shape)
    
    Image.fromarray(img_palette_array2d).convert('P', palette=Image.ADAPTIVE).save(fname, optimize=True)
    
    return kmeans_res.n_iter_




def callOptiPNG (optipng_path, dst_fname) :
    #COMMANDS = [ optipng_path, '-o7', dst_fname ]
    #p = sp.Popen(COMMANDS, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
    #p.wait()
    command = optipng_path + ' -o7 ' + dst_fname
    print(command)
    os.system(command)




def copy_file (src_path, dst_path) :
    if  os.path.isfile(src_path)  and  not os.path.exists(dst_path) :
        with open(src_path, 'rb') as src_fp :
            with open(dst_path, 'wb') as dst_fp :
                dst_fp.write(src_fp.read())




if __name__ == '__main__':
    
    # judge OS --------------------------------------------------------
    if   sys.platform.lower().startswith('win'):
        print('Windows')
        optipng_executable_fname = OPTIPNG_EXECUTABLE_FILE_NAME_WINDOWS
    elif sys.platform.lower().startswith('linux'):
        print('Linux')
        optipng_executable_fname = OPTIPNG_EXECUTABLE_FILE_NAME_LINUX
    else:
        print('current OS %s not support' % sys.platform)
        exit(-1)
    
    
    # get the path of optipng --------------------------------------------------------
    work_path = sys.argv[0]
    work_dir, _  = os.path.split(work_path)
    
    if work_dir == '' :
        optipng_path = '.'      + os.path.sep + optipng_executable_fname
    else :
        optipng_path = work_dir + os.path.sep + optipng_executable_fname
    
    
    # parse command args --------------------------------------------------------
    try :
        src_dir = sys.argv[1]
        dst_dir = sys.argv[2]
        if len(sys.argv) > 3 :
            quant = int(sys.argv[3])
        else :
            quant = 256
    except:
        print('Usage: python  %s  <source_directory>  <destination_directory>  [<quant(2~256)>]' % sys.argv[0])
        exit(-1)
    
    if quant < 2:
        quant = 2
    if quant > 256:
        quant = 256
    
    
    # print info --------------------------------------------------------
    print('source_directory      = %s' % src_dir )
    print('destination_directory = %s' % dst_dir )
    print('quant                 = %d' % quant   )
    print()
    
    
    # If dst_dir not exist, create it. If already exist, ask user whether to continue --------------------------------------------------------
    if os.path.isdir(dst_dir) :
        if input('warning: destination_directory %s already exist! continue? (y|n)' % dst_dir) != 'y':
            exit(-1)
    else:
        os.mkdir(dst_dir)
    
    
    # statistics variables -----------------------------
    total_count    = 0
    total_src_size = 0
    total_dst_size = 0
    
    
    # for all files in src_dir, try to compress it, and save to dst_dir --------------------------------------------------------
    for fname in os.listdir(src_dir) :
        
        fname_prefix, _ = os.path.splitext(fname)
        dst_fname = dst_dir + os.path.sep + fname_prefix + '.png'
        src_fname = src_dir + os.path.sep + fname
        
        # try to open file as image -----------------------------
        try :
            src_size = os.path.getsize(src_fname)
            img_array2d = loadImageFileAsRGBArray(src_fname)
        except :
            print('%s skip' % fname)
            continue
        
        # get image height and width -----------------------------
        h, w, _ = img_array2d.shape
        
        # compress stage1 : use KMeans to quantize image and save as palette-PNG file (lossy) -----------------------------
        print('compressing stage1 (KMeans Quantize) ...')
        n_iter = saveImageAsPalettePNGusingKMeans(quant, img_array2d, dst_fname)
        
        # compress stage2 : use optipng to do an optimization of deflate coding (lossless) -----------------------------
        print('compressing stage2 (OptiPNG) ...')
        callOptiPNG (optipng_path, dst_fname)
        #command = '%s -o7 "%s"' % (optipng_path, dst_fname)
        #os.system(command)
        
        # get compressed PNG size -----------------------------
        dst_size = os.path.getsize(dst_fname)
        
        # decide whether to use the compressed file, or just copy the original file
        if src_size <= dst_size :                               # not even better than original
            if src_dir != dst_dir :
                os.remove(dst_fname)                            # delete it
            dst_fname = dst_dir + os.path.sep + fname           # construct copy file name
            copy_file(src_fname, dst_fname)                     # just copy file
            dst_size = src_size
            print('%s (%dx%d)   just copy' % (fname, w, h) )
        else :
            print('%s (%dx%d)   kmeans-iter=%d   %dB -> %dB   %.2f%% off!' % (fname, w, h, n_iter, src_size, dst_size, 100.0*(1.0-dst_size/src_size) ) )
        
        
        total_count    += 1
        total_src_size += src_size
        total_dst_size += dst_size
    
    
    print()
    if total_count > 0 :
        print('%d files compressed    %dB -> %dB   %.2f%% off!' % (total_count, total_src_size, total_dst_size, 100.0*(1.0-total_dst_size/total_src_size) ) )
    else :
        print('no input file')





    