import requests
import io
import numpy as np
from PIL import Image
from collections import namedtuple

Point = namedtuple('Point','x,y')
Extent = namedtuple('Extent','point1,point2')
Poly = namedtuple('Poly','point_lt,point_rt,point_rb,point_lb')
Box = namedtuple('Box','point_lt,w,h')

def corners_to_poly(ptlist):
    points = []
    for pt in ptlist:
        points.append(Point(pt[0],pt[1]))
    return Poly(*points[:4])

def poly_to_box(poly):
    w = poly.point_rt.x-poly.point_lt.x
    h = poly.point_rb.y-poly.point_rt.y
    return Box(poly.point_lt,w,h)

def get_image_from_url(imgurl):
    imgbytes = io.BytesIO(requests.get(imgurl).content)
    return np.array(Image.open(imgbytes)) #,mode='r',formats=('jpeg','png')))


class IIPWSIProxy:
    endpoint='http://apollo2.humanbrain.in:9081/fcgi-bin/iipsrv.fcgi'

    iipurl = {
        "fif.jtl": '?FIF=%s&WID=1024&GAM=1&MINMAX=1:0,255&MINMAX=2:0,255&MINMAX=3:0,255&JTL=%s,%s',
        "fif.jtl.0":'?FIF=%s&WID=1024&GAM=1&MINMAX=1:0,255&MINMAX=2:0,255&MINMAX=3:0,255&JTL=0,0',
        "fif.tnail":'?FIF=%s&WID=%d&CVT=jpeg',
        "fif.rgn":'?FIF=%s&WID=%d&HEI=%d&RGN=%f,%f,%f,%f&CVT=jpeg',
    }

    def get_reduced_iiif(self, reduce):
        # for 16mpp, use reduce = 5 (0.5->16 = 32 = 2^5)
        pct = 100/(2**reduce)
        imgurl = "/".join([self.endpoint+'?IIIF=%s'%self.jp2path,'full','pct:%f'%pct, '0', 'default.jpg'])
        return get_image_from_url(imgurl)
        
    def __init__(self, jp2path):
        # jp2path is obtained by iterating the return of utils.APIutils.get_imglist_api
        self.jp2path = jp2path
        self.info = requests.get(self.endpoint+f'?IIIF={jp2path}/info.json').json()

    def _get_iip_rgn(self,x,y,w,h):
        return (
            x/self.info['width'],
            y/self.info['height'],
            w/self.info['width'],
            h/self.info['height'])
        
    def shape(self):
        return self.info['height'],self.info['width']
    
    def getthumbnail(self,ds=8):
        # um: [0.5, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
        # ds:   [0, 1, 2, 3, 4, 5,  6,  7,  8 , 9,  10]
        assert ds >= 5 and ds < 11
        tnwidth = self.info['width']//(2**ds)
        imgurl = self.endpoint+self.iipurl['fif.tnail'] % (self.jp2path,tnwidth)
        return get_image_from_url(imgurl)
    
    def get_tile(self,box):
        x,y,w,h = box.point_lt.x, box.point_lt.y, box.w, box.h

        assert x >= 0 and x <= self.info['width'] and y >= 0 and y <= self.info['height']
        assert w > 0 and w <= 4096 and h > 0 and h <= 4096
        rgn = self._get_iip_rgn(x,y,w,h)
        imgurl = self.endpoint+self.iipurl['fif.rgn'] % (
            self.jp2path,w,h,*rgn
        )
        return get_image_from_url(imgurl)
        
    