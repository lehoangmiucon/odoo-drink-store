# Kế hoạch triển khai chức năng yêu cầu bổ sung hàng

Cập nhật ngày 19/11/2026. Bản đề xuất theo yêu cầu của Trọng, tập trung vào một chức năng tùy chỉnh `store_restock` đã thiết kế ngày 18/11. Cần nhóm xác nhận phạm vi và phiên bản dùng chung trước khi nghiệm thu.

## Cách triển khai

Odoo Website có trình kéo thả khối nội dung để dựng trang web. Odoo Studio hỗ trợ tùy chỉnh trường, form và quy trình qua giao diện và thuộc nhóm tính năng Enterprise. Với môi trường Community đang dùng, triển khai phiếu nội bộ bằng addon nhỏ, sau đó cài và sử dụng bằng giao diện Odoo. Các phần sản phẩm, người dùng và dữ liệu demo được cấu hình qua giao diện.

Nguồn đối chiếu gồm [Website building blocks](https://www.odoo.com/documentation/19.0/applications/websites/website/web_design/building_blocks.html), [Odoo Studio](https://www.odoo.com/documentation/19.0/applications/productivity/studio.html) và [giới thiệu các phiên bản Odoo](https://www.odoo.com/documents/content/yeCVmkonSbesc49giQfkzQo33981).

## Đầu ra cần bàn giao

- Một ứng dụng nội bộ **Yêu cầu bổ sung hàng**, menu, danh sách và form.
- Nhân viên tạo phiếu gồm sản phẩm, số lượng và lý do, rồi gửi duyệt.
- Quản lý duyệt hoặc từ chối, lưu người xử lý, thời điểm và lý do từ chối.
- Máy chủ kiểm tra số lượng, trạng thái và quyền. Phiếu được duyệt giữ nguyên tồn kho, bước nhập hàng sử dụng nghiệp vụ chuẩn khi cần.
- Mã nguồn, hướng dẫn cài và cập nhật, minh chứng kiểm thử và backup tương ứng với commit bàn giao.

## Hiện trạng

| Phần việc | Trạng thái đã xác nhận |
| --- | --- |
| Máy Trọng | Odoo 20.0-20261115, PostgreSQL 16.14, database odoo20 |
| Cấu hình | Đã thêm custom_addons và mở lại được Apps |
| Backup ban đầu | Đã kiểm tra ZIP ngày 17/11, có SQL, manifest và filestore |
| Thiết kế | docs/store-restock-design.md trên main, commit fcb0f69 |
| Addon chạy được | Thư mục store_restock mới có README, cần bổ sung mã module |
| Quy ước với TV4 | Model, trường và quyền đang ở mức đề xuất, chờ rà soát |

## Trình tự thực hiện

### Bước 1 Chọn môi trường demo

Dùng bản Odoo đang chạy trên máy Trọng làm môi trường triển khai trước. Nhóm đối chiếu phiên bản trên các máy trước khi chuyển database. Tạo ZIP backup mới của odoo20 qua Database Manager và lưu ngoài repo. Ghi tên backup và commit đang dùng.

### Bước 2 Chốt chức năng theo thiết kế

Mở docs/store-restock-design.md. Bản đầu mỗi phiếu có một sản phẩm, dùng model store.restock.request và bốn trạng thái draft, submitted, approved, rejected. Nhân viên thấy phiếu của mình, quản lý xem toàn bộ phiếu của cửa hàng. Ghi nhận góp ý của Huy khi rà soát.

### Bước 3 Hoàn thiện addon trên máy

Thêm manifest, các file khởi tạo, model phiếu, hộp thoại từ chối, mã phiếu tự động, view danh sách/form/tìm kiếm, menu, nhóm quyền, ACL và record rules. Dùng thiết kế ngày 18/11 làm đầu vào. Quyền và quy tắc chuyển trạng thái phải được kiểm tra trên máy chủ. Kiểm tra khả năng tương thích với bộ cài Odoo 20 trên máy.

### Bước 4 Cài addon vào database thử

Tạo database thử cùng phiên bản, ví dụ odoo20_restock_test, với tài khoản quản trị riêng được lưu cục bộ. Nếu dùng bản sao của odoo20, khôi phục ZIP với tên database thử và chọn phương án bản sao theo hộp thoại. Khởi động lại dịch vụ Odoo để nạp mã, đăng nhập đúng database thử, bật chế độ nhà phát triển tại Cài đặt, vào Ứng dụng và cập nhật danh sách ứng dụng. Tìm theo tên module store_restock và cài. Chỉ thực hiện bước này sau khi manifest và mã module đã có.

### Bước 5 Chuẩn bị dữ liệu qua giao diện

Tạo sản phẩm thử Nước suối 500 ml. Tạo hai người dùng nội bộ là Nhân viên kho thử và Quản lý thử, cấp đúng nhóm quyền của addon. Dùng hai tài khoản riêng để kiểm tra chức năng. Tài khoản quản trị dùng để cấu hình hệ thống.

### Bước 6 Chạy luồng thành công

Đăng nhập nhân viên, tạo phiếu với 20 chai và lý do có nội dung. Lưu nháp rồi gửi duyệt. Đăng nhập quản lý, mở phiếu và duyệt. Kiểm tra trạng thái, người và thời điểm xử lý. Lặp lại bằng phiếu khác để từ chối và ghi lý do. Chụp danh sách, form, thông tin xử lý và hộp thoại từ chối.

### Bước 7 Kiểm tra dữ liệu sai và quyền

Thử gửi phiếu thiếu sản phẩm, lý do rỗng hoặc số lượng không hợp lệ. Thử sửa phiếu sau khi gửi, duyệt lại phiếu đã xử lý, nhân viên gọi hành động duyệt, tự duyệt khi có cả hai nhóm và xem phiếu nhân viên khác. Kiểm tra thao tác trái quyền qua máy chủ và đối chiếu tồn trước/sau duyệt. Ghi đầu vào, kỳ vọng, kết quả thực tế và minh chứng cho TC10–TC12.

### Bước 8 Chốt bản demo và Git

Khi module cài được và các ca kiểm thử đạt, rà file chuẩn bị commit, đưa mã lên Git, ghi mã commit, tạo backup database demo và cập nhật hướng dẫn cài/khôi phục. Chạy lại từ hướng dẫn để xác nhận người khác làm theo được. Bộ bàn giao gồm mã nguồn, tài liệu, kết quả kiểm thử và ZIP lưu riêng.

## Phân công đề xuất

Huy phụ trách model và quy tắc nghiệp vụ. Trọng phụ trách view, menu, nhóm quyền, tích hợp và hướng dẫn cài. Trọng có thể chuẩn bị bản triển khai đầu khi Huy bận, ghi rõ các quyết định cần Huy rà. Thiên xác nhận tiêu chí YC10–YC12. TV6 chạy và ghi kiểm thử. TV7 tổng hợp minh chứng.

## Mốc hoàn thành đề xuất

Ngày 19–20/11 hoàn thiện addon và cài thử. Ngày 21/11 demo luồng gửi, duyệt và từ chối. Ngày 23–24/11 tích hợp và kiểm tra quyền, sửa lỗi. Ngày 25–28/11 nghiệm thu, hoàn thiện báo cáo, thử khôi phục và bàn giao. Tiến độ thực tế cập nhật theo kết quả chạy được.
