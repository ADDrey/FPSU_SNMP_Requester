# FPSU_SNMP_Requester
Program for making SNMP Request to "ПАК ФПСУ-IP" with using MIB-base.


AMICON-FPSU-MIB.my - mib base from site [Amicon](https://amicon.ru/download.php)

fpsu_snmp_requester.py - completed
mib_vase_parser.py - not completed

## Using

In the file [fpsu_snmp_requester.py](./fpsu_snmp_requester.py) change next:

    SNMP_PASSWORD = "snmppassword" # your SNMP password
    SNMP_HOST = "192.168.0.1" # your host for managing with SNMP
  
You can change timeout for request to your FPSU in next sting:

    t.sleep(300) # timeout for request, may be changed
