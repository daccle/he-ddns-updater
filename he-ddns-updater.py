#!/usr/bin/env python3
'''
he-ddns-updater.py

Updates dns entry on Hurricane Electric dDNS, if the current dns entry doesn't
equal the current ip address on https://ifconfig.co/

Expects a config file named config.yaml in the same directory with the
following content:

- domain: some.domain
  key: NOTSORANDOMKEY

Dependencies:

PyYAML       >=   5.4.1
requests     >=   2.25.1
dnspython    >=   2.1.0

MIT License

Copyright (c) 2023 Daniel Clerc <mail@clerc.eu>

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

# enforce IPv4 to get IPv4 ip address from ifconfig.co
requests.packages.urllib3.util.connection.HAS_IPV6 = False


def main(CONFIG):
   # get my current ip
   r = requests.get(r'https://ifconfig.co/json')
   MYIP = r.json()['ip']
   logging.debug(f"MYIP: {MYIP}")
   
   try:
       with open(CONFIG, "r") as configfile:
           data = yaml.load(configfile, Loader=yaml.FullLoader)
           logging.debug("Opening config successful")
   
       DOMAIN = data[0]['domain']
       KEY = data[0]['key']
   
       logging.debug(f'DOMAIN: {DOMAIN}')
       logging.debug(f'KEY: {KEY}')
   except KeyError:
       logging.warning("Config file in wrong format")
       sys.exit(1)
   except FileNotFoundError:
       logging.warning("No config file. Place config.yaml in current working directory.")
       sys.exit(1)
   
   for i in data:
       DOMAIN = i['domain']
       KEY = i['key']
   
       # get the current IP for DOMAIN on nameserver
       dns.resolver.override_system_resolver(resolver="ns1.he.net")
       answer = dns.resolver.resolve(DOMAIN, 'A')
       CURRENT_IP_ON_NS = answer[0].to_text()
       dns.resolver.restore_system_resolver()
       logging.debug(f"CURRENT_IP_ON_NS: {CURRENT_IP_ON_NS}")
       if not CURRENT_IP_ON_NS == MYIP:
           URL = f'https://dyn.dns.he.net/nic/update?hostname={DOMAIN}&password={KEY}&myip={MYIP}'
           r = requests.get(URL)
           logging.debug(f"IP update performed. Server answer{r.status_code}")
       else:
           logging.debug("MYIP equals CURRENT_IP_ON_NS, no update needed.")

if __name__ == "__main__":
    main(CONFIG)
