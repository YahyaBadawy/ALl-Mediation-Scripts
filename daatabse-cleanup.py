__author__ = "Yahya Badawy"
__license__ = "Public Domain"
__version__ = "2.7"

# Pyhton script for database cleanup where it iterates over each server on cluster truncating, reindexing and vacuuming log entry tables.

import sys
import os
import subprocess
import time

# Defining ix method to return dictionary key.

def ix(self, dic, n): #don't use dict as  a variable name
   try:
       return sorted(dic)[n] # or sorted(dic)[n] if you want the keys to be sorted
   except IndexError:
       print 'not enough keys'

# starting cleanup action.
sys.stdout.write('Cleanup Started!\n')

#Mapping each server to corresponding physical blade.

stream = subprocess.check_output('hares -state | grep "^Server" | grep ONLINE | awk {\'print $1, $3\'}', shell=True)

# Constructing map  dictionary with servers as keys and blades as values.
mapDict = {}
for line in stream.split('\n'):
    line = line.strip()
    if line:
        serverName, bladeName = line.split()
        mapDict[serverName] = bladeName

# Constructing psql map dictionary

postgresDict={
"Server1" : 'PGPASSWORD=thule psql -d fm_db_Server1 -p 5432 -h 172.30.147.172  -U mmsuper',
"Server2" : 'PGPASSWORD=thule psql -d fm_db_Server2 -p 5442 -h 172.30.147.172  -U mmsuper',
"Server3" : 'PGPASSWORD=thule psql -d fm_db_Server3 -p 5452 -h 172.30.147.173  -U mmsuper',
"Server4" : 'PGPASSWORD=thule psql -d fm_db_Server4 -p 5462 -h 172.30.147.173  -U mmsuper',
"Server5" : 'PGPASSWORD=thule psql -d fm_db_Server5 -p 5472 -h 172.30.147.174  -U mmsuper',
"Server6" : 'PGPASSWORD=thule psql -d fm_db_Server6 -p 5482 -h 172.30.147.174  -U mmsuper',
"Server7" : 'PGPASSWORD=thule psql -d fm_db_Server7 -p 5492 -h 172.30.147.175  -U mmsuper',
"Server8" : 'PGPASSWORD=thule psql -d fm_db_Server8 -p 5502 -h 172.30.147.175  -U mmsuper',
"Server9" : 'PGPASSWORD=thule psql -d fm_db_Server9 -p 5512 -h 172.30.147.176  -U mmsuper',
"Server10" : 'PGPASSWORD=thule psql -d fm_db_Server10 -p 5522 -h 172.30.147.176  -U mmsuper',
"Server11" : 'PGPASSWORD=thule psql -d fm_db_Server11 -p 5532 -h 172.30.147.177  -U mmsuper',
"Server12" : 'PGPASSWORD=thule psql -d fm_db_Server12 -p 5572 -h 172.30.147.177  -U mmsuper',
"Server13" : 'PGPASSWORD=thule psql -d fm_db_Server13 -p 5582 -h 172.30.147.178  -U mmsuper',
"Server14" : 'PGPASSWORD=thule psql -d fm_db_Server14 -p 5592 -h 172.30.147.178  -U mmsuper',
"Server15" : 'PGPASSWORD=thule psql -d fm_db_Server15 -p 5602 -h 172.30.147.179  -U mmsuper',
"Server16" : 'PGPASSWORD=thule psql -d fm_db_Server16 -p 5612 -h 172.30.147.179  -U mmsuper',
"Server17" : 'PGPASSWORD=thule psql -d fm_db_Server17 -p 5622 -h 172.30.147.180  -U mmsuper',
"Server18" : 'PGPASSWORD=thule psql -d fm_db_Server18 -p 5632 -h 172.30.147.180  -U mmsuper',
"Server19" : 'PGPASSWORD=thule psql -d fm_db_Server19 -p 5642 -h 172.30.147.181  -U mmsuper',
"Server20" : 'PGPASSWORD=thule psql -d fm_db_Server20 -p 5652 -h 172.30.147.181  -U mmsuper',
"Server21" : 'PGPASSWORD=thule psql -d fm_db_Server21 -p 5662 -h 172.30.147.182  -U mmsuper',
"Server22" : 'PGPASSWORD=thule psql -d fm_db_Server22 -p 5672 -h 172.30.147.182  -U mmsuper',
"Server23" : 'PGPASSWORD=thule psql -d fm_db_Server23 -p 5682 -h 172.30.147.183  -U mmsuper',
"Server24" : 'PGPASSWORD=thule psql -d fm_db_Server24 -p 5692 -h 172.30.147.183  -U mmsuper',
"Server25" : 'PGPASSWORD=thule psql -d fm_db_Server25 -p 5702 -h 172.30.147.184  -U mmsuper',
"Server26" : 'PGPASSWORD=thule psql -d fm_db_Server26 -p 5712 -h 172.30.147.184  -U mmsuper',
"Server27" : 'PGPASSWORD=thule psql -d fm_db_Server27 -p 5722 -h 172.30.147.185  -U mmsuper',
"Server28" : 'PGPASSWORD=thule psql -d fm_db_Server28 -p 5732 -h 172.30.147.185  -U mmsuper',
"Server29" : 'PGPASSWORD=thule psql -d fm_db_Server29 -p 5809 -h 172.30.147.174  -U mmsuper'
}

