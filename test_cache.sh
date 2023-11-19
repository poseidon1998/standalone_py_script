#! /usr/bin/bash

docker run -t --rm --name test_createcache -v /raid/keerthi/data:/data -v /home/hbp/code/image_computing_base:/code hbp1/hbpbase:1.1 python3 /code/create_cache_script.py 37 /store/nvmestorage/keerthi/data /store/repos1/iitlab/humanbrain/analytics/ 1
