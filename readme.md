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

Sau khi khởi động lại, ki
### Reactivate BIG-IP license

## Lab 2 - configure 
