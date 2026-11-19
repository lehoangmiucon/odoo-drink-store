# Yêu cầu bổ sung hàng

Addon dành cho Odoo Community `20.0-20261115` trên máy Trọng. Nhân viên kho lập và gửi phiếu, quản lý duyệt hoặc từ chối. Model phiếu là `store.restock.request`. Bản đầu mỗi phiếu có một sản phẩm.

## Cài vào Odoo

1. Tạo ZIP backup của database sẽ dùng. Máy Trọng đã thêm `D:\odoo-drink-store\custom_addons` vào `addons_path`.
2. Khởi động lại dịch vụ `odoo-server-20.0` trong `services.msc` để nạp mã Python.
3. Đăng nhập tài khoản quản trị, vào đúng database. Bật chế độ nhà phát triển tại Cài đặt, rồi vào Ứng dụng và Cập nhật danh sách ứng dụng.
4. Tìm `store_restock` hoặc `Yêu cầu bổ sung hàng`, bấm Kích hoạt hoặc Cài đặt. Bỏ bộ lọc Ứng dụng nếu cần tìm theo tên kỹ thuật.
5. Vào Cài đặt → Người dùng và công ty → Người dùng. Cấp nhóm **Quản lý bổ sung hàng** cho tài khoản quản trị demo để có menu ứng dụng. Hai nhóm **Bổ sung hàng — Nhân viên** và **Bổ sung hàng — Quản lý** được hiển thị riêng trong quyền người dùng.
6. Tạo hai người dùng nội bộ với tên đăng nhập riêng. Cấp **Nhân viên kho** cho người dùng nhân viên và **Quản lý bổ sung hàng** cho người dùng quản lý. Đặt mật khẩu trực tiếp trên máy qua thao tác Đổi mật khẩu của người dùng. Dùng cửa sổ trình duyệt riêng cho mỗi tài khoản khi kiểm thử.
7. Quản trị viên có quyền quản lý sản phẩm dùng menu **Yêu cầu bổ sung hàng → Sản phẩm** để tạo **Nước suối 500 ml**, hoặc chọn sản phẩm thử đã có sẵn. Nhân viên chọn sản phẩm trên phiếu.

## Demo và minh chứng

| Bước | Tài khoản | Thao tác và kết quả |
| --- | --- | --- |
| 1 | Nhân viên | Tạo phiếu, chọn Nước suối 500 ml, số lượng 20, lý do cần bổ sung. Lưu nháp và chụp form có mã BSH. |
| 2 | Nhân viên | Bấm Gửi duyệt, trạng thái thành Chờ duyệt và nội dung chuyển sang chỉ đọc. |
| 3 | Quản lý | Mở phiếu vừa gửi, bấm Duyệt. Kiểm tra Đã duyệt, người và thời điểm xử lý. |
| 4 | Nhân viên | Tạo và gửi phiếu thứ hai với cùng sản phẩm, số lượng 5, lý do có nội dung. |
| 5 | Quản lý | Bấm Từ chối, nhập lý do rồi xác nhận. Kiểm tra trạng thái, người, thời điểm và lý do từ chối. |
| 6 | Nhân viên | Tạo phiếu số lượng 0 hoặc âm, thử gửi và chụp thông báo bị chặn. Thử thiếu sản phẩm và lý do rỗng. |
| 7 | Nhân viên | Kiểm tra phiếu đã gửi khóa nội dung và các nút duyệt/từ chối ẩn. Dùng nhân viên thứ hai để kiểm tra phạm vi xem. |

Quyền và chuyển trạng thái được kiểm tra tại máy chủ. Máy chủ chặn tự duyệt ngay cả khi tài khoản có cả hai vai trò. Duyệt phiếu giữ nguyên tồn kho. Menu Sản phẩm chỉ xuất hiện cho người được cấp quyền quản lý sản phẩm.

## Cập nhật và phiên bản

Sau khi sửa Python, khởi động lại dịch vụ Odoo. Sau khi sửa view hoặc dữ liệu quyền, dùng **Nâng cấp / Upgrade** trên ứng dụng `store_restock`. Sao lưu database trước khi cập nhật.

Bộ cài Odoo 20 trên máy dùng model quyền `ir.access`, trường nhóm người dùng `group_ids` và API so sánh đơn vị tính `uom.uom.compare`. Cần điều chỉnh và kiểm tra lại trước khi chuyển addon sang Odoo 19. Thiết kế ở `docs/store-restock-design.md` để TV4 rà soát tên kỹ thuật và hành vi.
