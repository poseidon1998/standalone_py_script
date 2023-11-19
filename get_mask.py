import psycopg2 
import numpy as np
import constants
import utils
import cv2
import sys
import json
from utils.api import requester

def getMaskForSec(secid,filename):
    conn = psycopg2.connect(dbname=constants.postgis_db,
                            user='myuser',
                            password='mypass',
                            host='ap3.humanbrain.in',
                            port=5432)
    cur = conn.cursor()
    qur ="SELECT ST_AsGeoJSON(coords) as coords,tileno FROM metrics_values where secid=%s;"
    cur.execute(qur, (secid,))
    annotated_tile_coords = []
    for row in cur:
        rec = json.loads(row[0])
        coord  = rec['coordinates'][0][0]+rec['coordinates'][0][2]
        annotated_tile_coords.append(coord)
    print(annotated_tile_coords)
    cur.close()
    conn.close()
    url = constants.qcUrlPrefix + "querySectionById/" + str(secid)
    payload = {}
    response=requester(url, payload, "GET")
    
    width = response.data[0]['width']
    height = response.data[0]['height']
    print(width,height)
    tilesize = 512

    mask_blank = np.zeros((height,width),bool)
    for box in annotated_tile_coords:
        c1,r1,c2,r2=box
        print(r1,c1,r2,c2)
        mask_blank[r1:r2,c1:c2]=True
    mask_save = mask_blank[::64,::64].astype(np.uint8)
    print(mask_save.sum())
    cv2.imwrite('/mask/{}'.format(filename), mask_save*255)

# def get_tile_coords(tilenum,width,tilesize):
#     ntiles_c = round(width/tilesize)
#     tile_r = tilenum//ntiles_c
#     tile_c = tilenum % ntiles_c
#     tl = tile_c*512, tile_r*512
#     br = tl[0]+512, tl[1]+512
#     return tl[0],tl[1],br[0],br[1]

if __name__=="__main__":
    secid = sys.argv[1] 
    filename = sys.argv[2] 
    getMaskForSec(secid,filename)