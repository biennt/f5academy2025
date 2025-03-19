# F5 Academy 2025 - NetOps

## Mô hình kết nối trong lab

Để giảm dấu chân carbon và cứu trái đất, chúng tôi quyết định sẽ không sử dụng ảnh trong toàn bộ hướng dẫn này. Vì vậy mong bạn đọc chú ý thật kỹ.

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

Mô hình trên gồm có:
- Thiết bị BIG-IP đã cấu hình sẵn dịch vụ WAF và DNS
- Jump host đóng vai trò như một máy client để test dịch vụ. Trong đó có các công cụ cần thiết như dig, curl hay thậm chí cả nikto
- Web/DNS Server là backend server cho các dịch vụ WAF và DNS thực hiện trên BIG-IP. Nó chạy 2 containers là juiceshop (Webapp, port 3000) và unbound (DNS, port 53)
- AST: là máy dự kiến để các bạn tự cài Application Study Tool vào đó. Nó đã có sẵn git client, docker engine và docker compose
- ELK: là hệ thống Elasticsearch + Logstash + Kibana. Mới chỉ có Elasticsearch và Kibana được cài đặt và setup dưới dạng 2 container. Việc còn lại cho bạn là cài đặt và cấu hình Logstash, tích hợp nó vào thành ELK

## Lab 0 - Đi một vòng kiểm tra các cấu hình hiện tại

Trước khi sử dụng, thiết bị BIG-IP cần được kích hoạt license. Hãy liên hệ với giảng viên hoặc trợ giảng có mặt trong phòng học để có thông tin này.

Trong mục Access, chọn TMUI để vào giao diện quản trị đồ họa. Tài khoản quản trị là:
- Username: admin
- Password: f5!Demo.admin

Kích hoạt license theo chế độ Manual, sau đó khởi động lại thiết bị (```System  ››  Configuration : Device : General```, bấm vào ```Reboot```)

Sau khi khởi động lại, kiểm tra các thông tin cấu hình dịch vụ bằng cách truy cập vào giao diện quản trị web của thiết bị BIG-IP (chọn TMUI hoặc WEBGUI trong mục Access):
- Kiểm tra thông tin về Node, Pool
- Kiểm tra thông tin về virtual server (lưu ý địa chỉ virtual address)
- Kiểm tra về WAF Policy, Event log

Truy cập Web Shell vào Jump host, kiểm tra dịch vụ trên BIG-IP bằng cách:
- Đối với dịch vụ web: gõ lệnh ```curl http://10.1.10.9/```
- Đối với dịch vụ DNS: gõ lệnh ```dig @10.1.10.9 vnexpress.net```

Đối với dịch vụ web, có thể truy cập từ BIG-IP qua mục Access --> JUICESHOP để xem ngay tại trình duyệt.

Kiểm tra dịch vụ Kibana và Elasticsearch bằng cách truy cập qua mục Access --> Kibana trên máy ELK. Tài khoản quản trị là:
- Username: admin
- Password: f5!Demo.admin

Trên máy AST (truy cập qua Web Shell) lúc vừa khởi tạo lab mới chỉ có docker engine, git client và một số phương tiện cơ bản

## Lab 1 - Cài đặt Application Study Tool

