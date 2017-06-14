# ping-exporter
Prometheus Ping exporter

A simple python script call fping(require version 4.0) and parse the output to allow prometheus scrape it. And you can generate a nice graph with Grafana easily.

![alt text](https://ifconfig.xyz/file/ping.png)

For Debian user, you can get the fping deb file from http://ftp.debian.org/debian/pool/main/f/fping/fping_4.0-1_armhf.deb

PS: The script is working fine with > 40 ping target in a PI 3B.

Append the following in prometheus's config
```
  - job_name: 'ping-exporter'
    scrape_interval: 60s
    metrics_path: /probe
    params:                                         
         prot: ['4']                  
    target_groups:
      - targets:
          - www.ifconfig.xyz
          - www.google.com
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
        replacement: ${1}
      - source_labels: [__param_target]
        regex: (.*)
        target_label: instance
        replacement: ${1}
      - source_labels: []
        regex: .*
        target_label: __address__
        replacement: <Your exporter IP>:8085  
```