# Constructing postgres table space query map dictionary.

postgres_status_Dict={
"Server1" : 'PGPASSWORD=thule psql -d fm_db_Server1 -p 5432 -h 172.30.147.172  -U mmsuper -c "SELECT nspname || \'.\' || relname AS \"relation\", pg_size_pretty(pg_relation_size(C.oid)) AS \"size\" FROM pg_class C LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace) WHERE nspname NOT IN (\'pg_catalog\',\'information_schema\') ORDER BY pg_relation_size(C.oid) DESC LIMIT 20;"',
"Server2" : 'PGPASSWORD=thule psql -d fm_db_Server2 -p 5442 -h 172.30.147.172  -U mmsuper -c "SELECT nspname || \'.\' || relname AS \"relation\", pg_size_pretty(pg_relation_size(C.oid)) AS \"size\" FROM pg_class C LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace) WHERE nspname NOT IN (\'pg_catalog\',\'information_schema\') ORDER BY pg_relation_size(C.oid) DESC LIMIT 20;"',
"Server3" : 'PGPASSWORD=thule psql -d fm_db_Server3 -p 5452 -h 172.30.147.173  -U mmsuper -c "SELECT nspname || \'.\' || relname AS \"relation\", pg_size_pretty(pg_relation_size(C.oid)) AS \"size\" FROM pg_class C LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace) WHERE nspname NOT IN (\'pg_catalog\',\'information_schema\') ORDER BY pg_relation_size(C.oid) DESC LIMIT 20;"',
"Server4" : 'PGPASSWORD=thule psql -d fm_db_Server4 -p 5462 -h 172.30.147.173  -U mmsuper -c "SELECT nspname || \'.\' || relname AS \"relation\", pg_size_pretty(pg_relation_size(C.oid)) AS \"size\" FROM pg_class C LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace) WHERE nspname NOT IN (\'pg_catalog\',\'information_schema\') ORDER BY pg_relation_size(C.oid) DESC LIMIT 20;"',
"Server5" : 'PGPASSWORD=thule psql -d fm_db_Server5 -p 5472 -h 172.30.147.174  -U mmsuper -c "SELECT nspname || \'.\' || relname AS \"relation\", pg_size_pretty(pg_relation_size(C.oid)) AS \"size\" FROM pg_class C LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace) WHERE nspname NOT IN (\'pg_catalog\',\'information_schema\') ORDER BY pg_relation_size(C.oid) DESC LIMIT 20;"',
"Server6" : 'PGPASSWORD=thule psql -d fm_db_Server6 -p 5482 -h 172.30.147.174  -U mmsuper -c "SELECT nspname || \'.\' || relname AS \"relation\", pg_size_pretty(pg_relation_size(C.oid)) AS \"size\" FROM pg_class C LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace) WHERE nspname NOT IN (\'pg_catalog\',\'information_schema\') ORDER BY pg_relation_size(C.oid) DESC LIMIT 20;"',
"Server7" : 'PGPASSWORD=thule psql -d fm_db_Server7 -p 5492 -h 172.30.147.175  -U mmsuper -c "SELECT nspname || \'.\' || relname AS \"relation\", pg_size_pretty(pg_relation_size(C.oid)) AS \"size\" FROM pg_class C LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace) WHERE nspname NOT IN (\'pg_catalog\',\'information_schema\') ORDER BY pg_relation_size(C.oid) DESC LIMIT 20;"',
"Server8" : 'PGPASSWORD=thule psql -d fm_db_Server8 -p 5502 -h 172.30.147.175  -U mmsuper -c "SELECT nspname || \'.\' || relname AS \"relation\", pg_size_pretty(pg_relation_size(C.oid)) AS \"size\" FROM pg_class C LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace) WHERE nspname NOT IN (\'pg_catalog\',\'information_schema\') ORDER BY pg_relation_size(C.oid) DESC LIMIT 20;"',
"Server9" : 'PGPASSWORD=thule psql -d fm_db_Server9 -p 5512 -h 172.30.147.176  -U mmsuper -c "SELECT nspname || \'.\' || relname AS \"relation\", pg_size_pretty(pg_relation_size(C.oid)) AS \"size\" FROM pg_class C LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace) WHERE nspname NOT IN (\'pg_catalog\',\'information_schema\') ORDER BY pg_relation_size(C.oid) DESC LIMIT 20;"',
"Server10" : 'PGPASSWORD=thule psql -d fm_db_Server10 -p 5522 -h 172.30.147.176  -U mmsuper -c "SELECT nspname || \'.\' || relname AS \"relation\", pg_size_pretty(pg_relation_size(C.oid)) AS \"size\" FROM pg_class C LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace) WHERE nspname NOT IN (\'pg_catalog\',\'information_schema\') ORDER BY pg_relation_size(C.oid) DESC LIMIT 20;"',
"Server11" : 'PGPASSWORD=thule psql -d fm_db_Server11 -p 5532 -h 172.30.147.177  -U mmsuper -c "SELECT nspname || \'.\' || relname AS \"relation\", pg_size_pretty(pg_relation_size(C.oid)) AS \"size\" FROM pg_class C LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace) WHERE nspname NOT IN (\'pg_catalog\',\'information_schema\') ORDER BY pg_relation_size(C.oid) DESC LIMIT 20;"',
"Server12" : 'PGPASSWORD=thule psql -d fm_db_Server12 -p 5572 -h 172.30.147.177  -U mmsuper -c "SELECT nspname || \'.\' || relname AS \"relation\", pg_size_pretty(pg_relation_size(C.oid)) AS \"size\" FROM pg_class C LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace) WHERE nspname NOT IN (\'pg_catalog\',\'information_schema\') ORDER BY pg_relation_size(C.oid) DESC LIMIT 20;"',
"Server13" : 'PGPASSWORD=thule psql -d fm_db_Server13 -p 5582 -h 172.30.147.178  -U mmsuper -c "SELECT nspname || \'.\' || relname AS \"relation\", pg_size_pretty(pg_relation_size(C.oid)) AS \"size\" FROM pg_class C LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace) WHERE nspname NOT IN (\'pg_catalog\',\'information_schema\') ORDER BY pg_relation_size(C.oid) DESC LIMIT 20;"',
"Server14" : 'PGPASSWORD=thule psql -d fm_db_Server14 -p 5592 -h 172.30.147.178  -U mmsuper -c "SELECT nspname || \'.\' || relname AS \"relation\", pg_size_pretty(pg_relation_size(C.oid)) AS \"size\" FROM pg_class C LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace) WHERE nspname NOT IN (\'pg_catalog\',\'information_schema\') ORDER BY pg_relation_size(C.oid) DESC LIMIT 20;"',
"Server15" : 'PGPASSWORD=thule psql -d fm_db_Server15 -p 5602 -h 172.30.147.179  -U mmsuper -c "SELECT nspname || \'.\' || relname AS \"relation\", pg_size_pretty(pg_relation_size(C.oid)) AS \"size\" FROM pg_class C LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace) WHERE nspname NOT IN (\'pg_catalog\',\'information_schema\') ORDER BY pg_relation_size(C.oid) DESC LIMIT 20;"',
"Server16" : 'PGPASSWORD=thule psql -d fm_db_Server16 -p 5612 -h 172.30.147.179  -U mmsuper -c "SELECT nspname || \'.\' || relname AS \"relation\", pg_size_pretty(pg_relation_size(C.oid)) AS \"size\" FROM pg_class C LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace) WHERE nspname NOT IN (\'pg_catalog\',\'information_schema\') ORDER BY pg_relation_size(C.oid) DESC LIMIT 20;"',
"Server17" : 'PGPASSWORD=thule psql -d fm_db_Server17 -p 5622 -h 172.30.147.180  -U mmsuper -c "SELECT nspname || \'.\' || relname AS \"relation\", pg_size_pretty(pg_relation_size(C.oid)) AS \"size\" FROM pg_class C LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace) WHERE nspname NOT IN (\'pg_catalog\',\'information_schema\') ORDER BY pg_relation_size(C.oid) DESC LIMIT 20;"',
"Server18" : 'PGPASSWORD=thule psql -d fm_db_Server18 -p 5632 -h 172.30.147.180  -U mmsuper -c "SELECT nspname || \'.\' || relname AS \"relation\", pg_size_pretty(pg_relation_size(C.oid)) AS \"size\" FROM pg_class C LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace) WHERE nspname NOT IN (\'pg_catalog\',\'information_schema\') ORDER BY pg_relation_size(C.oid) DESC LIMIT 20;"',
"Server19" : 'PGPASSWORD=thule psql -d fm_db_Server19 -p 5642 -h 172.30.147.181  -U mmsuper -c "SELECT nspname || \'.\' || relname AS \"relation\", pg_size_pretty(pg_relation_size(C.oid)) AS \"size\" FROM pg_class C LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace) WHERE nspname NOT IN (\'pg_catalog\',\'information_schema\') ORDER BY pg_relation_size(C.oid) DESC LIMIT 20;"',
"Server20" : 'PGPASSWORD=thule psql -d fm_db_Server20 -p 5652 -h 172.30.147.181  -U mmsuper -c "SELECT nspname || \'.\' || relname AS \"relation\", pg_size_pretty(pg_relation_size(C.oid)) AS \"size\" FROM pg_class C LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace) WHERE nspname NOT IN (\'pg_catalog\',\'information_schema\') ORDER BY pg_relation_size(C.oid) DESC LIMIT 20;"',
"Server21" : 'PGPASSWORD=thule psql -d fm_db_Server21 -p 5662 -h 172.30.147.182  -U mmsuper -c "SELECT nspname || \'.\' || relname AS \"relation\", pg_size_pretty(pg_relation_size(C.oid)) AS \"size\" FROM pg_class C LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace) WHERE nspname NOT IN (\'pg_catalog\',\'information_schema\') ORDER BY pg_relation_size(C.oid) DESC LIMIT 20;"',
"Server22" : 'PGPASSWORD=thule psql -d fm_db_Server22 -p 5672 -h 172.30.147.182  -U mmsuper -c "SELECT nspname || \'.\' || relname AS \"relation\", pg_size_pretty(pg_relation_size(C.oid)) AS \"size\" FROM pg_class C LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace) WHERE nspname NOT IN (\'pg_catalog\',\'information_schema\') ORDER BY pg_relation_size(C.oid) DESC LIMIT 20;"',
"Server23" : 'PGPASSWORD=thule psql -d fm_db_Server23 -p 5682 -h 172.30.147.183  -U mmsuper -c "SELECT nspname || \'.\' || relname AS \"relation\", pg_size_pretty(pg_relation_size(C.oid)) AS \"size\" FROM pg_class C LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace) WHERE nspname NOT IN (\'pg_catalog\',\'information_schema\') ORDER BY pg_relation_size(C.oid) DESC LIMIT 20;"',
"Server24" : 'PGPASSWORD=thule psql -d fm_db_Server24 -p 5692 -h 172.30.147.183  -U mmsuper -c "SELECT nspname || \'.\' || relname AS \"relation\", pg_size_pretty(pg_relation_size(C.oid)) AS \"size\" FROM pg_class C LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace) WHERE nspname NOT IN (\'pg_catalog\',\'information_schema\') ORDER BY pg_relation_size(C.oid) DESC LIMIT 20;"',
"Server25" : 'PGPASSWORD=thule psql -d fm_db_Server25 -p 5702 -h 172.30.147.184  -U mmsuper -c "SELECT nspname || \'.\' || relname AS \"relation\", pg_size_pretty(pg_relation_size(C.oid)) AS \"size\" FROM pg_class C LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace) WHERE nspname NOT IN (\'pg_catalog\',\'information_schema\') ORDER BY pg_relation_size(C.oid) DESC LIMIT 20;"',
"Server26" : 'PGPASSWORD=thule psql -d fm_db_Server26 -p 5712 -h 172.30.147.184  -U mmsuper -c "SELECT nspname || \'.\' || relname AS \"relation\", pg_size_pretty(pg_relation_size(C.oid)) AS \"size\" FROM pg_class C LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace) WHERE nspname NOT IN (\'pg_catalog\',\'information_schema\') ORDER BY pg_relation_size(C.oid) DESC LIMIT 20;"',
"Server27" : 'PGPASSWORD=thule psql -d fm_db_Server27 -p 5722 -h 172.30.147.185  -U mmsuper -c "SELECT nspname || \'.\' || relname AS \"relation\", pg_size_pretty(pg_relation_size(C.oid)) AS \"size\" FROM pg_class C LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace) WHERE nspname NOT IN (\'pg_catalog\',\'information_schema\') ORDER BY pg_relation_size(C.oid) DESC LIMIT 20;"',
"Server28" : 'PGPASSWORD=thule psql -d fm_db_Server28 -p 5732 -h 172.30.147.185  -U mmsuper -c "SELECT nspname || \'.\' || relname AS \"relation\", pg_size_pretty(pg_relation_size(C.oid)) AS \"size\" FROM pg_class C LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace) WHERE nspname NOT IN (\'pg_catalog\',\'information_schema\') ORDER BY pg_relation_size(C.oid) DESC LIMIT 20;"',
"Server29" : 'PGPASSWORD=thule psql -d fm_db_Server29 -p 5809 -h 172.30.147.174  -U mmsuper -c "SELECT nspname || \'.\' || relname AS \"relation\", pg_size_pretty(pg_relation_size(C.oid)) AS \"size\" FROM pg_class C LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace) WHERE nspname NOT IN (\'pg_catalog\',\'information_schema\') ORDER BY pg_relation_size(C.oid) DESC LIMIT 20;"'
}


