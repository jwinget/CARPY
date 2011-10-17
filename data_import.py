#!/usr/bin/python2.7

import os, sys, csv, re
from subprocess import call
from carpy import *

##########################
# USER-DEFINED VARIABLES #
##########################
datafile = 'db11.csv'

# Define models

# Create the database
db.drop_all()
db.create_all()

# Read in data from flat file
f = open(datafile, 'rb')
data = csv.reader(f)
data.next() # skip headers

# Calculate percentiles and add them to the flat file

	# Add the percentiles directly to the data variable

# Populate the database
added = []
for protein in data:
	if protein[1] not in added:
		added.append(protein[1])
		# Convert natural language strings to booleans
		# Need to think about how to solve "NA" != "No"
		for i in xrange(len(protein)):
			if protein[i] in ['tagged', 'visualized', 'TAP visualized', 'TRUE']:
				protein[i] = 1
			elif protein[i] in ['not tagged', 'not TAP visualized', 'not visualized', '', 'FALSE', 'NA']:
				protein[i] = 0
			else:
				pass
		p = Protein(*protein)
		db.session.add(p)
db.session.commit()

print "="*20
print "Added "+str(len(added))+" proteins"
print "="*20

# Update the global stats
#print 'Calculating global statistics'
#print "="*20
## generate stats with R
#global_stats = 'global_stats.txt'
#call('R CMD BATCH --slave --no-timing "--args '+ datafile +'" scripts/global_stats.R '+ global_stats, shell=True)
## read in the results
#g = open(global_stats, 'rb')
#for line in g:
#	print line
#g.close()

print 'Done'
print "*"*20
print "*"*20
f.close()
