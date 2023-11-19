#! /usr/bin/bash

docker run -t --rm --name test_createmmap -v /raid/keerthi/data:/data -v /home/hbp/code/image_computing_base:/code hbp1/hbpbase:1.1 python3 /code/create_mmap_script.py /data/JP2/B_37_FB3-SL_560-ST_NISL-SE_1678_lossless.jp2 /data/special/jp2cache
