# Yêu cầu bổ sung hàng

Addon dành cho Odoo Community `20.0-20261115` trên máy Trọng, bản hiện tại **20.0.2.0.0**, phụ thuộc `stock`. Nhân viên siêu thị lập yêu cầu; quản lý kho tổng duyệt/từ chối và gửi hàng; nhân viên kiểm nhận rồi xác nhận nhập kho. Model phiếu là `store.restock.request`, một sản phẩm mỗi phiếu, chuyển kho nội bộ cùng công ty, không lô/serial.

Hướng dẫn đầy đủ cho bản hiện tại: [cài đặt và nâng cấp](../../docs/huong-dan-cai-dat.md), [demo giao nhận](../../docs/demo-speed-run.md), [kết quả 21/11](../../docs/ket-qua-2026-11-21.md). Các bước bên dưới mô tả nền tảng; khi cài cần chuẩn bị thêm tuyến và tồn kho theo hướng dẫn mới.

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

Quyền và chuyển trạng thái được kiểm tra tại máy chủ. Máy chủ chặn tự duyệt ngay cả khi tài khoản có cả hai vai trò. Duyệt giữ nguyên tồn; gửi hàng giảm kho tổng và chuyển sang trung chuyển; nhận hàng tăng tồn siêu thị. Nhận thiếu tạo backorder và lịch sử từng lần. Menu Sản phẩm cho nhân viên chỉ xem/chọn; admin quản lý danh mục theo quyền sản phẩm.

## Cập nhật và phiên bản

Phiên bản `20.0.2.0.0` thêm Inventory, cấu hình tuyến, phiếu chuyển kho gốc, gửi hàng, nhận từng phần, lịch sử nhận và số tồn hiện tại. Có kiểm tra chống gửi/nhận trùng, dữ liệu không hợp lệ và trái quyền; giữ phiếu đã liên kết kho để đối chiếu. Danh mục đồ uống có bảng và tìm kiếm riêng theo vai trò. Lịch sử nhận khóa kéo giãn, căn trái số và chỉ sắp xếp theo thời gian. Chín test tích hợp nằm trong `tests/test_fulfillment.py`. Script dữ liệu thử ở `scripts/setup_restock_demo.py` tại gốc repo; chạy lại không reset tồn. Bắt buộc cài `stock`, nâng cấp addon và restart Odoo khi nhận mã Python mới.

Phiên bản `20.0.1.0.8` khóa kéo giãn cột và bỏ sắp xếp bằng tiêu đề trong danh sách phiếu; mặc định phiếu mới nhất đứng trước. Bộ lọc và nhóm trong ô tìm kiếm vẫn dùng bình thường. Renderer riêng chỉ áp dụng cho danh sách bổ sung hàng, không thay đổi các ứng dụng Odoo khác. Sau nâng cấp cần khởi động lại Odoo để nạp khai báo asset mới.

Phiên bản `20.0.1.0.7` chỉnh giao diện danh sách và form: giới hạn chiều rộng bảng, đặt độ rộng cột số lượng, nhóm sản phẩm/số lượng cùng nhau, tách thông tin phiếu và kết quả xử lý. Cột Số lượng căn trái cả tiêu đề và giá trị theo yêu cầu; bảng hỗ trợ cuộn ngang khi thiếu chỗ, có thêm nhóm theo trạng thái, ngày và người yêu cầu. CSS chỉ áp dụng cho addon này. Sau nâng cấp, tải lại trình duyệt bằng Ctrl+F5 để nhận giao diện mới.

Phiên bản `20.0.1.0.6` cho nhân viên xóa phiếu Nháp và Chờ duyệt của chính mình. Khi xóa phiếu ở trạng thái kết thúc, máy chủ báo “Chỉ được xóa phiếu nháp và phiếu chờ duyệt”. Nút Rút yêu cầu vẫn có thể dùng khi cần giữ lịch sử dưới trạng thái Đã hủy.

Phiên bản `20.0.1.0.5` thêm **Rút yêu cầu** cho nhân viên trên phiếu Chờ duyệt của mình. Sau xác nhận, phiếu chuyển sang **Đã hủy**, lưu thời điểm rút và giữ lịch sử cho quản lý. Phiếu Đã hủy kết thúc xử lý. Máy chủ khóa phiếu trong lúc chuyển trạng thái để kiểm tra lại trạng thái khi thao tác đồng thời với quản lý. Xóa phiếu Nháp và rút phiếu Chờ duyệt là hai thao tác riêng trên giao diện.

Phiên bản `20.0.1.0.4` cho nhân viên xóa phiếu Nháp của chính mình. Khi chọn nhiều phiếu, toàn bộ lựa chọn phải hợp lệ trước khi xóa. Nhân viên giữ lại phiếu Chờ duyệt, Đã duyệt và Từ chối. Quản trị viên hệ thống có quyền xóa dữ liệu thử ở mọi trạng thái.

Phiên bản `20.0.1.0.3` giữ phiếu Nháp riêng cho người tạo. Quản lý thấy phiếu của nhân viên sau khi nhân viên gửi duyệt, gồm Chờ duyệt, Đã duyệt và Từ chối. Quy tắc áp dụng cả danh sách và đọc trực tiếp tại máy chủ cho tài khoản quản trị thông thường.

Phiên bản `20.0.1.0.1` cho phép tài khoản có quyền quản trị hệ thống (`base.group_system`) xóa phiếu ở mọi trạng thái để dọn dữ liệu thử. Nhân viên và quản lý bổ sung hàng thông thường không có quyền xóa. Trong danh sách, quản trị viên chọn phiếu → Tác vụ → Xóa và xác nhận. Các tài khoản vẫn phải tuân theo phạm vi công ty được phép.

Sau khi sửa Python, khởi động lại dịch vụ Odoo. Sau khi sửa view hoặc dữ liệu quyền, dùng **Nâng cấp / Upgrade** trên ứng dụng `store_restock`. Sao lưu database trước khi cập nhật.

Bộ cài Odoo 20 trên máy dùng model quyền `ir.access`, trường nhóm người dùng `group_ids` và API so sánh đơn vị tính `uom.uom.compare`. Cần điều chỉnh và kiểm tra lại trước khi chuyển addon sang Odoo 19. Thiết kế ở `docs/store-restock-design.md` để TV4 rà soát tên kỹ thuật và hành vi.
