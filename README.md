#Test program for the NBE pellet burner UDP protocol
A client that can connect to a scotte V7/V13 controller, and a test server that simulates a controller box.

##Client

<pre>
   usage: client.py [-h] [-v] [-a ADDRESS] [-p PASSWORD] [-n] function payload

   positional arguments:
     function
     payload

   optional arguments:
     -h, --help            show this help message and exit
     -v, --verbose
     -a ADDRESS, --address ADDRESS
                           controller address, autodiscovered if omitted
     -p PASSWORD, --password PASSWORD
                           the controller does not verify the password yet
                           so it can be omitted
     -n, --noseqnum        use with firmware older than 7.0614

function  command
   1        Read setup value
   2        Set setup value
   3        Read setup min,max,default,decimal
   4        Read operating data
   5        Read advanced data
   6        Read consumption data
   7        Read chart data
   8        Read event log
   9        Read info messages
   10       Read available programs
   11       Read barbeque data

examples:
   read all boiler settings, function: 1 payload: boiler.*
   write setting, function: 2 payload: boiler.diff_over=5

setup groups:
boiler.* hot_water.* regulation.* weather.* oxygen.* cleaning.* hopper.* fan.* auger.* ignition.* pump.* sun.* vacuum.* misc.* alarm.* manual.* bbq_smoke.* bbq_rotation.* bbq_grill.* bbq_meat.* bbq_afterburner.* bbq_div.*

</pre>

##Server

<pre>
   usage: server.py [-h] [-s] [-H HOST] [-p PASSWORD] [-n]

   optional arguments:
     -h, --help            show this help message and exit
     -H HOST, --host HOST  default is 0.0.0.0
     -p PASSWORD, --password PASSWORD
     -n, --noseqnum
</pre>

