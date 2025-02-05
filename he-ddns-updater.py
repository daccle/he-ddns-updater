#!/usr/bin/env python3
'''
he-ddns-updater.py

Updates dns entry on Hurricane Electric dDNS, if the current dns entry doesn't
equal the current ip address on https://ifconfig.co/

Expects a config file named config.yaml in the same directory with the
following content:

- domain: some.domain
  key_v4: NOTSORANDOMKEY
  key_v6: NOTSORANDOMKEY

Dependencies:

PyYAML       >=   5.4.1
requests     >=   2.25.1
dnspython    >=   2.1.0

MIT License

Copyright (c) 2025 Daniel Clerc <mail@clerc.eu>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import requests
import dns.resolver
import yaml
import logging
import sys

CONFIG = "/home/pi/he-ddns-updater/config.yaml"

logging.basicConfig(stream=sys.stderr, level=logging.WARN)


def main(CONFIG):
   # get my current IPv6
   r = requests.get(r'https://ifconfig.co/json')
   MYIPv6 = r.json()['ip']
   logging.debug(f"MYIPv6: {MYIPv6}")
   
   # get my current IPv4
   # enforce IPv4 to get IPv4 ip address from ifconfig.co
   requests.packages.urllib3.util.connection.HAS_IPV6 = False
   r = requests.get(r'https://ifconfig.co/json')
   MYIPv4 = r.json()['ip']
   logging.debug(f"MYIPv4: {MYIPv4}")
   
   try:
       with open(CONFIG, "r") as configfile:
           data = yaml.load(configfile, Loader=yaml.FullLoader)
           logging.debug("Opening config successful")
   
       DOMAIN = data[0]['domain']
       KEYv4 = data[0]['key_v4']
       KEYv6 = data[0]['key_v6']
   except KeyError:
       logging.warning("Config file in wrong format")
       sys.exit(1)
   except FileNotFoundError:
       logging.warning("No config file. Place config.yaml in current working directory.")
       sys.exit(1)
   
   for i in data:
       DOMAIN = i['domain']
       KEYv4 = i['key_v4']
       KEYv6 = i['key_v6']
       
       logging.debug(f'DOMAIN: {DOMAIN}')
       logging.debug(f'KEYv4: {KEYv4}')
       logging.debug(f'KEYv6: {KEYv6}')
   
       # IPv4
       # get the current IPv4 for DOMAIN on nameserver
       dns.resolver.override_system_resolver(resolver="ns1.he.net")
       answer = dns.resolver.resolve(DOMAIN, 'A')
       CURRENT_IPv4_ON_NS = answer[0].to_text()
       dns.resolver.restore_system_resolver()
       logging.debug(f"CURRENT_IPv4_ON_NS: {CURRENT_IPv4_ON_NS}")
       if not CURRENT_IPv4_ON_NS == MYIPv4:
           URL = f'https://dyn.dns.he.net/nic/update?hostname={DOMAIN}&password={KEYv4}&myip={MYIPv4}'
           r = requests.get(URL)
           logging.debug(f"IPv4 update performed. Server answer{r.status_code}")
       else:
           logging.debug("MYIPv4 equals CURRENT_IPv4_ON_NS, no update needed.")
       
       # IPv6
       # get the current IPv6 for DOMAIN on nameserver
       dns.resolver.override_system_resolver(resolver="ns1.he.net")
       answer = dns.resolver.resolve(DOMAIN, 'AAAA')
       CURRENT_IPv6_ON_NS = answer[0].to_text()
       dns.resolver.restore_system_resolver()
       logging.debug(f"CURRENT_IPv6_ON_NS: {CURRENT_IPv6_ON_NS}")
       if not CURRENT_IPv6_ON_NS == MYIPv6:
           URL = f'https://dyn.dns.he.net/nic/update?hostname={DOMAIN}&password={KEYv6}&myip={MYIPv6}'
           r = requests.get(URL)
           logging.debug(f"IPv6 update performed. Server answer{r.status_code}")
       else:
           logging.debug("MYIPv6 equals CURRENT_IPv6_ON_NS, no update needed.")

if __name__ == "__main__":
    main(CONFIG)
