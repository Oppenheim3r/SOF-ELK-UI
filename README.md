
# SOF-ELK Web Interface

This project is meant to be an add on to the amazing SOF-ELK VM created by [@philhagen](https://github.com/philhagen/sof-elk/wiki/Virtual-Machine-README)  not a standalone tool. I built this Django based web interface specifically to be cloned and run inside the SOF-ELK VM itself. The idea is simple: give users a graphical UI to help upload, manage, and process log files without needing to mess with the command line every time.

I struggled a lot with uploading and managing files on SOF-ELK over SSH. It was clunky, especially when dealing with large log sets or constantly switching file types. So I built this to make my life easier and figured others might find it helpful too, which is why I’m sharing it with the community.
And yes, I used AI to help put this together.

## What It Does

- A simple dashboard to keep an eye on system status
- Upload and manage log files directly from the browser
- **New Feature:** View and delete uploaded log files (individually or in bulk)
- Process NetFlow, AWS VPC Flow, and Azure VPC Flow logs
- Manage Elasticsearch indices from the UI
- Update SOF-ELK configurations easily
- Monitor the system’s health

## 🛠 How to Install

## Make sure you are running on root while doing all of this 

1. Clone this repo inside your SOF-ELK VM.
    
``` git clone https://github.com/Oppenheim3r/SOF-ELK-UI.git```
   

3. Install the required dependencies:

   ```bash
   pip3 install django
   ```

3. Run the migrations:

   ```bash
   python3 manage.py makemigrations
   python3 manage.py migrate
   ```

4. (Optional) Create an admin user:

   ```bash
   python3 manage.py createsuperuser
   ```

5. Start the development server:

   ```bash
   python3 manage.py runserver 0.0.0.0:8000
   ```

6. Access the web interface via your browser at:  
   `http://<your-vm-ip>:8000`

> **Note:** I personally ran into an issue accessing Django from my host machine — whether I used NAT or a custom bridged adapter, I just couldn’t reach it.  
> So here’s what I did: I forwarded port `8080` to `8000` inside the SOF-ELK VM using iptables. This way, Django thinks I’m hitting it locally on `127.0.0.1`.

Here’s how I set that up:

```bash
sudo iptables -t nat -A PREROUTING -p tcp --dport 8080 -j REDIRECT --to-port 8000
sudo iptables -t nat -A OUTPUT -p tcp --dport 8080 -j REDIRECT --to-port 8000
```

Then just run:

```bash
python manage.py runserver 0.0.0.0:8000
```

To make these iptables rules stick after a reboot:

```bash
sudo apt install iptables-persistent
sudo netfilter-persistent save
```

Now I can simply open `http://<vm-ip>:8080` from my host machine, and Django behaves like I'm accessing it via `127.0.0.1`.

##  Requirements
- Python 3.11+
- Django 5.2+



##  System Paths in SOF-ELK

The web UI respects the original SOF-ELK paths and CLI tools:

- Log dirs: `/logstash/*/`
- Configs: `/etc/logstash/conf.d/*.conf`
- Core repo: `/usr/local/sof-elk/*`
- System tools used:
  - `/usr/local/sbin/sof-elk_clear.py`
  - `/usr/local/sbin/sof-elk_update.sh`
  - `nfdump2sof-elk.sh`
  - `aws-vpcflow2sof-elk.sh`
  - `azure-vpcflow2sof-elk.py`

## Note 

## The following are not working for now , and I will be fixing them later 
#NetFlow Processing
Command-line activity: nfdump2sof-elk.sh -r /path/to/netflow/ -w /logstash/nfarch/output.txt
Web interface action: Form to upload NetFlow files and specify parameters
#AWS VPC Flow Processing
Command-line activity: aws-vpcflow2sof-elk.sh -r /path/to/aws-vpcflow/ -w /logstash/nfarch/output.txt
Web interface action: Form to upload AWS VPC Flow files and specify parameters
#Azure VPC Flow Processing
Command-line activity: azure-vpcflow2sof-elk.py -r /path/to/gcp-vpcflow/ -w /logstash/nfarch/output.txt
Web interface action: Form to upload Azure VPC Flow files and specify parameters

## Permissions 

- The Django app runs with the same privileges as the user starting the server (e.g., `elk_user`).
- **File Uploads & Deletion:** That user must have write permissions to relevant `/logstash/*` subdirectories.
- **Log Processing (NetFlow, etc.):** Requires write access to `/logstash/nfarch/`.
- **Privileged Commands:** For stuff like `sof-elk_update.sh`, make sure the Django server user has **passwordless sudo** access specifically for that command.


