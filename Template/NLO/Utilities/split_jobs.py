#!/usr/bin/env python
#  MZ, 2012-06-14
import os

class SplitJobsError(Exception):
    pass

max_events = {'H' :0, 'S': 0, 'F': 0, 'V': 0, 'B': 0}

#read the nevents_unweighted file 
nevents_file = open('nevents_unweighted')
nevents_lines = nevents_file.read().split('\n')
nevents_file.close()
jobs = []
tot_events = 0
for line in nevents_lines:
    if line:
        channel = os.path.dirname(line.split()[0])
        (dir, chann) = os.path.split(channel)
        ev_type = chann[1]
        nevts = int(line.split()[1])
        xsec = float(line.split()[2])
        jobs.append({'dir': dir, 'channel': chann, 'type': ev_type, \
                'nevts': nevts, 'xsec': xsec})
        tot_events += nevts 
        try:
            max_events[ev_type] = max(max_events[ev_type], nevts)
        except KeyError:
            raise SplitJobsError('Unknown run_mode, %s, %s, %s' \
                    %(dir, chann, ev_type))


print 'nevents_unweighted read, found %d jobs with a total of %d events' % (len(jobs), tot_events)

max_dict = {}

for (k, max_n) in max_events.items():
    if max_n:
        print 'Max %s-events per channel found is %d' % (k, max_n)
        max_dict[k] = max(max_n/20, 100)
        if max_dict[k]:
            print 'Max number of events in splitted job is %d' % max_dict[k]
    
while True:
    for job in jobs:
        if max_dict[job['type']]:
            job['nsplit'] = job['nevts']/max_dict[job['type']] + 1
        else:
            job['nsplit'] = 1
    ntot_dict = {}
    for k in max_dict.keys():
        ntot_dict[k] = sum(d['nsplit'] for d in jobs if d['type'] == k) 
    print 'This will give:'
    for k, tot in ntot_dict.items():
        if tot:
            print '  %d %s-events jobs' % (tot, k)
    yes = input('Is this acceptable? (1: yes 0: no) ')
    if yes == 1:
        break
    
    for (k, max_n) in max_events.items():
        if max_n:
            print 'Found %s-events' % k 
            print 'Max %s-events per channel found is %d' % (k, max_n)
            new_max = input('Give new maximum if you want to split jobs ') 
            max_dict[k] = new_max



splitted_lines = []
tot_events = 0
for job in jobs:
    dir = os.path.join(job['dir'], job['channel'])
    job_events = 0
    for i in range(job['nsplit']):
        filename = os.path.join(dir,'events_%d.lhe' % (i+1))
        if i != (job['nsplit']-1):
            split_nevts = job['nevts']/job['nsplit']
            split_xsec = job['xsec']*float(split_nevts)/float(job['nevts'])
        else:
            #split_nevts = long(job['nevts']) - long((job['nsplit'] - 1) * job['nevts']/job['nsplit'])
            split_nevts = job['nevts']/job['nsplit'] + job['nevts'] % job['nsplit']
            split_xsec = job['xsec']*float(split_nevts)/float(job['nevts'])
        tot_events += split_nevts
        job_events += split_nevts
        splitted_lines.append('%s     %d     %9e' % (filename.ljust(40), split_nevts, split_xsec))
        nevts_filename = os.path.join(dir,'nevts__%d' % (i+1))
        nevts_file = open(nevts_filename, 'w')
        nevts_file.write('%d' % split_nevts)
        nevts_file.close()
    print '%s, %s, Original %d, after splitting %d' % (job['dir'], job['channel'], job['nevts'], job_events)

new_nevents_file = open('nevents_unweighted_splitted', 'w')
new_nevents_file.write('\n'.join(splitted_lines))
new_nevents_file.close()
        
print 'Done, total %d events' %  tot_events


    

    