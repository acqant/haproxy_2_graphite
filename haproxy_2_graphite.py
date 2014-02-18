#!/usr/bin/env python
import sys
from datetime import datetime, date, timedelta, time
import subprocess
import pprint
from socket import socket

pp = pprint.PrettyPrinter(indent=4)

#
# SETTINGS
#
CARBON_SERVER = '127.0.0.1'		# Your graphite server
CARBON_PORT = 2003			# Your graphite port
LOG_STATS=1				# Log the stats sent to graphite to a text file to see what is being sent
log_path="/tmp/haproxy_stats"		# The file to log the stats too
test=1					# Turns off sending to graphite
one_levels=['creative', 'TOPLEVEL'] 	# What to report on. TOPLEVEL is '/' in the log line.  All others are ignored.
#################################


################################################################
# SUBS
################################################################
def rollup(): 
        lines=[]
        sock = socket()
        f = open("%s/%s" % (log_path, schema), 'a')
        try:
                sock.connect( (CARBON_SERVER,CARBON_PORT) )
        except:
                print "Couldn't connect to %(server)s on port %(port)d, is carbon-agent.py running?" % { 'server':CARBON_SERVER, 'port':CARBON_PORT }
                sys.exit(1)
	for key in server:
		#
		# Aborted
		#
                if key == 'aborted':
                        lines.append("%s.aborted %s %d" % (schema, server[key], unix_time))
                        continue
		#
		# hits per sec or min
		#
		if key == 'hps':
			if int(delta) == 60:
				key='hpm'
				num=server['hps'] 
				lines.append("%s.hpm %s %d" % (schema, num, unix_time))
				continue
			else:
				num=server[key] / int(delta)
				lines.append("%s.hps %s %d" % (schema, num, unix_time))
				continue
		#
		# one level URL
		#
		if key[0] == 'one_level':
			num=server[key[0], key[1]] / int(delta)
			lines.append("%s.%s %s %d" % (schema, key[1], num, unix_time))
			continue
                if key[1] == 'lines':
                        hps=server[key[0],'lines'] / int(delta)
                        name=key[0] + '.hps'
                        lines.append("%s.%s %s %d" % (schema, name , hps, unix_time))

                if key[1] == 'total_Tq':
                        avg=server[key[0], 'total_Tq'] / server[key[0], 'lines']
                        lines.append("%s.%s.avgTq %s %d" % (schema, key[0], avg, unix_time))
                if key[1] == 'total_Tw':
                        avg=server[key[0], 'total_Tw'] / server[key[0], 'lines']
                        lines.append("%s.%s.avgTw %s %d" % (schema, key[0], avg, unix_time))
                if key[1] == 'total_Tc':
                        avg=server[key[0], 'total_Tc'] / server[key[0], 'lines']
                        lines.append("%s.%s.avgTc %s %d" % (schema, key[0], avg, unix_time))
                if key[1] == 'total_Tr':
                        avg=server[key[0], 'total_Tr'] / server[key[0], 'lines']
                        lines.append("%s.%s.avgTr %s %d" % (schema, key[0], avg, unix_time))
                if key[1] == 'total_Tt':
                        avg=server[key[0], 'total_Tt'] / server[key[0], 'lines']
                        lines.append("%s.%s.avgTt %s %d" % (schema, key[0], avg, unix_time))

                if key[1] == 'max_Tq':
                        lines.append("%s.%s.maxTq %s %d" % (schema, key[0], server[key], unix_time))
                if key[1] == 'max_Tw':
                        lines.append("%s.%s.maxTw %s %d" % (schema, key[0], server[key], unix_time))
                if key[1] == 'max_Tc':
                        lines.append("%s.%s.max_Tc %s %d" % (schema, key[0], server[key], unix_time))
                if key[1] == 'max_Tr':
                        lines.append("%s.%s.maxTr %s %d" % (schema, key[0], server[key], unix_time))
                if key[1] == 'max_Tt':
                        lines.append("%s.%s.maxTt %s %d" % (schema, key[0], server[key], unix_time))

        message = '\n'.join(lines) + '\n' #all lines must end in a newline
        if test == 0:
        	if LOG_STATS == 1:
			f.write("sending message.....")
			f.write(message)
                sock.sendall(message)
                #print message
        else:
                print message
                #f.write(message)
        f.write("sent.\n")


def run_total(total, new):
        if (backend_srv, total) in server:
                server[(backend_srv, total)]= server[(backend_srv, total)] + int(new)
        else:
                server[(backend_srv, total)]=int(new)

def max(max, new):
        if (backend_srv, max) in server:
                if int(new) > server[(backend_srv, max)]:
                        server[(backend_srv, max)]=int(new)
        else:
                server[(backend_srv, max)]=int(new)

