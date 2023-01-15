import pysnmp
import string
import time as t
from pysnmp.entity.rfc3413.oneliner import cmdgen
from itertools import product

SNMP_PASSWORD = "snmppassword" # your SNMP password
SNMP_HOST = "192.168.0.1" # your host for managing with SNMP
PORT = 161  # default SNMP port for Amicon
USER = "authOnlyUser" # default SNMP user for Amicon
timeout = 0.0001
retries = 1

# Some oids from AMICON-FPSU-MIB.my for requests 
oids_dict = {'.1.3.6.1.4.1.37249.2.1.13.1.2.1': ['Сбросов пакетов драйвером, из-за переполнения reorder', '_1'],
            '.1.3.6.1.4.1.37249.2.1.13.1.2.2': ['Сбросов пакетов драйвером, из-за переполнения reorder', '_2'],
            '.1.3.6.1.4.1.37249.2.1.13.1.3.1': ['Сбросов пакетов драйвером, из-за переполнения очередей обработки', '_1'],
            '.1.3.6.1.4.1.37249.2.1.13.1.3.2': ['Сбросов пакетов драйвером, из-за переполнения очередей обработки', '_2'],
            '.1.3.6.1.4.1.37249.2.1.13.1.4.1': ['Сбросов пакетов из-за отсутствия памяти для приёма на сетевой карте', '_1'],
            '.1.3.6.1.4.1.37249.2.1.13.1.4.2': ['Сбросов пакетов из-за отсутствия памяти для приёма на сетевой карте', '_2'],
            '.1.3.6.1.4.1.37249.2.1.13.1.5.1': ['Общее количество сброшенных пакетов по всем счётчикам dpdkX<>', '_1'],
            '.1.3.6.1.4.1.37249.2.1.13.1.5.2': ['Общее количество сброшенных пакетов по всем счётчикам dpdkX<>', '_2'],
            '.1.3.6.1.4.1.37249.2.1.13.1.6.1': ['Counts the number of receive packets with CRC errors', '_1'],
            '.1.3.6.1.4.1.37249.2.1.13.1.6.2': ['Counts the number of receive packets with CRC errors', '_2'],
            '.1.3.6.1.4.1.37249.2.1.13.1.7.1': ['Number of MAC short packet discard packets received', '_1'],
            '.1.3.6.1.4.1.37249.2.1.13.1.7.2': ['Number of MAC short packet discard packets received', '_2'],
            '.1.3.6.1.4.1.37249.2.1.13.1.8.1': ['Number of packets with receive length errors', '_1'],
            '.1.3.6.1.4.1.37249.2.1.13.1.8.2': ['Number of packets with receive length errors', '_2'],
            '.1.3.6.1.4.1.37249.2.1.13.1.9.1': ['Receive Undersize Error', '_1'],
            '.1.3.6.1.4.1.37249.2.1.13.1.9.2': ['Receive Undersize Error', '_2'],
            '.1.3.6.1.4.1.37249.2.1.13.1.10.1': ['Receive Oversize Error', '_1'],
            '.1.3.6.1.4.1.37249.2.1.13.1.10.2': ['Receive Oversize Error', '_2'],
            '.1.3.6.1.4.1.37249.2.1.13.1.11.1': ['Illegal Byte Error Count', '_1'],
            '.1.3.6.1.4.1.37249.2.1.13.1.11.2': ['Illegal Byte Error Count', '_2'],
            '.1.3.6.1.4.1.37249.2.1.13.1.12.1': ['Error Byte Count', '_1'],
            '.1.3.6.1.4.1.37249.2.1.13.1.12.2': ['Error Byte Count', '_2'],
            '.1.3.6.1.4.1.37249.2.1.13.1.13.1': ['Number of receive fragment errors that have bad CRC', '_1'],
            '.1.3.6.1.4.1.37249.2.1.13.1.13.2': ['Number of receive fragment errors that have bad CRC', '_2'],
            '.1.3.6.1.4.1.37249.2.1.13.1.14.1': ['Count the number of packets with good Ethernet CRC and bad FC CRC', '_1'],
            '.1.3.6.1.4.1.37249.2.1.13.1.14.2': ['Count the number of packets with good Ethernet CRC and bad FC CRC', '_2'],
            '.1.3.6.1.4.1.37249.2.1.13.1.15.1': ['Number of packets received to valid FCoE contexts while their user buffers are exhausted', '_1'],
            '.1.3.6.1.4.1.37249.2.1.13.1.15.2': ['Number of packets received to valid FCoE contexts while their user buffers are exhausted', '_2'],
            '.1.3.6.1.4.1.37249.2.1.13.1.16.1': ['Counts the number of packets received in which RX_ER was asserted by the PHY', '_1'],
            '.1.3.6.1.4.1.37249.2.1.13.1.16.2': ['Counts the number of packets received in which RX_ER was asserted by the PHY', '_2'],
            '.1.3.6.1.4.1.37249.2.1.13.1.17.1': ['Counts the number of receive packets with alignment errors', '_1'],
            '.1.3.6.1.4.1.37249.2.1.13.1.17.2': ['Counts the number of receive packets with alignment errors', '_2'],
            '.1.3.6.1.4.1.37249.2.1.13.1.18.1': ['Number of packets sent by the host but discarded by the MAC', '_1'],
            '.1.3.6.1.4.1.37249.2.1.13.1.18.2': ['Number of packets sent by the host but discarded by the MAC', '_2'],
            '.1.3.6.1.4.1.37249.2.1.13.1.100.1': ['Успешно принятых пакетов сетевой картой', '_1'],
            '.1.3.6.1.4.1.37249.2.1.13.1.100.2': ['Успешно принятых пакетов сетевой картой', '_2']
        }  
        

def execute(host, port, user, auth_key, timeout, retries, oid, community='private'):
    security_model = cmdgen.UsmUserData(user, auth_key)
    errorIndication, errorStatus, errorIndex, varBinds = cmdgen.CommandGenerator().getCmd(security_model, cmdgen.UdpTransportTarget((host, port), timeout=timeout, retries=retries), oid)
    code = "{0}-{1}".format(errorStatus, errorIndex)
    if not errorIndication:
        mesg = varBinds
    else:
        mesg = errorIndication
    return  code, mesg, varBinds
    
    
def snmp_request():
    with open("Log.csv", 'a+', encoding='cp1251') as f:
        f.write(f'Timestamp;')
        for oid, description in oids_dict.items():
            f.write(f'{description[0] + description[1]};')
        f.write('\n')
        f.close()
    count = 0
    while True: #CTRL-C for stoping skript
        with open("Log.csv", 'a+', encoding='cp1251') as f:
            timestamp = t.strftime("%d.%m.%y %H:%M")
            f.write(f'{timestamp};')
            for oid, description in oids_dict.items():
                code, mesg, varBinds = execute(SNMP_HOST, PORT, USER, SNMP_PASSWORD, timeout, retries, oid)
                snmp_value = str(varBinds[-1])
                f.write(f'{snmp_value[int(snmp_value.rfind(" ")): len(snmp_value)]};')
                t.sleep(0.1)
            f.write('\n')
            f.close()
        count += 1
        print(count)
        t.sleep(300) # timeout for request, may be changed
        

if __name__ == "__main__":
    snmp_request()
