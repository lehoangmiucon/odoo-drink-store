# Cài chức năng yêu cầu bổ sung hàng trên máy thành viên

Addon `store_restock` phiên bản `20.0.1.0.0` đã cài và chạy thử trên Odoo Community `20.0-20261115`, PostgreSQL `16.14`, Windows. Thành viên dùng cùng bộ cài để tái hiện kết quả. Addon dùng cơ chế `ir.access` của bộ cài Odoo 20 này, cần điều chỉnh và kiểm thử riêng khi chuyển sang Odoo 19.

## 1 Lấy mã

Mở PowerShell ở thư mục muốn lưu dự án. Khi lấy lần đầu, chạy hai lệnh sau.

```powershell
git clone https://github.com/lehoangmiucon/odoo-drink-store.git
Set-Location -LiteralPath '.\odoo-drink-store'
```

Nếu đã có repo, vào thư mục clone, kiểm tra `git status -sb`, lưu công việc đang sửa vào nhánh của mình trước khi chuyển nhánh. Khi working tree sạch, chạy các lệnh dưới đây để lấy bản chung.

```powershell
git switch main
git pull --ff-only origin main
git log -1 --oneline
```

Ghi mã commit vào nhật ký cài đặt để nhóm đối chiếu đúng phiên bản. Nếu `pull` báo lỗi hoặc có thay đổi cục bộ, giữ lại thông báo để xử lý lịch sử và phần việc đang sửa.

## 2 Nối custom_addons

Mở file `odoo.conf` mà dịch vụ Odoo trên máy đang đọc. Giữ các đường dẫn có sẵn trong `addons_path` và nối đường dẫn tuyệt đối tới thư mục `custom_addons` của repo sau dấu phẩy. Ví dụ trên máy Trọng dùng dòng dưới đây.

```ini
addons_path = C:\Program Files\Odoo 20.0.20261115\server\odoo\addons,D:\odoo-drink-store\custom_addons
```

Mỗi thành viên thay đường dẫn theo vị trí cài và clone trên máy mình. Dịch vụ cần có quyền đọc thư mục đó. Giữ cấu hình thật và thông tin đăng nhập trên máy cục bộ. Mở `services.msc` bằng quyền quản trị và khởi động lại dịch vụ Odoo, ví dụ `odoo-server-20.0`.

## 3 Cài trên database của thành viên

1. Tạo database thử qua `http://localhost:8069/web/database/manager`, hoặc dùng database thử đã có và tạo ZIP backup trước khi thay đổi.
2. Đăng nhập tài khoản quản trị vào đúng database vừa chọn. Khi có nhiều database, chọn lại qua nút Select ở trang đăng nhập hoặc dùng `/web/login?db=TEN_DATABASE`.
3. Vào Cài đặt và bật chế độ nhà phát triển. Vào Ứng dụng → Cập nhật danh sách ứng dụng → Cập nhật.
4. Tìm `store_restock`, bỏ bộ lọc Ứng dụng nếu chưa thấy, rồi bấm Kích hoạt / Cài đặt trên ứng dụng **Yêu cầu bổ sung hàng**.
5. Vào Cài đặt → Người dùng & Công ty → Người dùng, cấp **Bổ sung hàng — Quản lý → Quản lý bổ sung hàng** cho tài khoản quản trị demo. Lưu thủ công nếu có biểu tượng đám mây rồi tải lại trang.

Git chuyển mã addon và tài liệu. Sản phẩm, người dùng và phiếu demo được tạo trong database trên máy đang chạy. Khi cài trên database mới, thực hiện bước chuẩn bị dữ liệu dưới đây.

## 4 Chuẩn bị dữ liệu và tài khoản

Tài khoản quản trị có quyền sản phẩm mở Yêu cầu bổ sung hàng → Sản phẩm, tạo **Nước suối 500 ml**, loại **Hàng hóa**. Ghi rõ đơn vị tính thực tế khi lập phiếu. Bản demo của Trọng đang dùng nhãn đơn vị **Đơn vị**.

