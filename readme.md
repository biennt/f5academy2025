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

## Lab 1 - reviewing the setup
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

### Reactivate BIG-IP license

## Lab 2 - configure 
