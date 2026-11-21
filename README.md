# Quản lý bán hàng và tồn kho cửa hàng đồ uống

Dự án nhóm triển khai trên Odoo Community với Contacts, Purchase, Inventory và Point of Sale. Phần tùy chỉnh đã triển khai trên máy Trọng là module yêu cầu bổ sung hàng tại `custom_addons/store_restock/`, phiên bản `20.0.2.0.0`: gửi yêu cầu, duyệt/từ chối, kho tổng gửi và siêu thị nhận hàng, cập nhật tồn qua Inventory.

Hướng dẫn lấy mã, cài Inventory, nâng cấp và tạo dữ liệu thử nằm trong [hướng dẫn cài đặt](docs/huong-dan-cai-dat.md). Xem [kết quả ngày 21/11](docs/ket-qua-2026-11-21.md) và [demo speed run](docs/demo-speed-run.md). Kết quả 19/11 và 20/11 được giữ như các mốc lịch sử.

## Môi trường

| Thành phần | Thông tin |
| --- | --- |
| Hệ điều hành | Windows |
| Odoo trên máy chuẩn bị | `20.0-20261115` theo `odoo-bin --version` |
| PostgreSQL server | `16.14`, xác nhận bằng `SHOW server_version;` trên database `odoo20` |
| URL trên mỗi máy | `http://localhost:8069/odoo/apps` |
| Database trên máy chuẩn bị | `odoo20` |

Tài liệu kế hoạch ghi Odoo 19.0. Nhóm cần chốt phiên bản chạy thực tế trước khi chia sẻ database hoặc phát triển module. Mỗi người dùng `localhost` để mở Odoo trên máy của mình.

## Khởi động trên Windows

1. Cài Odoo Community và PostgreSQL theo phiên bản nhóm chốt. Mở PowerShell ở thư mục muốn lưu dự án rồi chạy `git clone https://github.com/lehoangmiucon/odoo-drink-store.git`.
2. Mở `services.msc`. Kiểm tra dịch vụ PostgreSQL mà Odoo sử dụng đã chạy, rồi kiểm tra dịch vụ Odoo. Bật các dịch vụ đang dừng. Trên máy chuẩn bị, tên dịch vụ Odoo là `odoo-server-20.0`.
3. Khi cần nạp module của nhóm, mở file `odoo.conf` mà dịch vụ đang dùng. Trên máy chuẩn bị, file nằm ở `C:\Program Files\Odoo 20.0.20261115\server\odoo.conf`. Nối đường dẫn tuyệt đối của `custom_addons` vào cuối dòng `addons_path`, sau dấu phẩy. Xem `config/odoo.conf.example` để biết dạng cấu hình. Khởi động lại dịch vụ Odoo sau khi lưu. Dịch vụ cần có quyền đọc thư mục clone.
4. Mở `http://localhost:8069/odoo/apps`, đăng nhập đúng database. Bật chế độ nhà phát triển rồi vào Ứng dụng → Cập nhật danh sách ứng dụng và tìm `store_restock`. Bỏ bộ lọc Ứng dụng khi cần tìm theo tên kỹ thuật. Cài module rồi cấp nhóm quyền theo hướng dẫn cài đặt.

## Sao lưu database

Mở `http://localhost:8069/web/database/manager`, chọn **Backup** cạnh database dự án và chọn **ZIP (includes filestore)**. Nhập Master Password trực tiếp trên trang quản trị cục bộ. Lưu ZIP ở thư mục ngoài repo, ví dụ `D:\odoo-backups`. Mở ZIP để kiểm tra `dump.sql`, `manifest.json` và các tệp trong `filestore/` nếu database có tệp đính kèm lưu trên đĩa. Chia sẻ backup qua nơi lưu trữ riêng của nhóm.

## Làm việc với Git

- `main` giữ bản chung. Tạo nhánh `feat/<ten-viec>` hoặc `fix/<ten-loi>` từ `main` mới nhất, đẩy nhánh lên GitHub rồi mở pull request vào `main`.
- Mã module nằm trong `custom_addons/`, tài liệu kỹ thuật nằm trong `docs/` và kịch bản kiểm thử nằm trong `tests/`.
- Mỗi người giữ file cấu hình thật, mật khẩu và backup trên máy hoặc nơi lưu trữ riêng của nhóm. Trước khi commit, dùng `git diff --cached --name-only` và `git diff --cached` để xem các tệp và nội dung đã chuẩn bị đưa lên Git.
