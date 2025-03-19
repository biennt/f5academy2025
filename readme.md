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
Kiểm tra nội dung file f5waf.conf
```
root@ip-10-1-1-8:/# cat /f5academy2025/pipeline/f5waf.conf 
input {
  tcp {
    type => "syslog"
    port => 5140
  }
  udp {
    type => "syslog"
    port => 5140
  }
}

filter {
  grok {
        match => { "message" => "<%{NUMBER:msgid}>%{DATA:logtime} %{HOSTNAME:logdevice} ASM:unit_hostname=\"%{HOSTNAME:unit_hostname}\",management_ip_address=\"%{IP:mgmt_ip}\",management_ip_address_2=\"%{DATA:mgmt_ip2}\",http_class_name=\"%{DATA:http_class_name}\",web_application_name=\"%{DATA:web_application_name}\",policy_name=\"%{DATA:policy_name}\",policy_apply_date=\"%{TIMESTAMP_ISO8601:policy_apply_date}\",violations=\"%{DATA:violations}\",support_id=\"%{DATA:support_id}\",request_status=\"%{DATA:request_status}\",response_code=\"%{DATA:response_code}\",ip_client=\"%{DATA:ip_client}\",route_domain=\"%{DATA:route_domain}\",method=\"%{DATA:method}\",protocol=\"%{DATA:protocol}\",query_string=\"%{DATA:query_string}\",x_forwarded_for_header_value=\"%{DATA:x_forwarded_for_header_value}\",sig_ids=\"%{DATA:sig_ids}\",sig_names=\"%{DATA:sig_names}\",date_time=\"%{TIMESTAMP_ISO8601:timestamp}\",severity=\"%{DATA:severity}\",attack_type=\"%{DATA:attack_type}\",geo_location=\"%{DATA:geo_location}\",ip_address_intelligence=\"%{DATA:ip_address_intelligence}\",username=\"%{DATA:username}\",session_id=\"%{DATA:session_id}\",src_port=\"%{DATA:src_port}\",dest_port=\"%{DATA:dest_port}\",dest_ip=\"%{IP:dest_ip}\",sub_violations=\"%{DATA:sub_violations}\",virus_name=\"%{DATA:virus_name}\",violation_rating=\"%{NUMBER:violation_rating}\",websocket_direction=\"%{DATA:websocket_direction}\",websocket_message_type=\"%{DATA:websocket_message_type}\",device_id=\"%{DATA:device_id}\",staged_sig_ids=\"%{DATA:staged_sig_ids}\",staged_sig_names=\"%{DATA:staged_sig_names}\",threat_campaign_names=\"%{DATA:threat_campaign_names}\",staged_threat_campaign_names=\"%{DATA:staged_threat_campaign_names}\",blocking_exception_reason=\"%{DATA:blocking_exception_reason}\",captcha_result=\"%{DATA:captcha_result}\",microservice=\"%{DATA:microservice}\",tap_event_id=\"%{DATA:tap_event_id}\",tap_vid=\"%{DATA:tap_vid}\",vs_name=\"%{DATA:vs_name}\",sig_cves=\"%{DATA:sig_cves}\",staged_sig_cves=\"%{DATA:staged_sig_cves}\",uri=\"%{DATA:uri}\",fragment=\"%{DATA:fragment}\",request=\"%{DATA:request},response=\"%{DATA:response}\""}
  }
  mutate {
    convert => {"violation_rating" => "integer"}
  }

}

output {
  elasticsearch {
    hosts => ["10.1.30.8:9200"]
    ssl_enabled => true
    ssl_verification_mode => none
    index => "f5waf-%{+YYYY.MM.dd}"
    user => "admin"
    password => "f5!Demo.admin"
  }
}
```
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
