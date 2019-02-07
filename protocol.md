Protocol frame structure
========================

| Request field    | bytes | Details                       |
|------------------|-------|-------------------------------|
| app_id           |    12 | string                        |
| controller id    |     6 | string                        |
| encrypted        |     1 | ' '=No, '*'=RSA, '-'=xtea     |
| start            |     1 | STX=2                         |
| function         |     2 | ascii function code number    |
| seqnum           |     2 | ascii sequence number         |
| pincode          |    10 | ascii, spaces when unencrypted|
| timestamp        |    10 | ascii seconds since 01.01.1970|
| extra            |     4 | future use                    |
| payloadsize      |     3 | ascii number                  |
| payload          |     n |                               |
| end              |     1 | EOT=4                         |

| Response  field  | bytes | Details                       |
|------------------|-------|-------------------------------|
| app_id           |    12 | string                        |
| controller id    |     6 | string                        |
| start            |     1 | STX=2                         |
| function         |     2 | ascii function code number    |
| seqnum           |     2 | ascii sequence number         |
| response code    |     1 |                               |
| payloadsize      |     3 | ascii number                  |
| payload          |     n |                               |
| end              |     1 | EOT=4                         |

| Function codes   | Function                |
|------------------|-------------------------|
|                0 | Discovery               |
|                1 | Read setup value        |
|                2 | Set setup value         |
|                3 | Read setup range        |
|                4 | Read operating data     |
|                5 | Read advanced data      |
|                6 | Read consumption data   |
|                7 | Read chart data         |
|                8 | Read event log          |
|                9 | Read info               |
|               10 | Read avail. programs    |

## Read setup values

Setup values are read in groups or one by one using function code *1*.
Set payload to group/* to read all settings in the group.
Set payload to group/setting to read one setting.

| Available setting groups |
|--------------------------|
| boiler                   |
| hot_water                |
| regulation               |
| weather                  |
| weather2                 |
| oxygen                   |
| cleaning                 |
| hopper                   |
| fan                      |
| auger                    |
| ignition                 |
| pump                     |
| sun                      |
| vacuum                   |
| misc                     |
| alarm                    |
| manual                   |


