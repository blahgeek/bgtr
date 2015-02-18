#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by i@BlahGeek.com at 2015-02-17

import sys
from netfilterqueue import NetfilterQueue
from scapy.all import IPv6, ICMPv6TimeExceeded
from scapy.sendrecv import __gen_send  # `send` is fucking slow!
from scapy.config import conf

socket = conf.L3socket()

PREFIX = '2001:470:1f05:42c:2015::'
ROUTES = [PREFIX + hex(x).split('x')[-1] for x in range(1, 17)]

def handle(inpkt):
    pkt = IPv6(inpkt.get_payload())
    print 'Packet from', pkt.src, 'hop limit =', pkt.hlim
    hlim = pkt.hlim - 1
    if hlim < len(ROUTES):
        inpkt.drop()
        tosend = IPv6(src=ROUTES[hlim], dst=pkt.src) / ICMPv6TimeExceeded() / pkt
        __gen_send(socket, tosend)
    else:
        inpkt.accept()

if __name__ == '__main__':
    queue = 1
    if len(sys.argv) > 1:
        queue = int(sys.argv[1])

    print 'Binding queue', queue

    nfqueue = NetfilterQueue()
    nfqueue.bind(queue, handle)
    try:
        print 'Listening...'
        nfqueue.run()
    except KeyboardInterrupt:
        pass
