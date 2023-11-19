import json
import constants
import utils
import os
from utils.api import requester
   
def getSeriesJobs():
    try:
        url = constants.processingUrlprefix + "getcdSeriesJob/"
        payload = {}
        response = requester(url, payload, "GET")
        data = response.data[0]
        
        # input_Dir = data['jp2Path']
        # input_Dir1 = f"{constants.user}@{constants.host}:{input_Dir}"
        # dstpath    = '/store/repos1/input'
        # copyFile = "rsync -Pav %s %s" % (input_Dir1, dstpath)
        
        # print('COPY..', copyFile)
        # os.system(copyFile)
        return(data)
         
    except Exception as e :
        print("An error occurred ", str(e))
        return str(e)

if __name__ == "__main__":
    result = getSeriesJobs()
    print(json.dumps(result))    