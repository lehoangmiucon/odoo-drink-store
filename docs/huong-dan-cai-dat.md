# Cài đặt và cập nhật chức năng bổ sung hàng

Bản hiện tại: `store_restock` **20.0.2.0.0**, đã kiểm tra trên Odoo Community **20.0-20261115**, PostgreSQL 16.14, Windows. Phụ thuộc ứng dụng **Tồn kho / Inventory (`stock`)**. Các bộ cài khác, đặc biệt Odoo 19, cần điều chỉnh và kiểm thử riêng vì bộ cài này dùng quyền `ir.access` và API kho Odoo 20.

Luồng: Nhân viên siêu thị gửi yêu cầu → Quản lý kho tổng duyệt/từ chối → Kho tổng gửi hàng → Siêu thị kiểm nhận → Xác nhận nhập kho. Duyệt chưa đổi tồn; gửi làm giảm kho tổng, nhận làm tăng kho siêu thị.

## 1. Lấy mã và nối addon

Lấy lần đầu:

```powershell
git clone https://github.com/lehoangmiucon/odoo-drink-store.git
Set-Location -LiteralPath '.\odoo-drink-store'
```

Đã có repo: lưu phần đang sửa vào nhánh riêng; khi working tree sạch:

```powershell
git switch main
git pull --ff-only origin main
git log -1 --oneline
```

Ghi lại commit để đối chiếu. Trong file cấu hình mà dịch vụ Odoo đang đọc, giữ đường dẫn gốc và thêm `custom_addons` của repo. Ví dụ máy Trọng:

```ini
addons_path = C:\Program Files\Odoo 20.0.20261115\server\odoo\addons,D:\odoo-drink-store\custom_addons
```

Thay đường dẫn theo máy mình. Không đưa cấu hình thật, mật khẩu hoặc backup lên Git.

## 2. Cài mới hoặc nâng cấp database

1. Dùng database thử. Nếu database đã có dữ liệu, vào `http://localhost:8069/web/database/manager` và tạo backup **ZIP có filestore** trước khi nâng cấp.
2. Mở `services.msc` bằng quyền quản trị. Khởi động lại dịch vụ Odoo (`odoo-server-20.0` trên máy Trọng) để nạp Python và khai báo asset mới.
3. Đăng nhập đúng database, bật chế độ nhà phát triển → Ứng dụng → Cập nhật danh sách ứng dụng.
4. Cài **Tồn kho / Inventory**, rồi tìm `store_restock` và **Kích hoạt**. Nếu module đã cài bản cũ, dùng **Nâng cấp / Upgrade**. Bản mới chuyển phụ thuộc từ `product` sang `stock`, nên kiểm tra Inventory đã được cài.
5. Ctrl+F5; bấm lại menu ứng dụng để nhận action mới, không chỉ tải lại URL kanban Sản phẩm cũ.

Phương án dòng lệnh trên bộ cài Windows của Trọng (thay đường dẫn/database trên máy khác). Dừng dịch vụ Odoo trước khi chạy và khởi động lại khi hoàn tất để tránh phục vụ bằng mã cũ trong quá trình nâng cấp:

```powershell
$odooPython = 'C:\Program Files\Odoo 20.0.20261115\python\python.exe'
$odooServer = 'C:\Program Files\Odoo 20.0.20261115\server\odoo-bin'
$odooConfig = 'C:\Program Files\Odoo 20.0.20261115\server\odoo.conf'
$databaseName = 'TEN_DATABASE_THU'
$env:PYTHONUTF8 = '1'
& $odooPython -X utf8 -B $odooServer -c $odooConfig --db_host=127.0.0.1 -d $databaseName -i stock -u store_restock --stop-after-init --no-http --workers=0
```

Lệnh này cài Inventory và cập nhật addon, không tự tạo tài khoản, tồn đầu kỳ hoặc phiếu mẫu. Không chạy lệnh trên database chưa xác định hoặc chưa backup.

## 3. Tài khoản và công ty

| Vai trò nghiệp vụ | Quyền cần cấp |
| --- | --- |
| Nhân viên siêu thị | Người dùng nội bộ, nhóm **Bổ sung hàng — Nhân viên / Nhân viên kho**; không cấp nhóm quản lý hoặc quản trị hệ thống |
| Quản lý kho tổng | Người dùng nội bộ, nhóm **Bổ sung hàng — Quản lý / Quản lý bổ sung hàng** |
| Người cấu hình/quản lý danh mục | Admin hệ thống có quyền quản lý sản phẩm và kho; tài khoản riêng khi triển khai thật |

