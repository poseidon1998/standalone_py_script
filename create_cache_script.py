import glob
from tqdm import tqdm
import os
from utils.multiproc import get_multiproc_plan
from utils.general import TicToc
from utils.args import parseargs
from functools import partial
from concurrent.futures import ProcessPoolExecutor
from cachedimage import SectionImage8U

def get_sectionimage(biosampleid, imgpath, rigidrotation=0,mpp=16,adjustgamma=False):

    basedir = os.getenv('SA_PNGBASE','/data')

    pngdir = basedir+'/special/pngcache%d' % biosampleid
    tmpdir = basedir+'/special/tmpdir'
    os.makedirs(pngdir,exist_ok=True)
    os.makedirs(tmpdir,exist_ok=True)

    img = SectionImage8U(imgpath, mpp=mpp, removeblack=False, gray=False, invert=False, 
        adjustgamma=adjustgamma,usecache=True,pngdir=pngdir,tmpdir=tmpdir)

    if int(rigidrotation) == 270:
        img._rotate180()
        img._rotate90()
    
    elif int(rigidrotation) == 180:
        img._rotate180()

    elif int(rigidrotation) == 90:
        img._rotate90()

    sz = int(4000*16/mpp) # 16mpp => 4000pix for fetal
    img._pad((sz,sz),bordercolor=None)

    return img



def make_cache(biosampleid, dataroot, multiproc=True):
    
    workerfunc = partial(get_sectionimage,biosampleid)

    for modality in ('NISL','HEOS'):
        files = glob.glob(f'{dataroot}/{biosampleid}/{modality}/*_compressed.jp2')
        
        if multiproc:
            plan = get_multiproc_plan(len(files),minwork=10)
            print(plan)
            with TicToc(f'cache creation time({modality})') as tm:
            
                with ProcessPoolExecutor(max_workers=plan.nworkers) as executor:
                    for _ in executor.map(workerfunc,files,chunksize=plan.rounds):
                        pass

            print(tm)
        else:
            for jp2filename in tqdm(files):
                workerfunc(jp2filename)
                #break


if __name__=="__main__":
    args = parseargs({
        1:('biosampleid',int,142),
        2:('pngbase',str,'/data'),
        #3:('dataroot',str,'/store/repos1/iitlab/humanbrain/analytics'),
        3:('dataroot',str,'/analyticsdata'),
        4:('multiproc',int,1)
    },named=True)

    print(args)

    os.environ['SA_PNGBASE'] = args.pngbase

    make_cache(args.biosampleid,args.dataroot,args.multiproc)
