#!/usr/bin/env python
"""mk_level2_fsf.py - make 2nd level (between-runs) fixed effect model
"""

## Copyright 2011, Russell Poldrack. All rights reserved.

## Redistribution and use in source and binary forms, with or without modification, are
## permitted provided that the following conditions are met:

##    1. Redistributions of source code must retain the above copyright notice, this list of
##       conditions and the following disclaimer.

##    2. Redistributions in binary form must reproduce the above copyright notice, this list
##       of conditions and the following disclaimer in the documentation and/or other materials
##       provided with the distribution.

## THIS SOFTWARE IS PROVIDED BY RUSSELL POLDRACK ``AS IS'' AND ANY EXPRESS OR IMPLIED
## WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
## FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL RUSSELL POLDRACK OR
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
## CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
## SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
## ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
## NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.



# create fsf file for arbitrary design
import numpy as N
import sys
import os
import subprocess as sub
from openfmri_utils import *

def mk_level2_fsf(taskid,subnum,tasknum,runs,basedir,modelnum):

    subdir='%s%s/sub%03d'%(basedir,taskid,subnum)

    # read the conditions_key file
    cond_key=load_condkey(basedir+taskid+'/models/model%03d/condition_key.txt'%modelnum)
    all_addl_contrasts=load_contrasts(basedir+taskid+'/models/model%03d/task_contrasts.txt'%modelnum)
    if all_addl_contrasts.has_key('task%03d'%tasknum):
        addl_contrasts=all_addl_contrasts['task%03d'%tasknum]
        n_addl_contrasts=len(addl_contrasts)
    else:
        n_addl_contrasts=0
    
    conditions=cond_key[tasknum].values()
    nruns=len(runs)

    stubfilename='/home1/01329/poldrack/code/openfmri/pipeline/design_level2.stub'
    modeldir=subdir+'/model/model%03d'%modelnum

    outfilename='%s/task%03d.fsf'%(modeldir,tasknum)
    outfile=open(outfilename,'w')
    outfile.write('# Automatically generated by mk_fsf.py\n')

    # first get common lines from stub file
    stubfile=open(stubfilename,'r')
    for l in stubfile:
        outfile.write(l)

    stubfile.close()

    # now add custom lines

    # first check for empty EV file
    empty_evs=[]
    for r in range(nruns):
        if os.path.exists("%s/%s/sub%03d/model/model%03d/onsets/task%03d_run%03d/empty_evs.txt"%(basedir,taskid,subnum, modelnum,tasknum,runs[r])):
            evfile=open("%s/%s/sub%03d/model/model%03d/onsets/task%03d_run%03d/empty_evs.txt"%(basedir,taskid,subnum,modelnum,tasknum,runs[r]),'r')
            empty_evs=[int(x.strip()) for x in evfile.readlines()]
            evfile.close()
            
    outfile.write('\n\n### AUTOMATICALLY GENERATED PART###\n\n')

    outfile.write('set fmri(outputdir) "%s/task%03d.gfeat"\n'%(modeldir,tasknum))
    outfile.write('set fmri(npts) %d\n'%nruns) # number of runs
    outfile.write('set fmri(multiple) %d\n'%nruns) # number of runs
    outfile.write('set fmri(ncopeinputs) %d\n'%int(len(cond_key[tasknum])+1+n_addl_contrasts)) # number of copes
    
    for r in range(nruns):
        outfile.write('set feat_files(%d) "%s/task%03d_run%03d.feat"\n'%(int(r+1),modeldir,tasknum,runs[r]))
        outfile.write('set fmri(evg%d.1) 1\n'%int(r+1))
        outfile.write('set fmri(groupmem.%d) 1\n'%int(r+1))

    # need to figure out if any runs have empty EVs and leave them out

    for c in range(len(cond_key[tasknum])+1+n_addl_contrasts):
        if not c+1 in empty_evs:
            outfile.write('set fmri(copeinput.%d) 1\n'%int(c+1))
        else:
             outfile.write('set fmri(copeinput.%d) 0\n'%int(c+1))
           
        

                
        
    outfile.close()
#    print 'outfilename: '+outfilename
    return outfilename