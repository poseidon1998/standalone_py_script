#%% --- django api utilities

import traceback
import requests
import json

class APIutils:
    def __init__(self,
                 endpoint='http://apollo2.humanbrain.in:8000',
                 use_requests=True):
        self.endpoint = endpoint
        self.authtuple = ('admin','admin')
        self.localdir = '/data/special/apicache'
        self.use_requests = use_requests
        if self.use_requests:
            try:
                requests.get(self.endpoint,timeout=10)
            except:
                print('warning: api endpoint not reachable. setting use_requests to False')
                self.use_requests = False

        if not self.use_requests:
            # check self.localdir
            assert os.path.exists(self.localdir+'/qc/SeriesSet.json')
            assert os.path.exists(self.localdir+'/GW/getBrainViewerDetails')
            assert os.path.exists(self.localdir+'/BR/AppAnnotationType')

    def __api_or_local(self,apisuffix,**api_extra_querystringargs):
        if self.use_requests:
            qs = "?"
            for k,v in api_extra_querystringargs.items():
                qs+=f'{k}={v}&'
            resp = requests.get(self.endpoint+apisuffix+qs[:-1],auth=self.authtuple).json()
            if os.path.exists(self.localdir):
                localfname = self.localdir+apisuffix.replace(':','_')+'.json'
                os.makedirs(os.path.dirname(localfname),exist_ok=True)
                # if os.path.exists(localfname):                
                #     os.rename(localfname,localfname+'_last')
                json.dump(resp,open(localfname,'wt'))
            return resp
        else:
            return json.load(open(self.localdir+apisuffix.replace(':','_')+'.json','rt'))
        
    def get_ssid(self,biosampleid):
        sslist = self.__api_or_local('/qc/SeriesSet',format='json')
        # sslist=requests.get(self.endpoint+'/qc/SeriesSet/?format=json',auth=self.authtuple).json()
        for rec in sslist:
            if str(rec['biosample'])==str(biosampleid):
                return int(rec['id'])
        return None

    def get_imglist_api(self,biosampleid):

        ssid = self.get_ssid(biosampleid)
        imglist = self.__api_or_local(f'/GW/getBrainViewerDetails/IIT/V1/SS-{ssid}:-1:-1',format='json')
        
        seriesnames = {} # fullname:shortname
        shortnames = []
        for serfullname,serlist in imglist['thumbNail'].items():
            dn = os.path.dirname(serlist[0]['jp2Path'])
            shortname = dn.split('/')[-1]
            if shortname not in shortnames:
                seriesnames[serfullname]=shortname
                shortnames.append(shortname)
            

        serieslist = {} # shortname:[{elt}]
        for serfullname,sername in seriesnames.items():
            
            sections = {}
            for elt in imglist['thumbNail'][serfullname]:
                sections[elt['position_index']]=elt
            serieslist[sername]=sections

        return serieslist
    
    def get_atlastree(self,ontoid):
        resp =  self.__api_or_local(f'/BR/AppAnnotationType/{ontoid}',format='json')
        ontodata = json.loads(resp['app_annotation_tree_json'])
        return ontodata['msg']

#%%

from typing import Any

class ErrorMessage:
    errorMessage=''
    errorCode=0

    def __init__(self,errorCode=0,errorMessage=''):
        self.errorCode =errorCode
        self.errorMessage= errorMessage

class ReturnData:
    data:Any
    error:ErrorMessage
    
    def __init__(self,data={},err=ErrorMessage()):
        self.data =data
        self.error= err       

def requester(url,payload,method):
    payload_str = json.dumps(payload)

    headers = {
    'Authorization': 'Basic YWRtaW46YWRtaW4=',
    'Content-Type': 'application/json'
    }

    response = requests.request(method, url, headers=headers, data=payload_str)
    #print(payload_str)
    #print(response.text)
    err=ErrorMessage()
    dat={}
    try:
        dat = json.loads(response.text)                
    except Exception as ee1:        
        ret = {'data': {},'error':{'errorCode':1, 'errorMessage':str(traceback.format_exc())}}
        err=ErrorMessage(1,str(traceback.format_exc()))
    return ReturnData(dat,err)


