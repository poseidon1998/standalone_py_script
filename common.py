import scipy
from scipy.stats import kurtosis
import numpy as np
from skimage.exposure import adjust_gamma

def auto_gamma(arr, sp='auto', ref_val=192, step = 0.15, tol = 0.01, eta=2, max_iter=30, dbg=False):
    """find gamma iteratively until 8% (sp) of blue intensities (arr[...,2]) are < 192;
        sp='auto' - choose setpoint based on kurtosis (indicator of dense or moderate or sparse tile)
        ref_val: 192 (sum(0-192)==75% of dark)
        step: 0.15 (gamma update steps)
        eta: 2 (momentum)
        tol: 0.01 (stopping when pv is close enough)
        max_iter: 30 (10-100)
        dbg: False (print debug info)
    """
    
    assert arr.dtype == 'uint8'
    assert step>0
    if sp !='auto':
        assert sp>0 and sp < 1
    else:
        ku = kurtosis(arr[...,2].ravel())
        sp = 0.08
        if ku < 5: sp = 0.04 # dense
        if ku > 10: sp = 0.12 # sparse
            
    assert ref_val > 100 and ref_val < 240
    assert tol > 0.0001 and tol < 0.05
    
    cnt=arr.shape[0]*arr.shape[1]

    data2 = arr.copy()
    gam = 1
    eta = 2 # momentum
    
    max_iter = max(10,min(100,max_iter)) # sanity

    for _ in range(max_iter):
        pv = np.sum(data2[:,:,2]<ref_val)/cnt
        err = sp-pv
        err_pc = 1-pv/sp
        
        if dbg:print(sp,pv,err,err_pc,gam)

        if np.abs(err) < tol:
            break

        gam2 = gam + step*err_pc*eta
        if gam2 < 0: # can't be negative
            gam = gam*3/4
        else:
            gam = gam2
        data2 = adjust_gamma(arr,gam)

    return data2, gam
