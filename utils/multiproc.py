#%% --- for processpool 

from multiprocessing import cpu_count
from collections import namedtuple

MultiprocPlan = namedtuple('MultiprocPlan','worksize,nworkers,perworker,rounds,minwork')

def get_multiproc_plan(worksize,minwork=50):
    
    assert minwork>0 
    minwork = min(minwork, worksize)
    
    maxcnt = cpu_count()
    
    for factor in (1/2, 2/3, 3/4, 4/5, 5/6, 6/7, 7/8):

        nworkers = int(maxcnt*factor)
    
        perworker = worksize//nworkers

        rounds = perworker//minwork
        
        while rounds < 1 and nworkers > 1:
            nworkers=nworkers//2
            perworker = worksize//nworkers

            rounds = perworker//minwork
        
        if rounds < 1:
            rounds = 1
            break
            
        if rounds > 5: # need more workers
            continue
        else:
            break
    return MultiprocPlan(worksize,nworkers,perworker,rounds,minwork)


