from collections import namedtuple
import argparse
import sys

def parseargs(argspec,named=False):
    """parseargs(argspec)
        argspec = {ii:('name',type,'default','helptext')}
    ii is position in argv (all positional args); 
    if named==True, all named arguments -- use ArgumentParser
    """
    argvals = {}
    assert type(argspec)==dict
    if named:
        ap = argparse.ArgumentParser(allow_abbrev=False)
        for v in argspec.values():
            name = "--"+v[0]
            opts = {}
            if len(v)>1:
                opts['type']=v[1]
            if len(v)>2:
                opts['default']=v[2]
            else:
                opts['required']=True
            if len(v)>3:
                opts['help']=v[3]
            ap.add_argument(name,**opts)

        argvals = vars(ap.parse_args())

    else:
        for k,v in argspec.items():
            nm,typ = v[:2]
            if len(sys.argv)>k:
                argvals[nm] = typ(sys.argv[k]) # may raise index error
                
            elif len(v)>2: # take supplied default 
                if v[2] is not None:
                    argvals[nm]=typ(v[2])
                else:
                    argvals[nm]=None
            else:
                print(argspec)
                print(argvals)
                raise IndexError
            
    return namedtuple('args',argvals)(**argvals)

def extendargs(args,key,val):
    argsdict = args._asdict()
    assert key not in argsdict
    argsdict[key]=val
    return namedtuple('args',argsdict)(**argsdict)


