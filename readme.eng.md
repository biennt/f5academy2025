# F5 Academy 2025 - NetOps

## Connection Model in the Lab

To reduce our carbon footprint and save the Earth, we decided not to use any images in this guide. So, please pay close attention to the details.

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

The above model includes:
- The pre-configured BIG-IP device with WAF and DNS services.
- The Jump host, which acts as a client to test the services, includes tools like dig, curl, and even nikto.
- The Web/DNS Server is the backend server for the WAF and DNS services running on BIG-IP. It runs two containers: juiceshop (Webapp, port 3000) and unbound (DNS, port 53).
- AST: A machine where you are expected to install the Application Study Tool. It already has a git client, docker engine, and docker compose installed.
- ELK: The Elasticsearch + Logstash + Kibana system. Only Elasticsearch and Kibana are installed and set up as two containers. The rest is for you to install and configure Logstash and integrate it into the ELK system.

## Lab 0 - Review Current Configurations

Before use, the BIG-IP device needs to be licensed. Please contact the instructor or teaching assistant in the classroom for this information.

In the Access section, select TMUI to enter the graphical admin interface. The admin account is:
- Username: admin
- Password: f5!Demo.admin

Activate the license manually, then reboot the device (```System  ››  Configuration : Device : General```, click on ```Reboot```).

After rebooting, check the service configuration information by accessing the BIG-IP web admin interface (select TMUI or WEBGUI in the Access section):
- Check information about Nodes, Pools
- Check information about virtual servers (note the virtual address)
- Check WAF Policy, Event logs

Access the Jump host's Web Shell and check the services on BIG-IP by running:
- For web services: run ```curl http://10.1.10.9/```
- For DNS services: run ```dig @10.1.10.9 vnexpress.net```

For web services, you can also access it from BIG-IP via Access --> JUICESHOP to view it in the browser.

Check Kibana and Elasticsearch services by accessing them via Access --> Kibana on the ELK machine. The admin account is:
- Username: admin
- Password: f5!Demo.admin

On the AST machine (access via Web Shell), when the lab is first created, it only has the docker engine, git client, and some basic tools.

## Lab 1 - Install Application Study Tool

