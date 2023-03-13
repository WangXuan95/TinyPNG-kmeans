# -*- coding: utf-8 -*-
# Python3

import os
import sys
import warnings
import numpy as np
from PIL import Image
from sklearn.cluster import MiniBatchKMeans



OPTIPNG_EXECUTABLE_FILE_PATH = 'optipng.exe'




def loadImageFileAsRGBArray(fname) :
    img = Image.open(fname)
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore')
        img_rgb = img.convert('RGB')
    img.close()
    return np.asarray(img_rgb)




def saveImageAsPalettePNGusingKMeans(QUANT, img_array2d, fname) :
    h, w, _ = img_array2d.shape
    
    kmeans_n_clusters = min(QUANT, w*h)
    
    img_array1d = img_array2d.reshape((-1,3))
    
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore')
        kmeans_res = MiniBatchKMeans(n_clusters=kmeans_n_clusters, init='k-means++', max_iter=100, batch_size=32768, compute_labels=True, random_state=0).fit(img_array1d)
    
    palette_array = np.array(kmeans_res.cluster_centers_ + 0.5, dtype=np.uint8)
    
    img_palette_array1d = palette_array[kmeans_res.labels_]
    
    img_palette_array2d = img_palette_array1d.reshape(img_array2d.shape)
    
    Image.fromarray(img_palette_array2d).convert('P', palette=Image.ADAPTIVE).save(fname, optimize=True)
    
    return kmeans_res.n_iter_






if __name__ == '__main__':
    
    OPTIPNG_EXECUTABLE_FILE_PATH = os.path.split(sys.argv[0])[0] + os.path.sep + OPTIPNG_EXECUTABLE_FILE_PATH

    # parse command args
    try:
        SRC_DIR, DST_DIR = sys.argv[1:3]
        QUANT = 256
        if len(sys.argv) > 3:
            QUANT = int(sys.argv[3])
    except:
        print('Usage: python  %s  <source_directory>  <destination_directory>  [<QUANT(2~256)>]' % sys.argv[0])
        exit(-1)
    
    if QUANT < 2:
        QUANT = 2
    if QUANT > 256:
        QUANT = 256
    
    print('source_directory      = %s' % SRC_DIR )
    print('destination_directory = %s' % DST_DIR )
    print('QUANT                 = %d' % QUANT   )
    print()
    
    
    if os.path.isdir(DST_DIR):
        if input('warning: destination_directory %s already exist! continue? (y|n)' % DST_DIR) != 'y':
            exit(-1)
    else:
        os.mkdir(DST_DIR)
    
    
    total_count, total_src_size, total_dst_size = 0, 0, 0              # statistics
    
    
    for fname in os.listdir(SRC_DIR):
        
        fname_prefix = os.path.splitext(fname)[0]
        dst_fname = DST_DIR + os.path.sep + fname_prefix + '.png'
        src_fname = SRC_DIR + os.path.sep + fname
        
        try:
            src_size = os.path.getsize(src_fname)
            img_array2d = loadImageFileAsRGBArray(src_fname)
        except:
            print('%s skip' % fname)
            continue
        
        h, w, _ = img_array2d.shape
        
        
        # stage1 : use KMeans to quantize image and save as palette-PNG file (lossy)
        n_iter = saveImageAsPalettePNGusingKMeans(QUANT, img_array2d, dst_fname)
        
        
        # stage2 : use optipng to do an optimization of deflate coding (lossless)
        command = '%s -o7 "%s"' % (OPTIPNG_EXECUTABLE_FILE_PATH, dst_fname)
        os.system(command)
        
        
        dst_size = os.path.getsize(dst_fname)
        
        if src_size <= dst_size :                               # not better than original
            os.remove(dst_fname)
            dst_fname = DST_DIR + os.path.sep + fname
            
            if SRC_DIR != DST_DIR :                             # just copy file
                with open(src_fname, 'rb') as src_fp :
                    with open(dst_fname, 'wb') as dst_fp :
                        dst_fp.write(src_fp.read())
            
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





    