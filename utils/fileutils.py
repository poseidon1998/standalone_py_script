#%% for autostacking
import glob
import os
from sys import stderr

def get_imglist(datadir='/store/repos1/37/BFI',series='BFI', suffix='', ext='jpg'):
    # img_list = glob.glob(datadir+'/*.'+ext)
    img_list = glob.glob(f'{datadir}/*_{series}-*{suffix}.'+ext)
    
    sections = {} # OrderedDict()
    
    for sec in img_list:
        pn,bn = os.path.split(sec)
        
        pre,base = bn.split('-ST_%s-SE_' % series)
        
        base = base.split('_')[0]
        secno = base.split('.')[0]
        if int(secno) not in sections:
            sections[int(secno)]=sec
        else:
            print('repeat %s' % secno)

    # print(sections)    
    mid = len(sections)//2

    secnumlist = sorted(sections)
    ref_sec = secnumlist[mid]
    seq1 = secnumlist[mid-1::-1]
    seq2 = secnumlist[mid+1:]   

    return secnumlist, sections, ref_sec, seq1, seq2  
    

def get_jp2list(datadir='/store/repos1/37/NISL',series='NISL',ext='jp2'):
    jp2_list = glob.glob(f'{datadir}/*_{series}*_compressed.'+ext)
    
    sections = {} # OrderedDict()
    sections_mr = {}
    for sec in jp2_list:
        pn,bn = os.path.split(sec)
        # secno = bn.split('_')[-2]
        # print(bn)
        pre,base = bn.split('-ST_%s-SE_' % series)
        
        if '-MR_' in base:
            secno = base.split('-')[0]
            if int(secno) not in sections_mr:
                sections_mr[int(secno)]=sec
            else:
                print('repeat_mr %s' % secno)
        else:
            secno = base.split('_')[0]
            if int(secno) not in sections:
                sections[int(secno)]=sec
            else:
                print('repeat %s' % secno)

    for secno in sections_mr:
        if secno not in sections:
            sections[secno]=sections_mr[secno]
        else:
            stderr.write(str(('e',secno,sections_mr[secno],sections[secno],'\n')))

    mid = len(sections)//2

    secnumlist = sorted(sections)
    ref_sec = secnumlist[mid]
    seq1 = secnumlist[mid-1::-1]
    seq2 = secnumlist[mid+1:]   

    return sections, ref_sec, seq1, seq2  

