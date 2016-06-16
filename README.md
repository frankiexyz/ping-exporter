# ping-exporter
Prometheus Ping exporter

Install pyping
```
pip install pyping
```

Append the following in prometheus's config
```
  - job_name: 'ping-exporter'
    scrape_interval: 60s
    metrics_path: /
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
        replacement: <Your exporter IP>:9095  
```
