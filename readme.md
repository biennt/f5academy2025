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

  

