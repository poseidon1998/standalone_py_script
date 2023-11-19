from tiling import Accessor
from jp2_converter import create_mmap, get_mmap_name
import sys
import os
import subprocess
from utils.general import TicToc

def main(jp2path, mmapdir, use_glymur=False,use_kdu=True):

    mmapfilename, infoname = get_mmap_name(jp2path)
    if not os.path.exists(mmapdir+'/'+infoname):
        if use_glymur:
            accessor = Accessor(jp2path)
            loadtime,flushtime = create_mmap(accessor,mmapdir,concurrent=True)    

        elif use_kdu:
            with TicToc('expand time') as expandtime:
                basenm = os.path.basename(jp2path)
                tmpoutname = mmapdir+'/'+basenm[:-4]+'.tif'
                print(f'starting kdu_expand {basenm}')
                ret = subprocess.call(f'/app/bin/kdu_expand -num_threads 64 -i {jp2path} -o {tmpoutname} -quiet', shell=True)
                if ret!=0:
                    raise RuntimeError("kdu_expand failed")
                
            print(expandtime)

            
            accessor = Accessor(tmpoutname)
            print(accessor)
            accessor.imgpath = jp2path # to set nameprefix of _info.pkl
            loadtime,flushtime =  create_mmap(accessor, mmapdir, concurrent=False)

            print( loadtime)
            print(flushtime)

            os.unlink(tmpoutname)
        


if __name__=="__main__":

    jp2path = sys.argv[1].strip()
    mmapdir = sys.argv[2].strip()
    main(jp2path,mmapdir)
    