Trên máy AST, mục Access chọn Web Shell để vào bash shell, từ đó làm theo hướng dẫn tại [link này](https://github.com/f5devcentral/application-study-tool).

Địa chỉ IP quản trị của BIG-IP trong môi trường lab này là 10.1.1.9. Bạn có thể thu thập dữ liệu thêm từ các module như ASM, DNS.

Sau khi cài đặt xong, vào giao diện Grafana thông qua menu Access của máy AST. Hệ thống cần vài phút để có thể bắt đầu nhận đủ dữ liệu để vẽ các đồ thị. Trong lúc đó, bạn có thể truy cập các dịch vụ Web, DNS để phát sinh lưu lượng.

## Lab 2- Cài đặt ELK

Môi trường lab đã cài đặt sẵn 2 containers: Elasticsearch và Kibana, tích hợp chúng với nhau. Một tài khoản quản trị mới là ```admin:f5!Demo.admin``` cũng đã được tạo để sẵn sàng thao tác.

Nếu bạn quan tâm cách thức cài đặt 2 containers này, có thể tham khảo 2 hướng dẫn sau:
- https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html
- https://www.elastic.co/guide/en/kibana/current/docker.html

Và cài đặt Logstash:
- https://www.elastic.co/guide/en/logstash/current/docker.html

ELK có thể truy cập theo 2 cách:
- Giao diện command line (bash shell), vào Access --> Web Shell
- Giao diện đồ họa của Kibana, vào Access --> Kibana

Trong phần này, chúng ta sẽ bắt đầu cài đặt logstash lên máy chủ ELK. Nếu bạn để ý với lệnh ```docker images``` thì sẽ thấy rằng chúng tôi đã download về logstash image tương ứng với version của elasticsearch và kibana (cùng là 8.17.3).

Để dễ hiểu, mô hình kết nối giữa 3 thành phần này và nguồn log như sau:
```
                                                                                                          
+------------------+                                                                                       
|                  |         +------------------+                                                          
|  Log sources     |         |                  |                                                          
|                  |-------->|                  |         +------------------+         +------------------+
+------------------+         |     Logstash     |         |                  |         |                  |
+------------------+         |                  |-------->|  Elasticsearch   |<--------|      Kibana      |
|                  |-------->|                  |         |                  |         |                  |
|  Log sources     |         |                  |         +------------------+         +------------------+
|                  |         +------------------+                                                          
+------------------+                                                                                       
                           
```
- Log sources là nguồn log, ví dụ ở đây chính là thiết bị BIG-IP, nó đóng vai trò như một client gửi log thông qua giao thức syslog tới logstash (ta sẽ sử dụng 2 port lần lượt là 5140 và 5141 cho log tới từ WAF và DNS)
- Logstash là thành phần sẽ được cài đặt ở đây. Nó có nhiệm vụ nhận dạng log, chuyển về format mà Elasticsearch có thể hiểu được (json), và gửi cho Elasticsearch theo giao thức https:// trên port 9200
- Kibana là ứng dụng web, cung cấp giao diện cho ta thao tác với Elasticsearch dễ dàng hơn. Thậm chí nó còn làm được nhiều hơn thế, như vẽ các dashboard, đồ thị, phân tích điều tra.. Người quản trị truy cập vào Kibana theo giao thức http:// trên port 5601

Đứng từ giao diện bash shell của ELK, gõ lệnh:
```
git clone https://github.com/biennt/f5academy2025.git
```
Kiểm tra nội dung các file trong thư mục pipeline/
- output.conf chứa thông tin để logstash ghi dữ liệu vào elasticsearch
- f5waf.conf định nghĩa đầu vào cho log source từ F5 BIG-IP WAF
- f5dns.conf định nghĩa đầu vào cho log source từ F5 BIG-IP DNS
- .. và các file khác nếu có


Lưu ý các thông tin sau:
- Hosts: chứa tối thiểu 1 địa chỉ của elasticsearch master server
- Index: tên index sẽ được tạo/cập nhật dữ liệu trên elasticsearch
- User và Password: thông tin được logstash dùng để truy cập vào elasticsearch

Ngoài ra còn có phần filter, giúp Logstash nhận dạng format của log được gửi tới để nó biết cách chuyển về JSON. Bạn có thể tham khảo các ứng dụng trợ giúp tạo grok filter như:
- Tạo filter online: https://grokdebugger.com/
- Dùng chính Kibana để tạo filter: https://www.elastic.co/guide/en/kibana/current/xpack-grokdebugger.html

Giờ thì khởi tạo container logstash, với tất cả các file chỉ thị nguồn log nằm trong thư mục /f5academy2025/pipeline
```
docker run -d --name logstash --net host -v /f5academy2025/pipeline:/usr/share/logstash/pipeline -e XPACK_MONITORING_ENABLED=false --restart=unless-stopped logstash:8.17.3
```

Kiểm tra quá trình khởi động logstash bằng lệnh:
```
docker logs -f logstash
```
Nếu không có lỗi gì, ta có thể vào BIG-IP để cấu hình đẩy log cho phần F5 WAF.

## Lab 3- Cấu hình F5 BIG-IP (WAF) để đẩy log về ELK

Phần này sẽ sử dụng đến file pipeline/f5waf.conf trên máy ELK. Hãy kiểm tra trước nội dung của file này.

Từ BIG-IP Host, vào TMUI/WEBGUI, sau khi đăng nhập chọn  ```Security  ››  Event Logs : Logging Profiles  ››  Create New Logging Profile...```

Đặt tên profile là ```remote_log```, chọn ```Application Security```, sau đó:

- ```Storage Destination``` chọn Remote Storage
- ```Logging Format``` chọn Key-Value Pairs (Splunk)
- ```IP Address``` nhập vào 10.1.30.8
- ```Port``` nhập vào 5140 sau đó ấn vào ```Add```
- ```Maximum Entry Length``` chọn 64K
- ```Request Type``` chọn All requests

Sau đó áp dụng profile này bằng cách vào ```Local Traffic  ››  Virtual Servers : Virtual Server List  ››  vshttp```, chọn ```Security --> Policies```

Mục ```Log Profile``` chọn thêm ```remote_log``` sau đó bấm vào ```Update```

Tạo một số request tới dịch vụ web để phát sinh log:
- Từ BIG-IP Host, mục Access chọn JUICESHOP
- Từ Jump host, mục Access chọn Web Shell và sau đó sử dụng lệnh curl để tạo traffic, ví dụ ```curl http://10.1.10.9/```

Vào Kibana, chọn ```Stack Management --> Index Management``` ta sẽ nhìn thấy một index mới bắt đầu bằng ```f5waf-``` theo sau là định dạng năm-tháng-ngày được tạo ra.

Cũng từ giao diện này, chọn ```Data Views``` (trong phần Kibana), bấm vào ```Create data view```. 

Đặt tên Data view là f5waf, Index pattern là ```f5waf-*``` , sau đó bấm vào ```Save data view to Kibana```

Cuối cùng, xem log nhận được bằng cách bấm vào menu 3 dấu gạch ngang phía trên bên trái cửa sổ (thỉnh thoảng người ta gọi đây là hamburger menu vì nó giống cái bánh mì kẹp) và chọn Discover. Chọn Data view là f5waf nếu nó chưa được chọn sẵn.

Nếu bạn thấy được các dòng log, nghĩa là từ BIG-IP đã gửi được các log liên quan đến WAF tới ELK. 

Nếu bạn nhìn thấy ```_grokparsefailure``` trong log, nghĩa là có lỗi gì đó liên quan đến định dạng mà logstash nó không thể format được, thường là do viết sai filter (grok filter), bạn có thể xem lại file f5waf.conf, phần ```filter --> grok --> match```, và sử dụng công cụ Grok Debugger để kiểm tra, chỉnh sửa. Nhưng nhìn chung thì đến đây là 99% hoàn thành rồi.

**Chúc mừng bạn!**

Giảng viên sẽ hướng dẫn bạn một số thao tác, các tính năng cơ bản trên màn hình ```Discover``` này.

Là một người quản trị thiết bị WAF của F5, khi xem xét các log truy cập, bạn quan tâm điều gì? Tôi có một số gợi ý về các trường thông tin sau:
- ip_client: địa chỉ IP của client (layer 4), đôi khi nó không phải địa chỉ IP thật của người dùng nếu đi qua một hoặc nhiều các proxy khác trước khi tới thiết bị WAF
- x_forwarded_for_header_value: địa chỉ IP của client được lưu lại trong HTTP header (X-Forward-For) do thiết bị proxy phía trên chèn vào, đây là thông tin layer 7, tin vào giá trị này hay không còn tùy thuộc vào ngữ cảnh. Giảng viên sẽ giải thích kỹ hơn cho bạn
- dest_ip và dest_port là địa chỉ IP và port dịch vụ đang thực hiện request này trên BIG-IP (đại diện cho ứng dụng)
- policy_name: tên policy đang được áp dụng
- request_status: trạng thái của request (có thể là alerted hoặc passed hoặc blocked)
- violations: các loại vi phạm đối với request đó
- request: nội dung cụ thể của request (bắt đầu bằng method, sau đó là URI và các headers)
- violation_rating: mức độ vi phạm được đánh số từ 1 đến 5. Số càng lớn thể hiện mức độ vi phạm càng nghiêm trọng. Nếu bạn để ý, trong file cấu hình logstash, tôi đã chuyển đổi giá trị này từ string sang Integer để chúng ta có thể thao tác với các phép toán so sánh trong Elasticsearc/Kibana. Ví dụ bạn có thể lọc các request có violation_rating từ 3 trở lên để phân tích một cách dễ dàng.

Lúc này, bạn nên nghĩ về việc tạo một cái Dashboard, đưa vào đấy các biểu đồ giám sát một số chỉ số quan trọng.

## Lab 4- Cấu hình F5 BIG-IP (DNS) để đẩy log về ELK

Phần này sẽ sử dụng đến file pipeline/f5dns.conf trên máy ELK. Hãy kiểm tra trước nội dung của file này.

Trên BIG-IP Host, vào TMUI/WEBGUI, vào ```Local Traffic  ››  Pools : Pool List  ››  New Pool...``` để tạo một pool để đẩy log:
- Name: nhập vào ```elkpooldns```
- Member: nhập vào Node Name và Address là ```10.1.30.8```, Service Port là ```5141``` sau đó bấm vào Add (lab này chỉ có 1 logstash, nếu có nhiều hơn thì lần lượt add vào đây)

Cuối cùng bấm vào Finished để hoàn tất việc tạo pool có tên là ```elkpooldns```

Vào mục ```System  ››  Logs : Configuration : Log Destinations```, bấm ```Create```
- Name: elklogdestdns
- Type: Remote High-Speed Log
- Pool Name: elkpooldns

Bấm vào Finished để hoàn tất

Vào mục ```System  ››  Logs : Configuration : Log Publishers```, bấm ```Create```
- Name: elklogpubdns
- Destinations: elklogdestdns

Vào mục ```DNS  ››  Delivery : Profiles : Other : DNS Logging```, bấm ```Create```
- Name: dnslogprofile
- Log Publisher: elklogpubdns
- Chọn thêm Include Query ID và Log Responses (cơ bản là chọn hết các thông tin cần log)


Vào mục ```DNS  ››  Delivery : Profiles : DNS```, chọn profile có tên là ```dnsprofile```. Profile này đã được cấu hình sẵn để làm DNS Caching (vì thế trong Lab 0 chúng ta mới có thể kiểm tra và thử dịch vụ phân giải DNS thành công)

Trong ```dnsprofile```, phần ```Logging and Reporting```:
- Logging: Enabled
Logging Profile: dnslogprofile

Bấm vào Update để hoàn tất.

Từ máy Jumphost, bạn có thể sử dụng lệnh dig để truy vấn DNS và qua đó tạo log..

Ví dụ:
```
dig @10.1.10.9 facebook.com
dig @10.1.10.9 google.com
dig @10.1.10.9 vnexpress.net
dig @10.1.10.9 dantri.com
```

Nào, bây giờ hãy nín thở! Vào Kibana kiểm tra:

Vào Stack Management --> Index Management: bạn có nhìn thấy index có tên bắt đầu là f5dns- theo sau là định dạng năm-tháng-ngày không? Nếu có, hãy tiến hành tạo data view để xem trên Discover

Vào ```Data Views```, bấm vào ```Create data view```
- Name: f5dns
- Index pattern: f5dns-*

Sau đó bấm vào ```Save data view to Kibana```. Kiểm tra trong màn hình ```Discover``` xem dữ liệu của data view ```f5dns```

## Lab 5- Cấu hình F5 BIG-IP để đẩy system log về ELK

Phần này sẽ sử dụng đến file pipeline/f5ltm.conf trên máy ELK. Hãy kiểm tra trước nội dung của file này.

Trên BIG-IP Host, vào TMUI/WEBGUI, vào ```Local Traffic  ››  Pools : Pool List  ››  New Pool...``` để tạo một pool để đẩy log:
- Name: nhập vào ```elkpoolltm```
- Member: nhập vào Node Name và Address là ```10.1.30.8```, Service Port là ```5142``` sau đó bấm vào Add (lab này chỉ có 1 logstash, nếu có nhiều hơn thì lần lượt add vào đây)

Cuối cùng bấm vào Finished để hoàn tất việc tạo pool có tên là ```elkpoolltm```

Vào mục ```System  ››  Logs : Configuration : Log Destinations```, bấm ```Create```
- Name: elklogdestltm
- Type: Remote High-Speed Log
- Pool Name: elkpoolltm

Bấm vào Finished để hoàn tất

Vào mục ```System  ››  Logs : Configuration : Log Publishers```, bấm ```Create```
- Name: elklogpubltm
- Destinations: elklogdestltm

Vào mục ```System  ››  Logs : Configuration : Log Filters```, bấm ```Create```
- Name: filter_log_to_elk
- Severity: Informational
- Source: all
- Log Publisher: elklogpubltm

Để phát sinh log, bạn có thể vào máy webserver, tắt container juiceshop một lúc rồi bật lại:
```
docker stop juiceshop
# đợi khoảng 20 giây
docker start juiceshop
```
Đến đây, chắc bạn cũng đã biết phải làm gì trên Kibana để nhìn thấy index f5ltm-* và tạo data view f5ltm tương ứng cho nó rồi. Tôi không viết hướng dẫn nữa.
Bạn có thể thấy phần cấu hình ```Severity``` của log filter khá quan trọng. Nếu để là debug, thông tin log sẽ cự kỳ nhiều (quá mức cần thiết với việc vận hành nói chung).

## Lab 6- Cấu hình F5 BIG-IP Request log để đẩy http request và response log về ELK

Phần này sẽ sử dụng đến file pipeline/f5req.conf trên máy ELK. Hãy kiểm tra trước nội dung của file này.

Trên BIG-IP Host, vào TMUI/WEBGUI, vào ```Local Traffic  ››  Pools : Pool List  ››  New Pool...``` để tạo một pool để đẩy log:
- Name: nhập vào ```elklogreqpool```
- Member: nhập vào Node Name và Address là ```10.1.30.8```, Service Port là ```5143``` sau đó bấm vào Add (lab này chỉ có 1 logstash, nếu có nhiều hơn thì lần lượt add vào đây)

Cuối cùng bấm vào Finished để hoàn tất việc tạo pool có tên là ```elklogreqpool```

Vào ```Local Traffic  ››  Profiles : Other : Request Logging```, bấm vào Create để tạo một request log profile:
- Name: request-log-to-elk
- Request Logging: Enabled
- Template (cho Request log): ```req|$CLIENT_IP|$CLIENT_PORT|$VIRTUAL_IP|$VIRTUAL_PORT|$HTTP_METHOD|$HTTP_URI|${User-agent}```
- HSL Protocol (cho Request log): TCP
- Pool Name (cho Request log): elklogreqpool
- Response Logging: Enabled
- Template (cho Response log): ```res|$CLIENT_IP|$CLIENT_PORT|$VIRTUAL_IP|$VIRTUAL_PORT|$SNAT_IP|$SNAT_PORT|$SERVER_IP|$SERVER_PORT|$HTTP_METHOD|$HTTP_URI|$HTTP_STATCODE|$RESPONSE_SIZE|$RESPONSE_USECS|${User-agent}```
- HSL Protocol (cho Response log): TCP
- Pool Name (cho Response log): elklogreqpool

Bạn có thể tham khảo thêm các trường thông tin được phép đặt (Template) tại [link này](https://techdocs.f5.com/en-us/bigip-14-0-0/external-monitoring-of-big-ip-systems-implementations-14-0-0/configuring-request-logging.html) 

Áp dụng request log profile vừa tạo vào virtual server bằng cách truy cập vào ```Local Traffic  ››  Virtual Servers : Virtual Server List  ››  vshttp```, Mục Configuration nhớ chọn Advanced, mục ```Request Logging Profile``` chọn ```request-log-to-elk```

Để phát sinh log, bạn có thể truy cập vào mục JUICESHOP trên menu Access của BIG-IP Host.. 

Sau đó, thao tác trên Kibana tương tự như các phần trên:
- Vào Stack Management: xem có index tên là f5http chưa, nếu có, tạo Data View cho nó.
- Vào Discover, chọn Data View tương ứng để xem thông tin được log.

## Lab 7- Sử dụng iRule để log về ELK

Chà chà, thành thật mà nói: **Xin chúc mừng bạn!**, và tôi cũng phải cám ơn bạn về sự kiên trì cho tới tận chỗ này. 

Như bạn thấy, chúng ta đã có khá nhiều thông tin lấy được từ F5 BIG-IP, từ log của DNS, HTTP đến WAF và cả system log của bản thân thiết bị BIG-IP.. 99% thông tin cần thiết cho người vận hành theo dõi hệ thống F5 BIG-IP cơ bản có thể thu thập bằng các cách như vậy mà không phải lập trình hay tạo script iRule gì cả. Bài lab này dành cho những bạn muốn làm nhiều hơn nữa, giải quyết 1% ngóc ngách nào đó. 

Ví dụ: Bạn muốn lấy một thông tin gì đó từ POST data, cụ thể như: Bạn muốn log lại tên user đăng nhập vào một ứng dụng nào đó chẳng hạn. Thì đúng là nó thuộc 1% còn lại, vì giả sử không có license WAF, bạn không có cách nào track được User's session. Không xác định được ai đã đăng nhập vào lúc nào.

Thôi được rồi, không để bạn chờ lâu, chúng ta vào việc luôn:

1. Log pool tương tự như đã từng làm ở các bước trên (tạo 1 pool chứa 1 member trỏ đến ```10.1.30.8```, Service Port là ```5144``` chẳng hạn, port này được định nghĩa ở bước 3
2. [Tạo iRule để đẩy log](https://clouddocs.f5.com/api/irules/HSL.html) Giảng viên sẽ giúp bạn trực tiếp các bước cơ bản của việc viết iRule, áp dụng nó vào Virtual server
3. Tạo file input và grok filter cho logstash
4. Khởi động lại logstash để nó nhận file input mới
5. Tạo request để phát sinh log (ví dụ thử đăng nhập)
6. Trên Kibana: kiểm tra index mới được tạo, nếu có thì tạo Data view cho nó.

