haproxy_2_graphite
==================

This python script will read haproxy logs for a number of seconds 
and then roll up some interesting stats and send them to graphite.

It will pull the hostname out from haproxy log and use that as the
graphite schema.

For example, this line will send stats to graphite for schema www.mysite.com
Feb 18 12:40:45 10.10.106.143 haproxy[7030]: 166.147.120.168:15305 [18/Feb/2014:12:40:45.627] creative_frontend_crlb03 creative_backend_crlb03/cr2_a 1/0/0/1/33 302 147 - - ---- 66/66/19/0/0 0/0 {www.mysite.com|Mozilla/5.0 (Linux; U; Android 2.3.6; en-us; SAMSU} "GET /creative?param=value HTTP/1.1"

It will report on:
* The hits per second or hits per minute for the entire schema
* The same but for each URL
* The same but for each host
* As well as some max and total times from haproxy stats ( Tq,Tr,Tw,Tc,Tt )



You first need to setup graphite and create the top level schema.
If you site is www.mysite.com that is your top level schema.
Example usage

To get started, set test=1, enter your one_level URLs you want to report on
and then tail, or cat, a haproxy log file to the script.  Specify the schema name
and the time to rollup the stats.  If traffic is slow make the rollup time 10 or more seconds.
If you need to specify hits per minute use 60.

tail -F ./haproxy_file | ./haproxy_2_graphite.py matching_name time_2_report_on

What you should see for www.mysite.com for a 2 second rollup time
#
IMPORTANT:  Your rollup time should match your graphite storage settings.
#
tail -F ./myfile | ./haproxy_2_graphite.py www.mysite.com 2

www.mysite.com.hps 293 1392749389
www.mysite.com.cr2_b.avgTt 215 1392749389
www.mysite.com.cr3_a.avgTq 19 1392749389
www.mysite.com.cr4_b.avgTt 248 1392749389
www.mysite.com.cr4_b.maxTq 1211 1392749389
www.mysite.com.cr1_a.maxTt 2099 1392749389
www.mysite.com.cr5_a.maxTr 1136 1392749389
www.mysite.com.cr3_a.maxTt 2048 1392749389
www.mysite.com.cr5_b.maxTw 0 1392749389
www.mysite.com.cr3_a.max_Tc 1 1392749389
www.mysite.com.cr1_a.avgTc 0 1392749389
www.mysite.com.cr1_b.avgTq 15 1392749389
www.mysite.com.cr4_b.avgTc 0 1392749389
www.mysite.com.cr4_a.avgTc 0 1392749389
www.mysite.com.cr4_b.maxTr 2003 1392749389
www.mysite.com.cr1_a.maxTq 259 1392749389
www.mysite.com.cr1_b.max_Tc 1 1392749389
www.mysite.com.cr5_a.maxTw 0 1392749389
www.mysite.com.cr3_b.hps 33 1392749389
www.mysite.com.cr5_b.maxTr 2004 1392749389
www.mysite.com.cr4_a.maxTq 1459 1392749389
www.mysite.com.cr1_b.avgTt 261 1392749389