# Cleaning up Manager.
mgrState = subprocess.check_output('hagrp -state Manager_grp | grep \'ONLINE\|PARTIAL\' | sed \'s/STARTING//g;s/STOPPING//g\' | awk {\'print $4\'} | sed \'s/|//g\'' , shell=True).strip()
physicalBlade = subprocess.check_output('hagrp -state Manager_grp | grep ONLINE | awk {\'print $3\'}' , shell=True).strip()
if mgrState == "ONLINE":
        sys.stdout.write("Manager's online, proceeding in cleanup\n")
elif mgrState == "PARTIAL":
        sys.stdout.write("Manager's still partial, waiting\n")
        while mgrState == "PARTIAL":

                # Wait till finish
                toolbar_width = 20
                # setup progress toolbar
                sys.stdout.write("[%s]" % (" " * toolbar_width))
                sys.stdout.flush()
                sys.stdout.write("\b" * (toolbar_width+1)) # return to start of line, after '['

                for i in xrange(toolbar_width):
                        time.sleep(1) # do real work here
                        # update the bar
                        sys.stdout.write("-")
                        sys.stdout.flush()

                sys.stdout.write("]\n") # this ends the progress bar
                mgrState = subprocess.check_output('hagrp -state Manager_grp | grep \'PARTIAL\' | sed \'s/STARTING//g;s/STOPPING//g\' | awk {\'print $4\'} | sed \'s/|//g\'' , shell=True).strip()
                sys.stdout.write("Manager's still partial, waiting\n")
