# he-ddns-updater
Script to update Hurrican Electric DDNS


Updates dns entry on Hurricane Electric dDNS, if the current dns entry doesn't
equal the current ip address on [https://ifconfig.co/](https://ifconfig.co/)

Expects a config file named `config.yaml` in the same directory with the
following content:

```
- domain: some.domain
  key: NOTSORANDOMKEY
```


### Dependencies:

```
PyYAML 
requests 
dnspython
```  
