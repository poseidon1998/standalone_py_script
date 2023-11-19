from concurrent.futures import ProcessPoolExecutor

from datetime import datetime
import pickle
import os
import numpy as np
from utils.multiproc import get_multiproc_plan
from tiling import Accessor, to_slice
from utils.general import TicToc

def workerfunc(accessor,tilenum):
     arr, rgn, url = accessor[tilenum] # for __getitem__
     return arr,rgn, url, tilenum, os.getpid()

def get_mmap_name(imgpath):
    loc,bn = os.path.split(imgpath)
    namepart = ".".join(bn.split('.')[:-1])
    mmapfilename = namepart+'.dat'
    infoname = mmapfilename.replace('.dat','_info.pkl')
    return mmapfilename, infoname

def create_mmap(accessor,mmapdir='/data/special/mmapcache',concurrent=False):
    
    mmapfilename, infoname = get_mmap_name(accessor.imgpath)

    assert not os.path.exists(infoname)

    info = {'dtype':'uint8', 'shape':accessor.imageshape,'mmname':mmapfilename,'fname':accessor.imgpath}
        
    pickle.dump(info,open(mmapdir+'/'+infoname,'wb'))
    handle = np.memmap(mmapdir+'/'+mmapfilename,dtype='uint8',mode='w+',shape=accessor.imageshape )
    
    if not concurrent:
        with TicToc('load time') as loadtime:
            handle[:]=accessor._handle[:]
        with TicToc('flush time') as flushtime:   
            handle.flush()
        

    else:
        plan = get_multiproc_plan(accessor.ntiles,minwork=10)
        print(plan)
        
        # workerfunc2 = partial(workerfunc,self)
        # data,ext,url,tilenum,pid=workerfunc(accessor,accessor.ntiles-1)
        with TicToc('load time') as loadtime:

            pid_tiles = {}
            with ProcessPoolExecutor(max_workers=plan.nworkers) as executor:
                for data,extent,url,tilenum,pid in executor.map(workerfunc,accessor,range(plan.worksize),chunksize=plan.rounds):
                # for ii in tqdm(range(plan.worksize)):
                    # data,extent,_ = workerfunc2(ii)
                    if extent is not None:
                        rsl,csl = to_slice(extent)
                        handle[rsl,csl,:]=data
                    if pid not in pid_tiles:
                        pid_tiles[pid]=[]
                    pid_tiles[pid].append(tilenum)

        # print(loadtime)
        with TicToc('flush time') as flushtime:
            handle.flush()
    
        # print(flushtime)
        for pid,tiles in pid_tiles.items():
            print(pid,len(tiles))
        
    return loadtime,flushtime

