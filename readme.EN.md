The content below is translated from Vietnamese by ChatGPT

---

# F5 Academy 2025 - NetOps  

## Lab topology 

To reduce our carbon footprint and save the planet, we have decided not to use images throughout this guide. So please pay close attention.  

```  
+--------------+         +-------------+          +------------------+  
|              |         |             |          |                  |  
|  Jump host   | <-----> |   BIG-IP    | <------> |  Web/DNS Server  |  
|              |         |             |          |                  |  
+--------------+         +-------------+          +------------------+  
                            ^       ^  
                            |       |  
                            v       v  
                 +------------+   +------------+  
                 |            |   |            |  
                 |    AST     |   |    ELK     |  
                 |            |   |            |  
                 +------------+   +------------+  
```  

The model includes:  
- A BIG-IP device pre-configured with WAF and DNS services.  
- A Jump Host acting as a client machine for testing services. It includes essential tools such as `dig`, `curl`, and even `nikto`.  
- A Web/DNS Server serving as the backend for WAF and DNS services on BIG-IP. It runs two containers: `juiceshop` (Webapp, port 3000) and `unbound` (DNS, port 53).  
- AST: A machine intended for users to install the Application Study Tool. It comes pre-installed with a `git` client, `docker` engine, and `docker-compose`.  
- ELK: An Elasticsearch + Logstash + Kibana system. Only Elasticsearch and Kibana are pre-installed as two containers. Your task is to install and configure Logstash, integrating it into the ELK stack.  

## Lab 0 - Initial Configuration Check  

Before usage, the BIG-IP device needs to be licensed. Please contact the instructor or a teaching assistant in the lab for licensing information.  

In the **Access** menu, select **TMUI** to access the graphical management interface. The administrator account is:  
- **Username**: `admin`  
- **Password**: `f5!Demo.admin`  

Activate the license manually, then reboot the device (`System  ››  Configuration : Device : General`, click **Reboot**).  

After rebooting, check the service configuration by accessing the BIG-IP web management interface (select **TMUI** or **WEBGUI** in **Access**):  
- Check **Node** and **Pool** information.  
- Check **Virtual Server** details (note the virtual address).  
- Check **WAF Policy** and **Event Log**.  

Access the **Web Shell** on the Jump Host and verify services on BIG-IP using the following commands:  
- **For web service**: `curl http://10.1.10.9/`  
- **For DNS service**: `dig @10.1.10.9 vnexpress.net`  

For the web service, you can also access it through BIG-IP via **Access → JUICESHOP** to view it in the browser.  

To check **Kibana** and **Elasticsearch**, access **Access → Kibana** on the ELK machine. The login credentials are:  
- **Username**: `admin`  
- **Password**: `f5!Demo.admin`  

On the AST machine (accessible via Web Shell), only Docker engine, Git client, and some basic tools are installed at the beginning of the lab.  

## Lab 1 - Installing the Application Study Tool  

On the AST machine, go to **Access → Web Shell** to open the Bash shell, then follow the instructions at [this link](https://github.com/f5devcentral/application-study-tool).  

The BIG-IP management IP in this lab environment is `10.1.1.9`. You can collect additional data from modules like **ASM** and **DNS**.  

Once installed, access **Grafana** via the AST machine's **Access menu**. The system may take a few minutes to start collecting enough data for visualization. Meanwhile, you can generate traffic by accessing Web and DNS services.  

## Lab 2 - Installing ELK  

The lab environment is pre-configured with two containers: **Elasticsearch** and **Kibana**, integrated together. A new admin account `admin:f5!Demo.admin` has been created for immediate use.  

If you're interested in how these two containers were set up, check out:  
- [Elasticsearch Docker Setup](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html)  
- [Kibana Docker Setup](https://www.elastic.co/guide/en/kibana/current/docker.html)  
- [Logstash Docker Setup](https://www.elastic.co/guide/en/logstash/current/docker.html)  

ELK can be accessed in two ways:  
- **Command line (Bash Shell)** via **Access → Web Shell**  
- **Kibana GUI** via **Access → Kibana**  

Now, let's install **Logstash** on the ELK machine. The connection model between the three components and the log sources is as follows:  

```  
+------------------+  
|  Log sources     | ---> | Logstash | ---> | Elasticsearch | <--- | Kibana |  
+------------------+       +---------+       +-------------+       +--------+  
```  

- **Log sources**: BIG-IP sends logs via Syslog to Logstash (ports `5140` and `5141` for WAF and DNS logs).  
- **Logstash**: Processes logs, formats them into JSON, and forwards them to Elasticsearch via HTTPS (`port 9200`).  
- **Kibana**: A web application providing visualization and analytics for Elasticsearch data (`port 5601`).  

From the Bash Shell on ELK, run:  

```  
git clone https://github.com/biennt/f5academy2025.git  
```  

Review the configuration files in `pipeline/`:  
- `output.conf` → Configures Logstash to write data to Elasticsearch.  
- `f5waf.conf` → Defines input for WAF logs from BIG-IP.  
- `f5dns.conf` → Defines input for DNS logs from BIG-IP.  

To start the Logstash container:  

```  
docker run -d --name logstash --net host -v /f5academy2025/pipeline:/usr/share/logstash/pipeline -e XPACK_MONITORING_ENABLED=false --restart=unless-stopped logstash:8.17.3  
```  

Monitor Logstash startup:  

```  
docker logs -f logstash  
```  

If no errors appear, proceed with configuring BIG-IP to send logs.  

## Lab 3 - Configuring F5 BIG-IP (WAF) to Send Logs to ELK  

On BIG-IP:  
1. **Create a new Logging Profile** under `Security ›› Event Logs : Logging Profiles ›› Create New Logging Profile...`  
2. Set:  
   - **Storage Destination** → Remote Storage  
   - **Logging Format** → Key-Value Pairs (Splunk)  
   - **IP Address** → `10.1.30.8`  
   - **Port** → `5140`  
3. Apply the profile to `Local Traffic ›› Virtual Servers : Virtual Server List ›› vshttp`.  

Generate logs:  
- **Access JUICESHOP** via BIG-IP.  
- **Use curl on the Jump Host**: `curl http://10.1.10.9/`.  

Verify logs in Kibana under **Stack Management → Index Management**.  

## Lab 4 - Configuring F5 BIG-IP (DNS) to Send Logs to ELK  

On BIG-IP:  
1. **Create a Pool** (`elkpooldns`) with Member IP `10.1.30.8`, Port `5141`.  
2. **Create a Log Destination** (`elklogdestdns`).  
3. **Create a Log Publisher** (`elklogpubdns`).  
4. **Apply it to DNS Logging Profile** (`dnslogprofile`).  

Generate DNS queries from the Jump Host:  

```  
dig @10.1.10.9 facebook.com  
dig @10.1.10.9 google.com  
```  

Check logs in Kibana.  

## Lab 5 - Configuring F5 BIG-IP to Send System Logs to ELK  

On BIG-IP:  
1. **Create a Pool** (`elkpoolltm`) with Member IP `10.1.30.8`, Port `5142`.  
2. **Create a Log Destination and Publisher**.  
3. **Configure Log Filters**.  

Test by stopping and restarting the JuiceShop container:  

```  
docker stop juiceshop  
docker start juiceshop  
```  

Verify logs in Kibana.  

---

Congratulations! 🚀