################################################################################
#MAIN
################################################################################
try:
        only_for=sys.argv[1]
        delta=sys.argv[2]
        check_vip=1
except:
        pass
td=timedelta(seconds=+int(delta))
dtFirstLine=None
server={}
for line in sys.stdin:
        #
        # Parse Line
        #
	if 'GET' not in line and 'POST' not in line:
		print "Not a GET or a POST? "
		print line
		continue
        split_array=line.split()				#split_array	-- 	original split of line
        log_time=split_array[6]					#time		--	the time of the event
        backend=split_array[8].split("/")			#the backend	--	creative_backend/creative01
        backend_srv=backend[1]					#the adserver	--	creative01
        stats=split_array[9].split("/")				#the stats	-- 	26/0/0/125/255
	url_array=line.split("}")				#the URL element
	url=url_array[1].split()
	ols=url[1].split("?")
	one_level=ols[0].replace('/', '')
	if one_level == '':
		one_level='TOPLEVEL'
	
        host=split_array[17].replace('{',' ').replace('|',' ').split()[0].split('.')
	#print host
	if len(host) > 3 or len(host) < 2:			#has to be a hostname not 209.81
		print 'ship: ' + host
		continue
        schema=host[0] + '.' +  host[1]				#graphite schema
	try:
                if check_vip == 1:
                        #print schema, only_for
                        if schema != only_for:
                                print "skipping " + schema, only_for
                                continue
        except: 
                pass
	#
	#Get details of connections
	#
        Tq=stats[0]
        Tw=stats[1]
        Tc=stats[2]
        Tr=stats[3]
        Tt=stats[4]
        if (Tw == "-1" or Tq == '-1' or Tc == '-1' or Tr == '-1' or Tt =='-1'):
                if 'aborted' in server:
                        #f.write("ABORTED in SERVER %s" % server['aborted'])
                        server['aborted']= server['aborted'] + 1
                else:
                        server['aborted']=1
                continue
        dtLine = datetime.strptime(log_time, "[%d/%b/%Y:%H:%M:%S.%f]")
	int_unix_time=dtLine.strftime("%s")
        unix_time=int(int_unix_time)

        #
        # Running Total
        #
        run_total('total_Tq', Tq)
        run_total('total_Tc', Tc)
        run_total('total_Tw', Tw)
        run_total('total_Tr', Tr)
        run_total('total_Tt', Tt)
        #
        # MAX's
        #
        max('max_Tq', Tq)
        max('max_Tc', Tc)
        max('max_Tw', Tw)
        max('max_Tr', Tr)
        max('max_Tt', Tt)
        #
        # Everything total
        #
        if 'hps' in server:
                server['hps']=server['hps'] + 1
        else:
                server['hps']=server['hps'] = 1

        if (backend_srv,'lines') in server:
                server[(backend_srv,'lines')]=server[(backend_srv,'lines')] + 1
        else:
                server[(backend_srv,'lines')]= 1

	if one_level in one_levels: 
		try:
			server['one_level', one_level] = server['one_level',one_level] + 1	
		except KeyError:
			server['one_level', one_level] =   1
	#else:
		#print "not reporting on: " + line
        if dtFirstLine is None:
                dtFirstLine=dtLine
                dtStop=dtFirstLine + td
        if dtLine > dtStop:
                dtFirstLine=None
                import time
                now=int(time.time())
		#pp.pprint(server)
                rollup()
                server={}
##  6   Tq '/' Tw '/' Tc '/' Tr '/' Tt*                       10/0/30/69/109
#"Tq" total time in milliseconds spent waiting for the client to send a full HTTP request, not counting data.
#"Tc" total time in milliseconds spent waiting for the connection to establish to the final server, including retries.
#"Tw" total time in milliseconds spent waiting in the various queues.
#"Tr" total time in milliseconds spent waiting for the server to send  a full HTTP response, not counting data.
#"Tt" is the total time in milliseconds elapsed between the accept and the last close
# 12   actconn '/' feconn '/' beconn '/' srv_conn '/' retries*    1/1/1/1/0

#f.write (server + Tq + "\n")
#0[   'Aug',
#1    '28',
#2    '12:49:37',
#3    '10.10.106.202',
#4    'haproxy[28233]:',
#5    '174.62.109.81:54907',
#6    '[28/Aug/2012:12:49:37.487]',
#7    'frontend name',
#8    'backend name',
#9    '26/0/0/125/255',
#10    '200',
#11   '287',
#12    '-',
#13    '-',
#14    '----',
#15   '12/12/10/10/0',
#    '0/0',
#    'acl name',
#    '(iPad;',
#    'CPU',
#    'OS',
#    '5_1_1',
#    'like',
#    'Mac',
#    'OS',
#    'X)',
#    'App}',
#    '"GET',
#    'url'
#    'HTTP/1.1"']
