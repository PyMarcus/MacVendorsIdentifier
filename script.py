#!/usr/bin/env python
from scapy.all import *
from mac_vendor_lookup import MacLookup, BaseMacLookup


BaseMacLookup.cache_path = "vendor.txt"
_mac = MacLookup()


def sniffer():
    sniff(iface="wlp3s0mon", prn=scanner, monitor=True)

def parser_mac():
    _mac.update_vendors()


def find_mac(mac):
    return _mac.lookup(mac)


def scanner(packet):
    if packet.haslayer(Dot11):
        if packet.type == 0 and packet.subtype == 8:
            print("DEVICE FINDED")
            print("SSID: {0}\nMAC: {1}\nCREATOR: {2}".format(packet.info.decode(),
                                                             packet.addr2,
                                                             find_mac(str(packet.addr2).strip())))
            print('-' * 30)

if __name__ == '__main__':
    #sniffer()
    sniffer()
    find_mac("ec:c0:1b:9c:77:e0")