else: 
        sys.stdout.write("Manager's already offline, attempting online\n")
        physicalBlade = "HQ-EMM_PHY-01"
        os.system('hagrp -online Manager_grp -sys %s' % physicalBlade)
        mgrState = subprocess.check_output('hagrp -state Manager_grp | grep \'PARTIAL\' | sed \'s/STARTING//g;s/STOPPING//g\' | awk {\'print $4\'} | sed \'s/|//g\'' , shell=True).strip()
        while mgrState == "PARTIAL":

                # Wait till finish
                toolbar_width = 20
                # setup progress toolbar
                sys.stdout.write("[%s]" % (" " * toolbar_width))
                sys.stdout.flush()
                sys.stdout.write("\b" * (toolbar_width+1)) # return to start of line, after '['

                for i in xrange(toolbar_width):
                        time.sleep(1) # do real work here
                        # update the bar
                        sys.stdout.write("-")
                        sys.stdout.flush()

                sys.stdout.write("]\n") # this ends the progress bar
                mgrState = subprocess.check_output('hagrp -state Manager_grp | grep \'PARTIAL\' | sed \'s/STARTING//g;s/STOPPING//g\' | awk {\'print $4\'} | sed \'s/|//g\'' , shell=True).strip()
                sys.stdout.write("Manager's still partial, waiting\n")