Tạo hai tài khoản nhân viên nội bộ có vai trò **User**, đăng nhập riêng, và cấp quyền như bảng sau. Tài khoản quản trị demo có thể đóng vai trò quản lý để duyệt phiếu của nhân viên.

| Tài khoản | Bổ sung hàng — Nhân viên | Bổ sung hàng — Quản lý |
| --- | --- | --- |
| Nhân viên kho thử | Nhân viên kho | No |
| Nhân viên kho thử 2 | Nhân viên kho | No |
| Quản lý demo | No | Quản lý bổ sung hàng |

Mở menu ⋮ cạnh tên người dùng → Thay đổi Mật khẩu. Nếu Odoo yêu cầu xác minh, nhập mật khẩu hiện tại của tài khoản quản trị đang thao tác. Trong hộp tiếp theo, nhập mật khẩu mới vào dòng tài khoản nhân viên rồi xác nhận. Giữ thông tin đăng nhập cục bộ và truyền riêng cho người dùng cần truy cập. Dùng cửa sổ thường cho quản lý và cửa sổ ẩn danh cho nhân viên khi demo. Các cửa sổ ẩn danh có thể dùng chung phiên đăng nhập, cần đăng xuất khi đổi nhân viên.

## 5 Chạy demo và kiểm thử

1. Nhân viên tạo phiếu chọn sản phẩm, số lượng 20, lý do có nội dung. Lưu nháp, chụp mã phiếu rồi bấm Gửi duyệt.
2. Quản lý mở phiếu chờ duyệt và bấm Duyệt. Kiểm tra trạng thái, người và thời gian xử lý.
3. Nhân viên tạo phiếu thứ hai số lượng 5, gửi duyệt. Quản lý từ chối với lý do có nội dung rồi kiểm tra kết quả. Duyệt phiếu giữ nguyên tồn kho.
4. Trên phiếu nháp, thử số lượng 0, âm, thiếu sản phẩm và lý do rỗng. Gửi duyệt phải bị chặn. Đổi thành dữ liệu hợp lệ rồi gửi, kiểm tra nội dung đã khóa.
5. Quản lý thử từ chối phiếu chờ duyệt với lý do trống. Odoo yêu cầu nhập lý do. Bấm Hủy để giữ nguyên phiếu.
6. Đăng nhập nhân viên thứ hai, kiểm tra danh sách trống khi tài khoản chưa tạo phiếu. Sao chép URL của một phiếu nhân viên thứ nhất từ chính môi trường đang chạy và mở URL đó bằng nhân viên thứ hai, xác nhận bị chặn đọc.

Chụp kết quả và ghi đầu vào, kỳ vọng, kết quả thực tế theo mẫu ở tài liệu kết quả ngày 19/11. Khi người dùng đã chạy được trên máy thành viên, bổ sung tên máy, phiên bản và commit đã cài vào kết quả bàn giao.

## 6 Cập nhật mã sau khi đã cài

Backup database trước khi cập nhật. Lấy `main` mới bằng `git pull --ff-only origin main` khi đang ở nhánh main sạch. Khởi động lại dịch vụ Odoo để nạp Python. Vào Ứng dụng, tìm `store_restock` rồi chọn **Nâng cấp / Upgrade** để nạp view và cấu hình quyền. Chạy lại các ca demo liên quan.

## 7 Khôi phục bản demo của Trọng khi cần

Lấy file `odoo20_sau_demo_2026-11-19.zip` qua nơi lưu riêng của nhóm. Chuẩn bị cùng bộ cài Odoo và repo, nối `custom_addons`, khởi động lại dịch vụ trước khi khôi phục. Vào Database Manager → Restore Database, chọn ZIP và đặt tên database mới, ví dụ `odoo20_demo_restore`. Nếu được hỏi, chọn phương án tạo bản sao. Sau khi hoàn tất, đăng nhập database mới bằng tài khoản trong bản backup và kiểm tra phiếu, tài khoản, sản phẩm và tệp đính kèm. Nhóm cần chạy thử bước khôi phục để có minh chứng bàn giao. Việc đọc ZIP đã được kiểm tra, thao tác khôi phục trên máy thành viên đang chờ thực hiện.
