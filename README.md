# he-ddns-updater
Script to update Hurrican Electric DDNS


Updates dns A and AAAA entries on Hurricane Electric dDNS, if the current dns entry doesn't
equal the current ip address on [https://ifconfig.co/](https://ifconfig.co/)

Expects a config file named `config.yaml` in the same directory with the
following content:

```
- domain: some.domain
  key_v4: NOTSORANDOMKEY
  key_v6: NOTSORANDOMKEY
```


### Dependencies:

```
PyYAML 
requests 
dnspython
```  
