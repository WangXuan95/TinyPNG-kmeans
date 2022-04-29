# -*- coding: utf-8 -*-
# Python3

import os
import sys
import warnings
import numpy as np
from PIL import Image
from sklearn.cluster import MiniBatchKMeans




if __name__ == '__main__':

    # parse command args
    try:
        INPUT_DIR, OUTPUT_DIR = sys.argv[1:3]
        QUANT = 256
        if len(sys.argv) > 3:
            QUANT = int(sys.argv[3])
    except:
        print('Usage: python %s <IN_DIR> <OUT_DIR> [<QUANT>]' % sys.argv[0])
        exit(-1)
    
    if QUANT < 2:
        QUANT = 2
    if QUANT > 256:
        QUANT = 256
    
    print('\ninput_directory = %s\noutput_directory = %s\nQUANT = %d\n' % (INPUT_DIR, OUTPUT_DIR, QUANT) )
    
    if os.path.isdir(OUTPUT_DIR):
        if input('warning: output_directory %s already exist! would you like to continue? (y|n)' % OUTPUT_DIR) != 'y':
            exit(-1)
    else:
        os.mkdir(OUTPUT_DIR)
    
    
    total_count, total_isize, total_osize = 0, 0, 0
    
    for fname in os.listdir(INPUT_DIR):
        
        ifname = INPUT_DIR  + os.path.sep + fname
        fname_suffix = fname.split('.')[-1]
        if len(fname_suffix) < len(fname):
            ofname = OUTPUT_DIR + os.path.sep + fname.replace(fname_suffix, 'png')
        else:
            ofname = OUTPUT_DIR + os.path.sep + fname + '.png'
        
        if os.path.isfile(ifname):
            
            try:
                isize = os.path.getsize(ifname)
                img = Image.open(ifname)
                with warnings.catch_warnings():
                    warnings.filterwarnings('ignore')
                    img = img.convert('RGB')
                img_map = np.asarray(img)
            except:
                print('%s skip' % fname)
                continue
            
            if isize > 1024:
                
                kmeans_n_clusters = min(QUANT, img.width * img.height)
                
                with warnings.catch_warnings():
                    warnings.filterwarnings('ignore')
                    kmeans_res = MiniBatchKMeans(n_clusters=kmeans_n_clusters, init='k-means++', max_iter=100, batch_size=32768, compute_labels=True, random_state=0).fit(img_map.reshape((-1,3)))
                
                palette = np.array(kmeans_res.cluster_centers_ + 0.5, dtype=np.uint8)
                
                img_palette_map = palette[kmeans_res.labels_].reshape(img_map.shape)
                
                img_palette = Image.fromarray(img_palette_map).convert('P', palette=Image.ADAPTIVE)
                
                img_palette.save(ofname, optimize=True)
                
                osize = os.path.getsize(ofname)
                
                if isize <= osize:
                    os.remove(ofname)
                    print('%s skip' % fname)
                else:
                    print('%s (%dx%d %s)   kmeans-iter=%d   %dB -> %dB   %.2f%% off!' % (
                        fname,
                        img.width,
                        img.height,
                        img.mode,
                        kmeans_res.n_iter_,
                        isize,
                        osize,
                        100.0*(1.0-osize/isize) ) )
                    total_count += 1
                    total_isize += isize
                    total_osize += osize
            
            else:
                print('%s skip' % fname)
        
    print('\n%d files compressed,   %dB -> %dB   %.2f%% off!' % (
        total_count,
        total_isize,
        total_osize,
        100.0*(1.0-total_osize/total_isize) ) )
            




    