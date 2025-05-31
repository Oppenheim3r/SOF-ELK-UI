# SOF-ELK Web Interface

This project provides a Django-based web interface for SOF-ELK (Security Operations and Forensics Elasticsearch, Logstash, Kibana) VM. It allows users to control all command-line activities through a graphical user interface.

## Features

- Dashboard with system status overview
- Log file upload and management
- **NEW:** View and delete uploaded log files (single or bulk)
- NetFlow, AWS VPC Flow, and Azure VPC Flow processing
- Elasticsearch indices management
- SOF-ELK configuration update
- System status monitoring

## Installation

1. Clone this repository to your SOF-ELK VM
2. Set up a Python virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```
   pip install django
   ```
4. Run migrations:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```
5. Create a superuser (optional):
   ```
   python manage.py createsuperuser
   ```
6. Run the development server:
   ```
   python manage.py runserver 0.0.0.0:8000
   ```
7. Access the web interface at http://<your-vm-ip>:8000

## System Requirements

- SOF-ELK VM (Ubuntu 24.04 base)
- Python 3.11+
- Django 5.2+

## Project Structure

- `dashboard/`: Main Django app for SOF-ELK operations
- `static/`: CSS and JavaScript files
- `templates/`: HTML templates
- `sof_elk_ui/`: Django project settings

## SOF-ELK System Paths

This web interface respects all SOF-ELK system paths and command-line tools:

- Log directories: `/logstash/*/`
- Configuration files: `/etc/logstash/conf.d/*.conf`
- SOF-ELK repository: `/usr/local/sof-elk/*`
- System commands:
  - `/usr/local/sbin/sof-elk_clear.py`
  - `/usr/local/sbin/sof-elk_update.sh`
  - `nfdump2sof-elk.sh`
  - `aws-vpcflow2sof-elk.sh`
  - `azure-vpcflow2sof-elk.py`

## Security Considerations & Permissions

- The web interface runs with the same permissions as the user running the Django server (e.g., `elk_user`).
- **File Operations:**
  - **Uploading:** The user running the server needs write permissions to the target `/logstash/*` subdirectories (e.g., `/logstash/syslog/2024/`, `/logstash/httpd/`).
  - **Deleting:** The user running the server needs write permissions to the specific files within the `/logstash/*` subdirectories to delete them.
  - **Processing (NetFlow, etc.):** The user needs write permissions to `/logstash/nfarch/` to save the processed output files.
- **Command Execution:**
  - For operations requiring elevated privileges (like `/usr/local/sbin/sof-elk_update.sh`), the user running the server must have passwordless `sudo` access configured for that specific command.
- In production, consider using a proper web server like Nginx or Apache with WSGI and carefully manage user permissions.

## License

This project is provided as-is with no warranty. Use at your own risk.
