

limsBasePath            = "http://apollo2.humanbrain.in:8000"
BasePath            = "http://dev2sasi.humanbrain.in:8000"

processingUrlprefix     = limsBasePath + "/processing/"
limsUrlPrefix           = limsBasePath + "/lims/"
qcUrlPrefix             = limsBasePath + "/qc/"
masterConfigUrlPrefix   = limsBasePath + "/masterconfig/"
jirUrlPrefix            = limsBasePath + "/jira/"

processingUrlprefix_dev     = BasePath + "/processing/"
limsUrlPrefix_dev           = BasePath + "/lims/"
qcUrlPrefix_dev             = BasePath + "/qc/"
masterConfigUrlPrefix_dev   = BasePath + "/masterconfig/"
jirUrlPrefix_dev            = BasePath + "/jira/"

LIMS_SideBatchURL       = limsBasePath + "/admin/processing/slideinfo/?q="
ap3Base = "http://ap3.humanbrain.in:90/"
rootDir = '/store/repos1/iitlab/humanbrain/analytics/'

jenkinsBase             = 'http://dev2nathan.humanbrain.in:9011/'
Jenkins_auth            = ('admin','Health#123')
celDetectExrUrl         = jenkinsBase + '/job/tst_cellD_exe/build?token=sasi&'
JenkinsKey_mohan         = 'Basic YWRtaW46MTE2OTU5Njc0YmMzYzAwM2NiMTNmOTY4ZjQxOWMxMzczOQ=='
JenkinsKey_sasi        = 'Basic QWRtaW46MTExOWJmZTA3ZmY3ZjkxYTcyMzM5N2Q0ZTBjYTllMTA0NQ=='
postgis_db = 'cellannotationMetrics'
postgis_db_dev = 'metrics_dev'
host = "apollo1.humanbrain.in"
dgxhost ="dgx3.humanbrain.in"
user = "appUser"