#%% --- general utility functions

from datetime import datetime

class TicToc(object):
    def __init__(self, name=None):
        self.name = name

    def __enter__(self):
        self.tic = datetime.now()
        return self

    def __exit__(self, type, value, traceback):
        self.toc = datetime.now()
        self.elapsed = self.toc - self.tic

    def __str__(self):
        return "%s: %s" % (self.name or 'Time', self.elapsed)


#%%
def dict_filter(dictobj,cnt=None,**kwargs):
    # usage e.g dict_filter(out,1,position_index=secnumber)[0]
    outelts = []
    for elt in dictobj:
        matched=True
        for key,value in kwargs.items():
            if elt[key]!=value:
                matched=False
                break
        if matched:
            outelts.append(elt)
        if cnt is None:
            continue
        if len(outelts)==cnt:
            break
                
    return outelts


def get_intervals(seq,dx=3,max_skip=0):

    if seq[0] < seq[-1]: # asc
        dx=-dx
    intervals = []
    left = 0
    ii = left

    while ii + 1 < len(seq):
        int_i = [seq[left]]
        missing_i = []
        
        while ii+1<len(seq):
            cur = seq[ii]
            nxt = seq[ii+1]
            
            if cur-nxt==dx:
                int_i.append(nxt)
                ii+=1
                
            else:
                if (cur-nxt)//dx <= max_skip+1:
                    missing_i.extend([cur-m*dx for m in range(1,max_skip+1)])
                    int_i.append(nxt)
                else:
                    break
                ii+=1
                
        left = ii+1
        ii = left
        missing_i = list(set(missing_i)-set(int_i))
        intervals.append((int_i,sorted(missing_i)))
        
    return intervals,dx



