from datetime import datetime
import json
import psycopg2 
import sys
from utils.api import requester
import requests
import constants
import utils

def calMetrics(biosample,secid,secno):
    conn = psycopg2.connect(dbname=constants.postgis_db,
                            user='myuser',
                            password='mypass',
                            host='ap3.humanbrain.in',
                            port=5432)
    cur = conn.cursor()
    qur ="SELECT ST_AsGeoJSON(coords) as coords,seriestype, ontology, tileno FROM metrics_values where secid=%s;"
    cur.execute(qur, (secid,))
    result = cur.fetchall()
    if result:
        print("********************************************")
        print("************CALCULATE METRICS***************")
        print("********************************************")
        current_datetime = datetime.now()
        for data in result:
            coord_str,st,onto,tileno=data
            coord_json = json.loads(coord_str)
            coords = coord_json["coordinates"]
            coordinates = [[[x, -y] for x, y in polygon] for polygon in coords]

            url = constants.processingUrlprefix + "getstName/" + str(st)
            payload = {}
            response = requester(url, payload, "GET")
            seriesType=response.data['seriesTypeName']
            print(coordinates,seriesType,onto,tileno)
            pngPath = constants.rootDir+ str(biosample) + '/appData/cellDetection/' + str(onto) +'/'+ str(seriesType)+'/' + str(secno) + '/512/512/' + str(tileno) +'.png'
            url1=constants.processingUrlprefix + "getImageMask"
            payload1 = {"path":pngPath}
            response = requester(url1, payload1, "POST")
            gt = response.data
            gt = "data:image/png;base64,"+str(gt)
            fastapi_url =constants.ap3Base + 'comparemasks/'
            payload2 = {
                'annotated_mask': gt,
                'currentsection': secno,
                'biosample': biosample,
                'coords': coordinates,
                'ontologyTree': '',
            }
            response = requests.post(fastapi_url, json=payload2)
            metrics_js = response.json()
            print(metrics_js)
            metrics=json.dumps(metrics_js)
            update_query = """
            UPDATE metrics_values
            SET datetime = %s, metrics = %s
            WHERE secid = %s AND tileno = %s;
            """
            cur.execute(update_query, (current_datetime, metrics, secid, tileno))
            conn.commit()
    else:
        print("***********************************************")
        print("************NO GROUNDTRUTH FOUND***************")
        print("***********************************************")
        
    cur.close()
    conn.close()


if __name__=="__main__":
    # e.g. /store/repos1/iitlab/humanbrain/analytics/141/appData/cellDetection/3/NISSL/214/512/512/3241.png
    
    biosample = sys.argv[1] 
    secid = sys.argv[2]
    secno = sys.argv[3]
    calMetrics(biosample,secid,secno)