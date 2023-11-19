from utils.multiproc import get_multiproc_plan
from utils.api import APIutils
from concurrent.futures import ProcessPoolExecutor
import os
from iipimage import IIPWSIProxy,  corners_to_poly, poly_to_box
from tiling import Accessor
from matplotlib import pyplot as plt


def workerfortest(tilenum):
    print('.',end="",flush=True)
    return tilenum, os.getpid()

def test_plan():
    print('testing procplan')
    plan = get_multiproc_plan(400,minwork=10)
    print(plan)
    pid_tiles = {}
    print('starting map')
    with ProcessPoolExecutor(max_workers=plan.nworkers) as executor:
        for tilenum,pid in executor.map(workerfortest,range(plan.worksize),chunksize=plan.rounds):
        
            if pid not in pid_tiles:
                pid_tiles[pid]=[]
            pid_tiles[pid].append(tilenum)    

    print('map done')    
    for pid,tiles in pid_tiles.items():
        print(pid,len(tiles))


def test_iipimage():
    obj = APIutils()
    imglist = obj.get_imglist_api(222)
    jp2path = imglist['NISL'][1474]['jp2Path']
    print(jp2path)
    imgproxy = IIPWSIProxy(jp2path)
    print(imgproxy.shape())
    # tn = imgproxy.getthumbnail()
    tn = imgproxy.get_reduced_iiif(6)
    
    coords_xy = [[20000,20000],[20512,20000],[20512,20512],[20000,20512]]
    til=imgproxy.get_tile(poly_to_box(corners_to_poly(coords_xy)))

    plt.imshow(tn)
    plt.show()

def test_accessor():
    jp2path = 'C:/Users/keerthi/Documents/work/htic/hbp/data/special/jp2cache/B_37_FB3-SL_173-ST_NISL-SE_517_lossless.dat'
    tilenum = 18728
    obj = Accessor(jp2path,shp=(512,512),padding=0)
    arr,rgn,url = obj[tilenum]
    print(url)
    plt.imshow(arr)
    plt.show()

if __name__=="__main__":
    # test_plan()
    test_iipimage()
    # test_accessor()
