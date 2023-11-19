from skimage.io import imread
from collections import namedtuple


try:
    import glymur
    glymur.set_option('lib.num_threads',48)
    glymur.set_option('print.codestream',False)
    glymur.set_option('print.xml',False)
except:
    print('glymur not setup correctly')

import pickle

import numpy as np
import os

Point = namedtuple('Point','x,y')
Extent = namedtuple('Extent','point1,point2')

def to_slice(ext,step=1):
    """can directly index as arr[to_slice(ext)] - equiv to 
        arr[ext.point1.y:ext.point2.y,ext.point1.x:ext.point2.x,:]"""
    rsl = slice(int(ext.point1.y),int(ext.point2.y),step)
    csl = slice(int(ext.point1.x),int(ext.point2.x),step)
    return rsl,csl 

        

class Accessor:
    def __init__(self,imgpath,shp=(4096,4096),padding=0):
        # print(jp2path)
        # print(os.listdir(os.path.dirname(jp2path)))
        
        self.imgpath = imgpath
        
        if not os.path.exists(self.imgpath):
            raise RuntimeError('file not exists')
        
        if self.imgpath[-3:]=='jp2': 
            self._handle = glymur.Jp2k(self.imgpath)
            if self._handle is None :
                raise RuntimeError('glymur handle is invalid')
            # else:
                # print(self._jp2handle._readonly)
                # self._jp2handle.parse()
                # self._jp2handle._initialize_shape()

        elif self.imgpath[-3:]=='tif':
            # load whole array in RAM
            self._handle = imread(self.imgpath)

        elif self.imgpath[-3:]=='dat':

            infoname = self.imgpath.replace('.dat','_info.pkl').replace('img','hdr')
            info = pickle.load(open(infoname,'rb'))
            self._handle = np.memmap(self.imgpath,dtype='uint8',mode='r',shape=info['shape'])
            
        self.imageshape = self._handle.shape
        # print(self.imageshape)
        self.ntiles_c = round(self.imageshape[1]/shp[1]) # FIXME: was ceil, changing to round for compat with ui
        self.ntiles_r = round(self.imageshape[0]/shp[0]) # not actually used anywhere - only print
        self.ntiles = self.ntiles_r * self.ntiles_c
        # print(self.ntiles)
        self.padding=padding
        self.tileshape = (shp[0],shp[1],3)

        self.dec_factor = 1
        
    def __str__(self):
        return str({
            'imgpath':self.imgpath, 
            'imageshape':self.imageshape,
            'tileshape':self.tileshape,
            'padding':self.padding,
            'ntiles':self.ntiles})

    def get_tile_extent(self,tilenum):
        # assert tilenum<self.ntiles
        tile_r = tilenum//self.ntiles_c
        tile_c = tilenum % self.ntiles_c
        tl = Point(self.tileshape[1]*tile_c,self.tileshape[0]*tile_r)
        br = Point(min(tl.x+self.tileshape[1],self.imageshape[1]),min(tl.y+self.tileshape[0],self.imageshape[0]))
        
        return Extent(tl,br)

    def get_padded_extent(self,ext):
        padding = self.padding
        nc = self.imageshape[1]
        nr = self.imageshape[0]

        r1 = ext.point1.y
        r2 = ext.point2.y
        c1 = ext.point1.x
        c2 = ext.point2.x

        c_cover = self.tileshape[1]-(c2-c1)
        r_cover = self.tileshape[0]-(r2-r1)

        mirror_top = 0
        if r1 - padding < 0:
            mirror_top = -(r1 - padding)
        else:
            r1 = r1-padding

        mirror_left = 0
        if c1 - padding < 0:
            mirror_left = -(c1 - padding)
        else:
            c1 = c1-padding

        mirror_bot = 0
        if r2 + padding + r_cover >= nr:
            mirror_bot = (r2 + padding + r_cover) - nr
        else:
            r2 = r2+padding

        mirror_right = 0
        if c2 + padding + c_cover >= nc:
            mirror_right = (c2 + padding + c_cover) - nc
        else:
            c2 = c2+padding
            
        df = int(self.dec_factor)    
        ext2 = Extent(Point(c1*df,r1*df),Point(c2*df,r2*df))
        region = Extent(Point(c1-mirror_left,r1-mirror_top), Point(c2+mirror_right,r2+mirror_bot))
        return ext2, region, (mirror_top, mirror_left, mirror_bot, mirror_right)

    def __getitem__(self,tilenum):
        if tilenum < self.ntiles:
            # print('access %d' % tilenum)
            
            ext = self.get_tile_extent(tilenum)

            ext2, region, mirrorvals = self.get_padded_extent(ext)
            
            imgurl = None

            df = int(self.dec_factor)
            # tic = datetime.now()
            arr = self._handle[to_slice(ext2,df)]
            # elapsed = datetime.now()-tic
            # print(f'{os.getpid()}:{elapsed.microseconds//1000}',end=" ",flush=True)
            (mirror_top, mirror_left, mirror_bot, mirror_right) = mirrorvals
            if mirror_top > 0:
                arr = np.pad(arr,[(mirror_top,0),(0,0),(0,0)],mode='reflect')
            if mirror_left > 0:
                arr = np.pad(arr,[(0,0),(mirror_left,0),(0,0)],mode='reflect')
            if mirror_bot> 0:
                arr = np.pad(arr,[(0,mirror_bot),(0,0),(0,0)],mode='reflect')
            if mirror_right > 0:
                arr = np.pad(arr,[(0,0),(0,mirror_right),(0,0)],mode='reflect')
            
            return arr, region, imgurl
        else:
            print('#',end="",flush=True)
            return np.zeros((0,0,3)), None, None