# Access postgres db and acquire table info.
sys.stdout.write("Manager db table space before applying cleanup\n")
os.system('PGPASSWORD=thule psql -d mgrdb -p 5445 -h 172.30.147.166 -U mmsuper -c "SELECT nspname || \'.\' || relname AS \"relation\", pg_size_pretty(pg_relation_size(C.oid)) AS \"size\" FROM pg_class C LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace) WHERE nspname NOT IN (\'pg_catalog\',\'information_schema\') ORDER BY pg_relation_size(C.oid) DESC LIMIT 20;"')

# Wait till finish
toolbar_width = 3
# setup progress toolbar
sys.stdout.write("[%s]" % (" " * toolbar_width))
sys.stdout.flush()
sys.stdout.write("\b" * (toolbar_width+1)) # return to start of line, after '['

for i in xrange(toolbar_width):
        time.sleep(1) # do real work here
        # update the bar
        sys.stdout.write(".")
        sys.stdout.flush()

sys.stdout.write("]\n") # this ends the progress bar

# Truncating, re-indexing and vacuuming log entry tables.
sys.stdout.write('Truncating, reindexing and vacuuming log entry tables of Manager\n')
mgrQuery = "PGPASSWORD=thule psql -d mgrdb -p 5445 -h 172.30.147.166 -U mmsuper"
os.system('%s -c "truncate table mmsuper.mm_alarmlog;"' % mgrQuery)
os.system('%s -c "reindex table  mmsuper.mm_alarmlog;"' % mgrQuery)
os.system('%s -c "vacuum FULL mmsuper.mm_alarmlog;"' % mgrQuery)        

