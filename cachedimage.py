import os
from PIL import Image
import numpy as np
import tempfile
import subprocess
from common import auto_gamma
from functools import partial
from skimage import transform
from skimage.exposure import rescale_intensity
from skimage.morphology import dilation, square


get_rigid_xfm = partial(transform.estimate_transform,'euclidean')

def expand_lowres(jp2_path, reduce, outdir = '.'):
    im = None
    with tempfile.TemporaryDirectory(dir=outdir) as tmpdirname:
        ret=subprocess.call(f'/app/bin/kdu_expand -i {jp2_path} -o {tmpdirname}/tmp.tif -reduce {reduce} -quiet',shell=True)
        if ret==0:
            im = np.array(Image.open(tmpdirname+'/tmp.tif'))
            os.unlink(tmpdirname+'/tmp.tif')
            
        else:
            raise RuntimeError("kdu_expand failed in expand_lowres")
    return im


class SectionImage8U:

    def __init__(self, img_path, mpp=16, removeblack=False,
                 gray=False,invert=False,adjustgamma=True,
                 usecache=True,pngdir = '.',tmpdir='.'):
        
        self.img_path = img_path
        self.tforms = []
        
        pn,bn = os.path.split(img_path)
        
        self.arr = None
        self._arr0 = None
        pngpath = None
        ext = img_path.split('.')[-1]
            
        if usecache and 'jp2' in ext:
            pngpath = pngdir +'/'+bn[:-4]+'.png'
            if os.path.exists(pngpath):
                try:
                    self.arr = np.array(Image.open(pngpath))
                    assert len(self.arr.shape)==3 and self.arr.shape[-1]==3, 'unexpected shape '+str(self.arr.shape)
                    native_mpp = 16
                    assert mpp>=16
                    downsample = int(mpp/native_mpp)
                    self.arr = self.arr[::downsample,::downsample,:]
                except Exception as ex:
                    print(pngpath,ex)
                    self.arr = None

        if self.arr is None:
            
            if 'jp2' in ext:                
                native_mpp = 0.5
                downsample = int(mpp/native_mpp)
                # jp2obj = glymur.Jp2k(img_path)
                # self.arr = np.array(jp2obj[::downsample,::downsample,:]).astype(np.uint8) # decimate to 64um
                r = int(np.log2(downsample))
                assert 2**r == downsample, "not a power of 2"
                self.arr = expand_lowres(img_path,r,tmpdir)
                if pngpath is not None:
                    Image.fromarray(self.arr).save(pngpath)
                    
            elif 'jpg' in ext:
                self.arr = np.array(Image.open(img_path))[::downsample,::downsample,:]
                
        pre,base = bn.split('-SE_')
        if '-MR_' in base:
            self.secno = int(base.split('-')[0])
        else:
            self.secno = int(base.split('_')[0])
        
        # self.ch = 0 # for moments
        self.seriesname = ''
        if '-ST_NISL-' in bn:
            self.seriesname = 'NISL'
            self.ch = 1 # green in Nissl
        if '-ST_HEOS-' in bn:
            self.seriesname = 'HEOS'
            self.ch = 2 # trying blue channel in  H&E 

        if 'jpg' in ext:
            self.ch = 2 # for bfi
        
       
        self.contentpercent = 1
        
        if removeblack: self._removeblack()
        
        self._arr0 = self.arr.copy() # keep a copy of original
        
        if 'jp2' in ext and adjustgamma:
            self.arr, gam = auto_gamma(self._arr0)
            # print('gamma:',gam)
        
        if gray: self._gray()
        
        if invert: self._complement(range_limit=adjustgamma)
        
        self.keypoints = None
        self.args = {'removeblack':removeblack,'gray':gray, 'invert':invert,'adjustgamma':adjustgamma}
        # needed in load_tforms to replay from arr0
            
    def _pad(self, paddedsize=(1024,1536),bordercolor = None):

        assert self.keypoints is None
        nr,nc,_ = self.arr.shape
        srcpts = np.array([[0,0],[0,nc]]) # r,c
        newpts = srcpts.copy()

        pad_r = [0,0]
        pad_c = [0,0]
        if bordercolor is None:
            bordercolor = np.mean(self.arr[:,:10,:])
            bordercolor = 255 if bordercolor > 200 else 0 
        if paddedsize is not None:
            ps = paddedsize
            if nr < ps[0]:
                pad_r[0] = (ps[0]-nr)//2
                pad_r[1] = ps[0]-nr-pad_r[0]
            if nc < ps[1]:
                pad_c[0] = (ps[1]-nc)//2
                pad_c[1] = ps[1]-nc-pad_c[0]

            self.arr = np.pad(self.arr,(pad_r,pad_c,(0,0)),mode='constant',constant_values=bordercolor)
            # self._arr0 = np.pad(self._arr0,(pad_r,pad_c,(0,0)),mode='constant',constant_values=bordercolor)

            nr,nc,_ = self.arr.shape
            if nr > ps[0]: # crop
                start = ((nr-ps[0])*3)//4
                end = start+ps[0]
                self.arr=self.arr[start:end,...]
                # self._arr0=self._arr0[nr-ps[0]:,...]
            if nc > ps[1]:
                start = ((nc-ps[1])*3)//4
                end = start+ps[1]
                self.arr=self.arr[:,start:end,:]
                # self._arr0=self._arr0[:,nc-ps[1]:,:]
                
        newpts[:,0]+=pad_r[0]
        newpts[:,1]+=pad_c[0]
        self.tforms.append((get_rigid_xfm(srcpts,newpts),'pad',paddedsize))
        self.contentpercent = nr*nc/(paddedsize[0]*paddedsize[1])

    def _gray(self):
        self.arr = self.arr[...,self.ch]
        self.arr = self.arr[...,np.newaxis]
        self.ch = 0 # FIXME

    def _complement(self,range_limit=True):
        self.arr = 255-self.arr
        if range_limit:
            in_range = np.percentile(self.arr,(5,99.99)).astype(np.uint8)
            self.arr = rescale_intensity(self.arr,in_range=tuple(in_range),
                                         out_range=(0,192)).astype(np.uint8)
    
    def _removeblack(self):
        img = self.arr
        blk = (img[:,:,0]<20) & (img[:,:,1]<20) & (img[:,:,2]<20)
        blk = dilation(blk,square(39)) #
        img_r = np.where(blk,255,img[:,:,0]) #XXX: 255 is ok for brightfield nissl - check for others
        img_g = np.where(blk,255,img[:,:,1]) #FIXME: inpaint might be better?
        img_b = np.where(blk,255,img[:,:,2])
        self.arr = np.dstack((img_r,img_g,img_b))
    
    def _rotate90(self):
        assert self.keypoints is None
        nr,nc = self.arr.shape[:2]
        srcpts = np.array([[0,0],[0,nc]]) # r,c

        self.arr = np.fliplr(np.transpose(self.arr,axes=(1,0,2)))
        # self._arr0 = np.fliplr(np.transpose(self._arr0,axes=(1,0,2)))

        newpts = np.array([[0,nr],[nc,nr]])
        self.tforms.append((get_rigid_xfm(srcpts,newpts),'rot90'))

    def _rotate180(self):
        assert self.keypoints is None
        nr,nc,_ = self.arr.shape
        srcpts = np.array([[0,0],[0,nc]]) # r,c

        self.arr = np.fliplr(np.flipud(self.arr))
        # self._arr0 = np.fliplr(np.flipud(self._arr0))

        newpts = np.array([[nr,nc],[nr,0]])
        self.tforms.append((get_rigid_xfm(srcpts,newpts),'rot180'))
    
