# SOF-ELK Command-Line Activities Mapping

This document maps SOF-ELK command-line activities to web interface actions.

## Log Ingestion Operations

### File Upload and Processing
- **Command-line activity**: Placing files in `/logstash/*/` directories
- **Web interface action**: File upload interface with directory selection

### NetFlow Processing
- **Command-line activity**: `nfdump2sof-elk.sh -r /path/to/netflow/ -w /logstash/nfarch/output.txt`
- **Web interface action**: Form to upload NetFlow files and specify parameters

### AWS VPC Flow Processing
- **Command-line activity**: `aws-vpcflow2sof-elk.sh -r /path/to/aws-vpcflow/ -w /logstash/nfarch/output.txt`
- **Web interface action**: Form to upload AWS VPC Flow files and specify parameters

### Azure VPC Flow Processing
- **Command-line activity**: `azure-vpcflow2sof-elk.py -r /path/to/gcp-vpcflow/ -w /logstash/nfarch/output.txt`
- **Web interface action**: Form to upload Azure VPC Flow files and specify parameters

## System Management Operations

### Clear Elasticsearch Database
- **Command-line activity**: `/usr/local/sbin/sof-elk_clear.py -i [index_name]`
- **Web interface action**: Form to select indices to clear with confirmation dialog

### Update SOF-ELK Configuration
- **Command-line activity**: `/usr/local/sbin/sof-elk_update.sh`
- **Web interface action**: Button to trigger update with progress indicator

## System Information Operations

### View Loaded Data
- **Command-line activity**: Checking Kibana dashboards
- **Web interface action**: Dashboard overview showing loaded data counts and types

### View System Status
- **Command-line activity**: Various system commands
- **Web interface action**: System status dashboard with key metrics

## Important System Paths

- Log directories: `/logstash/*/`
  - `/logstash/aws/`
  - `/logstash/azure/`
  - `/logstash/gcp/`
  - `/logstash/gws/`
  - `/logstash/httpd/`
  - `/logstash/kape/`
  - `/logstash/kubernetes/`
  - `/logstash/microsoft365/`
  - `/logstash/nfarch/`
  - `/logstash/passivedns/`
  - `/logstash/plaso/`
  - `/logstash/syslog/`
  - `/logstash/zeek/`

- Configuration files: `/etc/logstash/conf.d/*.conf`
- SOF-ELK repository: `/usr/local/sof-elk/*`
- System commands:
  - `/usr/local/sbin/sof-elk_clear.py`
  - `/usr/local/sbin/sof-elk_update.sh`
  - `nfdump2sof-elk.sh`
  - `aws-vpcflow2sof-elk.sh`
  - `azure-vpcflow2sof-elk.py`