# Access postgres db and acquire table info.
sys.stdout.write("Manager db table space after applying cleanup\n")
os.system('PGPASSWORD=thule psql -d mgrdb -p 5445 -h 172.30.147.166 -U mmsuper -c "SELECT nspname || \'.\' || relname AS \"relation\", pg_size_pretty(pg_relation_size(C.oid)) AS \"size\" FROM pg_class C LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace) WHERE nspname NOT IN (\'pg_catalog\',\'information_schema\') ORDER BY pg_relation_size(C.oid) DESC LIMIT 20;"')

sys.stdout.write('Manager database cleaned...Starting servers database cleanup\n')

# Starting Servers databse cleanup.
for key in postgresDict:
        #server = ix(postgresDict, postgresDict, num)
        state = subprocess.check_output('hares -state %s | grep ONLINE | awk {\'print $4\'}' %key, shell=True)
        if state.strip() == "ONLINE":
                sys.stdout.write("%s's online, attempting offline\n" %key)
                os.system('hares -offline %s -sys %s' % (key,mapDict[key]))
                sys.stdout.write('Attempting offline %s on %s\n' % (key,mapDict[key]))
        else:
                sys.stdout.write("%s's already offline, proceeding to cleanup\n" %key)

                # If server's offline for some reason, acquire group info[blade] and and define it's mapDict value.
                mapDict[key] = subprocess.check_output('hagrp -state FM_%s_grp | grep PARTIAL | awk {\'print $3\'}' %key, shell=True).strip()
        while state.strip() == "ONLINE" :

                # Wait till finish
                toolbar_width = 40
                # setup progress toolbar
                sys.stdout.write("[%s]" % (" " * toolbar_width))
                sys.stdout.flush()
                sys.stdout.write("\b" * (toolbar_width+1)) # return to start of line, after '['

                for i in xrange(toolbar_width):
                        time.sleep(3) # do real work here
                        # update the bar
                        sys.stdout.write("-")
                        sys.stdout.flush()
                        state = subprocess.check_output('hares -state %s | grep ONLINE | awk {\'print $4\'}' %key, shell=True)
                        if state.strip() != "ONLINE":
                                break

                sys.stdout.write("O\n") # this ends the progress bar
                state = subprocess.check_output('hares -state %s | grep ONLINE | awk {\'print $4\'}' %key, shell=True)
                if state.strip() == "ONLINE":
                        sys.stdout.write("%s's still online, offline in progress\n" %key)
                else:
                        sys.stdout.write("%s became offline\n" %key)

        # Access postgres db and acquire table info.
        sys.stdout.write("%s db table space before applying cleanup\n" %key)
        os.system(postgres_status_Dict[key])

        # Wait till finish
        toolbar_width = 3
        # setup progress toolbar
        sys.stdout.write("[%s]" % (" " * toolbar_width))
        sys.stdout.flush()
        sys.stdout.write("\b" * (toolbar_width+1)) # return to start of line, after '['

        for i in xrange(toolbar_width):
                time.sleep(1) # do real work here
                # update the bar
                sys.stdout.write(".")
                sys.stdout.flush()

        sys.stdout.write("]\n") # this ends the progress bar

        # Truncating, re-indexing and vacuuming log entry tables.
        # for server in postgresDict:
        sys.stdout.write('Truncating, reindexing and vacuuming log entry tables of %s\n' % key)
        os.system('%s -c "truncate table  mmsuper.consolidatorlogentry;"' % postgresDict[key])
        os.system('%s -c "reindex table  mmsuper.consolidatorlogentry;"' % postgresDict[key])
        os.system('%s -c "vacuum FULL mmsuper.consolidatorlogentry;"' % postgresDict[key])
        os.system('%s -c "truncate table  mmsuper.loggedalarmentry;"' % postgresDict[key])
        os.system('%s -c "reindex table  mmsuper.loggedalarmentry;"' % postgresDict[key])
        os.system('%s -c "vacuum FULL mmsuper.loggedalarmentry;"' % postgresDict[key])


        # Access postgres db and acquire table info.
        sys.stdout.write("%s db table space after applying cleanup\n" %key)
        os.system(postgres_status_Dict[key])

        sys.stdout.write('Database cleaned. Attempting online %s on %s\n' % (key,mapDict[key]))
        os.system('hares -online %s -sys %s' % (key,mapDict[key]))
sys.stdout.write('Cleanup completed!\n')
