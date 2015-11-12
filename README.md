#NBE V13 test program
A client that can connect to a scotte V13, and a server that simulates a V13 controller box.

##client

<pre>
   usage: client.py [-h] [-v] [-a ADDRESS] [-p PASSWORD] function payload

   positional arguments:
     function
     payload

   optional arguments:
     -h, --help            show this help message and exit
     -v, --verbose
     -a ADDRESS, --address ADDRESS
                           controller address, autodiscovered if omitted
     -p PASSWORD, --password PASSWORD

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

</pre>

##Server

<pre>
   usage: server.py [-h] [-s] [-H HOST] [-p PASSWORD]

   optional arguments:
     -h, --help            show this help message and exit
     -s, --silent
     -H HOST, --host HOST  default is 0.0.0.0
     -p PASSWORD, --password PASSWORD
</pre>

