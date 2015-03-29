#Client

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

#Server

   usage: server.py [-h] [-s] [-H HOST] [-p PASSWORD]

   optional arguments:
     -h, --help            show this help message and exit
     -s, --silent
     -H HOST, --host HOST  default is 0.0.0.0
     -p PASSWORD, --password PASSWORD