Nhóm Nhân viên kho là tên kỹ thuật hiển thị hiện tại; trong demo tài khoản này đại diện cho **nhân viên siêu thị**. Admin đóng vai quản lý kho tổng khi trình bày.

Nhân viên chỉ xem/chọn sản phẩm. Bỏ quyền **Sản phẩm / Tạo (Create)** khỏi tài khoản nhân viên; menu sẽ mở danh mục chỉ đọc. Máy chủ vẫn chặn tạo/sửa/xóa sản phẩm và biến thể nếu quyền tạo bị cấp lại nhầm. Người có thêm nhóm Quản lý bổ sung hàng hoặc Quản trị hệ thống không bị quy tắc nhân viên này chặn, nhưng vẫn cần quyền sản phẩm gốc để quản lý danh mục.

Đặt mật khẩu bằng giao diện Người dùng và gửi riêng cho người nhận. Sau đổi quyền, đăng xuất/đăng nhập lại và Ctrl+F5. Các cửa sổ ẩn danh có thể dùng chung phiên; muốn đổi nhân viên phải đăng xuất hoặc dùng profile riêng.

**Công ty không phải kho:** kho tổng và siêu thị của luồng hiện tại phải thuộc **cùng một công ty**. Chọn đúng công ty chứa tuyến ở cả hai tài khoản. Tên công ty có thể đã được nhóm đổi; không mặc định Chicago hay San Francisco là hai kho. Tuyến không hiện thường do chọn nhầm công ty.

## 4. Chuẩn bị dữ liệu thử nhanh

Sau khi addon đã nâng cấp, chạy script bằng Odoo shell từ thư mục repo. Đây là dữ liệu cửa hàng giả lập, chỉ chạy trên database demo của nhóm:

```powershell
$odooPython = 'C:\Program Files\Odoo 20.0.20261115\python\python.exe'
$odooServer = 'C:\Program Files\Odoo 20.0.20261115\server\odoo-bin'
$odooConfig = 'C:\Program Files\Odoo 20.0.20261115\server\odoo.conf'
$databaseName = 'TEN_DATABASE_THU'
$env:PYTHONUTF8 = '1'
Get-Content -Raw '.\scripts\setup_restock_demo.py' | & $odooPython -X utf8 -B $odooServer shell -c $odooConfig --db_host=127.0.0.1 -d $databaseName --no-http --workers=0
```

Script dùng công ty mặc định của môi trường shell và tạo:

- **Kho tổng DEMO**, **Hàng đang đi DEMO**, **Siêu thị DEMO** và loại chuyển nội bộ có hỗ trợ backorder.
- Tuyến **Kho tổng → Siêu thị DEMO**.
- `[BSH-500] Nước suối 500 ml (chai)`, danh mục **Đồ uống / Nước suối**, số dư đầu kỳ 100 tại kho tổng.
- `[BSH-COLA330] Coca-Cola lon 330 ml (lon)`, danh mục **Đồ uống / Nước ngọt**, số dư đầu kỳ 50 tại kho tổng.

Số dư được tạo qua **điều chỉnh tồn kho gốc của Odoo**. Khi chạy lại, script giữ nguyên sản phẩm/vị trí đã có và không đặt lại tồn kho. Không tạo hoặc đổi mật khẩu. Số 100/50 là dữ liệu đầu kỳ của hai mặt hàng, không phải mặc định cho mọi phiếu/sản phẩm. Tên sản phẩm có chai/lon; đơn vị hệ thống của bộ dữ liệu là Đơn vị. Không tự đổi đơn vị sau khi đã phát sinh giao dịch kho.

Script không tự ghi đè thông tin danh mục đã chỉnh trên các sản phẩm có sẵn. Khi nâng cấp database đã dùng script cũ, admin kiểm tra mã/tên/danh mục trên hai mặt hàng và chỉnh lại qua Sản phẩm nếu cần. Các mã kỹ thuật `demo_water`, `demo_cola` được giữ để script nhận diện dữ liệu cũ.

## 5. Chuẩn bị thủ công nếu không dùng script