On the AST machine, select Web Shell in Access to enter bash shell, and then follow the instructions at [this link](https://github.com/f5devcentral/application-study-tool).

The admin IP address of BIG-IP in this lab environment is 10.1.1.9. You can collect additional data from modules like ASM, DNS.

After installation, access the Grafana interface through the Access menu of the AST machine. The system will need a few minutes to start collecting enough data to draw the graphs. During this time, you can access the Web and DNS services to generate traffic.

## Lab 2- Install ELK
The lab environment has two pre-installed containers: Elasticsearch and Kibana, integrated with each other. A new admin account ```admin:f5!Demo.admin``` has also been created and is ready for use.

If you're interested in how these two containers are installed, you can refer to the following guides:
- https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html
- https://www.elastic.co/guide/en/kibana/current/docker.html

And install Logstash:
- https://www.elastic.co/guide/en/logstash/current/docker.html

ELK can be accessed in two ways:
- Command-line interface (bash shell), go to Access --> Web Shell
- The graphical interface of Kibana, go to Access --> Kibana

In this section, we will begin installing Logstash on the ELK server. If you notice from the ```docker images``` command, you will see that we have downloaded the Logstash image corresponding to the version of Elasticsearch and Kibana (both are version 8.17.3).

For clarity, the connection model between these three components and the log source is as follows:
```
                                                                                                          
+------------------+                                                                                       
|                  |         +------------------+                                                          
|  Log sources     |         |                  |                                                          
|                  |-------->|                  |         +------------------+         +------------------+
+------------------+         |                  |         |                  |         |                  |
+------------------+         |     Logstash     |         |  Elasticsearch   |<--------|      Kibana      |
|                  |-------->|                  |         |                  |         |                  |
|  Log sources     |         |                  |         +------------------+         +------------------+
|                  |         +------------------+                                                          
+------------------+                                                                                       
                           
```
- Log sources are the log origins, such as the BIG-IP device, which acts as a client sending logs via syslog to Logstash (we will use ports 5140 and 5141 for logs from WAF and DNS respectively).
- Logstash is the component to be installed here. It is responsible for recognizing logs, converting them into a format that Elasticsearch can understand (JSON), and sending them to Elasticsearch over https:// on port 9200.
- Kibana is the web application that provides an interface to interact with Elasticsearch. It can even do more than that, such as drawing dashboards, graphs, performing investigations, etc. Administrators access Kibana via http:// on port 5601.

From the ELK bash shell interface, run the following command:
```
git clone https://github.com/biennt/f5academy2025.git
```
Check the contents of the files in the `pipeline/` folder:
- `output.conf` contains information for Logstash to write data into Elasticsearch
- `f5waf.conf` defines the input for log sources from F5 BIG-IP WAF
- `f5dns.conf` defines the input for log sources from F5 BIG-IP DNS
- ... and other files if present.

Note the following information:
- Hosts: contains at least one address of the Elasticsearch master server
- Index: the index name will be created/updated with data on Elasticsearch
- User and Password: credentials used by Logstash to access Elasticsearch

There is also the filter section, which helps Logstash recognize the log format and know how to convert it to JSON. You can refer to helper tools for creating grok filters such as:
- Create filters online: https://grokdebugger.com/
- Use Kibana to create filters: https://www.elastic.co/guide/en/kibana/current/xpack-grokdebugger.html

Now, initialize the Logstash container, with all log source directive files located in the `/f5academy2025/pipeline` folder:
```
docker run -d --name logstash --net host -v /f5academy2025/pipeline:/usr/share/logstash/pipeline -e XPACK_MONITORING_ENABLED=false --restart=unless-stopped logstash:8.17.3
```

Check the Logstash startup process with the command:
```
docker logs -f logstash
```
If there are no errors, we can proceed to configure the log forwarding from the F5 WAF on BIG-IP.

## Lab 3- Configure F5 BIG-IP (WAF) to Forward Logs to ELK

This section will use the file `pipeline/f5waf.conf` on the ELK machine. Please check the contents of this file first.

From the BIG-IP Host, go to TMUI/WEBGUI, after logging in, choose  ```Security  ››  Event Logs : Logging Profiles  ››  Create New Logging Profile...```

Name the profile ```remote_log```, choose ```Application Security```, and then:
- In ```Storage Destination```, choose Remote Storage
- In ```Logging Format```, choose Key-Value Pairs (Splunk)
- In ```IP Address```, enter 10.1.30.8
- In ```Port```, enter 5140 and click ```Add```
- In ```Maximum Entry Length```, choose 64K
- In ```Request Type```, select All requests

Then, apply this profile by going to ```Local Traffic  ››  Virtual Servers : Virtual Server List  ››  vshttp```, select ```Security --> Policies```

In the ```Log Profile``` section, add ```remote_log``` and then click ```Update```

Generate some requests to the web service to generate logs:
- From the BIG-IP Host, go to Access and select JUICESHOP
- From the Jump host, go to Access and select Web Shell, then use the `curl` command to create traffic, for example: ```curl http://10.1.10.9/```

Go to Kibana, select ```Stack Management --> Index Management``` and you should see a new index starting with ```f5waf-``` followed by the date format.

From this interface, select ```Data Views``` (in Kibana), click ```Create data view```. 

Name the data view `f5waf`, and the index pattern should be `f5waf-*`, then click ```Save data view to Kibana```

Finally, view the logs by clicking the three horizontal lines menu (sometimes called the hamburger menu) at the top left corner of the window and selecting Discover. Choose `f5waf` as the Data View if it hasn’t been selected automatically.

If you see log entries, it means that the logs from BIG-IP WAF have been successfully forwarded to ELK.

If you see ```_grokparsefailure``` in the log, it means there was an error related to the format that Logstash could not parse, usually due to a wrong filter (grok filter). You can check the file `f5waf.conf`, in the section ```filter --> grok --> match```, and use the Grok Debugger tool to check and adjust. But generally, by this point, the task is 99% complete.

**Congratulations!**

The instructor will guide you through some operations and basic features in the ```Discover``` screen.

As a WAF device administrator, what do you care about when reviewing access logs? Here are some suggestions on fields to consider:
- `ip_client`: The client's IP address (Layer 4), which might not be the actual user’s IP if it has passed through one or more proxies before reaching the WAF device.
- `x_forwarded_for_header_value`: The client's IP address recorded in the HTTP header (X-Forward-For) inserted by a proxy device upstream. This is a Layer 7 value, and whether to trust it depends on the context. The instructor will explain this in more detail.
- `dest_ip` and `dest_port` are the IP address and service port of the server handling the request on BIG-IP (representing the application).
- `policy_name`: The name of the policy being applied.
- `request_status`: The status of the request (could be alerted, passed, or blocked).
- `violations`: Types of violations for that request.
- `request`: The specific content of the request (starting with method, followed by URI and headers).
- `violation_rating`: The severity of the violation, rated from 1 to 5. The higher the number, the more severe the violation. If you notice, in the Logstash configuration file, I converted this value from string to Integer so we can perform comparison operations in Elasticsearch/Kibana. For example, you can filter requests with a violation rating of 3 or higher to easily analyze them.

At this point, you should consider creating a dashboard to monitor some key metrics.

## Lab 4- Configure F5 BIG-IP (DNS) to Forward Logs to ELK

This section will use the file `pipeline/f5dns.conf` on the ELK machine. Please check the contents of this file first.

On the BIG-IP Host, go to TMUI/WEBGUI, then navigate to ```Local Traffic  ››  Pools : Pool List  ››  New Pool...``` to create a pool for forwarding logs:
- Name: Enter ```elkpooldns```
- Member: Enter Node Name and Address as ```10.1.30.8```, Service Port as ```5141```, then click Add (This lab only has one Logstash instance, if there are more, you can add them here).

Finally, click Finished to complete creating the pool named ```elkpooldns```.

Go to ```System  ››  Logs : Configuration : Log Destinations```, click ```Create```
- Name: ```elklogdestdns```
- Type: Remote High-Speed Log
- Pool Name: ```elkpooldns```

Click Finished to complete.

Go to ```System  ››  Logs : Configuration : Log Publishers```, click ```Create```
- Name: ```elklogpubdns```
- Destinations: ```elklogdestdns```

Go to ```DNS  ››  Delivery : Profiles : Other : DNS Logging```, click ```Create```
- Name: ```dnslogprofile```
- Log Publisher: ```elklogpubdns```
- Select Include Query ID and Log Responses (basically select all the information you want to log).

Go to ```DNS  ››  Delivery : Profiles : DNS```, select the profile named ```dnsprofile``` (this profile was pre-configured for DNS Caching, which is why we could test the DNS resolution service in Lab 0).

In ```dnsprofile```, under ```Logging and Reporting```:
- Logging: Enabled
- Logging Profile: ```dnslogprofile```

Click Update to complete.

From the Jump host, you can use the `dig` command to query DNS and generate logs.

For example:
```
dig @10.1.10.9 facebook.com
dig @10.1.10.9 google.com
dig @10.1.10.9 vnexpress.net
dig @10.1.10.9 dantri.com
```

Now, hold your breath! Go to Kibana and check:

Go to ```Stack Management --> Index Management```, do you see an index starting with `f5dns-` followed by the year-month-day format? If so, create a data view to view it in Discover.

In ```Data Views```, click ```Create data view```
- Name: f5dns
- Index pattern: f5dns-*

Then click ```Save data view to Kibana```. Check the data view `f5dns` in the ```Discover``` screen.

## Lab 5- Configure F5 BIG-IP (DNS) to Forward System Logs to ELK

This section will use the file `pipeline/f5ltm.conf` on the ELK machine. Please check the contents of this file first.

On the BIG-IP Host, go to TMUI/WEBGUI, then go to ```Local Traffic  ››  Pools : Pool List  ››  New Pool...``` to create a pool for forwarding system logs:
- Name: Enter ```elkpoolltm```
- Member: Enter Node Name and Address as ```