1. Admin tạo ba vị trí cùng công ty: kho tổng loại **Nội bộ**, hàng đang đi loại **Trung chuyển**, siêu thị loại **Nội bộ**. Kho tổng và siêu thị phải tách biệt, không là thư mục cha/con của nhau.
2. Tạo/chọn loại hoạt động **Chuyển nội bộ** cùng công ty, hỗ trợ tạo backorder (không chọn Never).
3. Mở **Yêu cầu bổ sung hàng → Cấu hình tuyến**, nhập ba vị trí và loại hoạt động trên. Cấu hình tuyến dành cho admin.
4. Admin vào **Sản phẩm → Mới**, nhập tên, mã/tham chiếu nội bộ duy nhất trong dữ liệu nhóm, danh mục; chọn **Hàng hóa**, **Theo dõi: Theo số lượng**. Bản hiện tại không xử lý sản phẩm theo lô/serial.
5. Dùng **điều chỉnh tồn kho** của Inventory để nhập số dư thử vào đúng vị trí kho tổng và áp dụng. Tạo sản phẩm chưa làm phát sinh tồn. Không nhập số dư vào siêu thị nếu muốn demo siêu thị nhận từ 0.

Menu Sản phẩm mặc định mở bảng và lọc **Đồ uống**. Mã sản phẩm và tham chiếu nội bộ là cùng một trường; mã vạch là trường riêng, có thể bật cột khi cần. Nếu tạo mặt hàng ngoài Đồ uống, bỏ bộ lọc để xem; không xóa bàn ghế mẫu chỉ để dọn màn hình demo.

## 6. Chạy thử và xử lý lỗi thường gặp

Thực hiện [demo speed run](demo-speed-run.md). Tạo phiếu số lượng 10 → gửi → quản lý duyệt → quản lý gửi hàng → nhân viên nhận đủ 10. Duyệt chưa đổi tồn; gửi giảm kho tổng 10; nhận tăng siêu thị 10. Tồn hiển thị là số hiện tại, dùng chung giữa các phiếu cùng sản phẩm, không là ảnh chụp đầu kỳ.

Thử thêm: nhận 6 rồi 4 trên phiếu 10; nhập 0/âm/vượt còn lại; thử nhân viên khác đọc/nhận; thử nhân viên sửa danh mục. Chỉ người tạo phiếu được xác nhận nhận. Sau nhận thiếu, trạng thái vẫn **Đang vận chuyển**, kèm Đã nhận/Còn chờ nhận và lịch sử từng lần.

| Hiện tượng | Kiểm tra |
| --- | --- |
| Không thấy tuyến | Công ty đang chọn, công ty được phép của tài khoản, tuyến còn hoạt động |
| Không thấy sản phẩm trong bảng | Bộ lọc Đồ uống, danh mục sản phẩm, trạng thái lưu trữ/công ty |
| Duyệt báo chưa theo dõi tồn | Hàng hóa + Theo số lượng; không dùng dịch vụ hoặc lô/serial |
| Gửi báo thiếu hàng | Tồn khả dụng đúng vị trí kho tổng; chưa đủ toàn bộ yêu cầu thì không gửi được |
| Nhận báo phiên khác đã xử lý | Đóng hộp thoại, tải lại phiếu, kiểm lại phần còn chờ nhận |
| Nhân viên không có nút Mới/Sửa sản phẩm | Đúng thiết kế chỉ xem/chọn, dùng admin khi quản lý danh mục |
| Phiếu đã chuyển kho không xóa được | Giữ lịch sử đối chiếu, kể cả admin không xóa phiếu đã liên kết chuyển kho |
| Mã BSH có khoảng trống | Sequence tiếp tục tăng sau xóa/rollback; không tự đặt lại để demo |

Không sửa/xác nhận trực tiếp các phiếu kho liên kết ngoài các nút của addon trong bài demo. Nếu dữ liệu kho đã bị chỉnh ngoài luồng, dừng và kiểm tra, không bấm lặp để cố hoàn tất.

## 7. Kiểm thử tự động và backup

Chỉ chạy trên database thử riêng đã có addon. Ví dụ:

```powershell
& $odooPython -X utf8 -B $odooServer -c $odooConfig --db_host=127.0.0.1 -d 'TEN_DATABASE_KIEM_THU' -u store_restock --test-enable --test-tags /store_restock --http-port=8079 --stop-after-init --no-http --workers=0
```

Odoo test có thể khởi động HTTP dù có `--no-http`, nên dùng cổng riêng còn trống. Bộ hiện tại có 9 test tích hợp cho giao nhận, số tồn, quyền và danh mục. Xem [kết quả ngày 21/11](ket-qua-2026-11-21.md).

Git chuyển mã và tài liệu; không mang theo database, tài khoản, ảnh hay số tồn. Backup ZIP giữ riêng ngoài repo. Backup ngày 19/11 là dữ liệu phiên bản trước khi có giao nhận; khôi phục trên database mới rồi nâng cấp addon, cấu hình tuyến và dữ liệu thử theo hướng dẫn này. Việc cài/restore trên máy thành viên cần được nhóm kiểm tra thực tế và ghi kết quả.
