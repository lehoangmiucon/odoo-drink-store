# Thiết kế giao diện và quyền cho yêu cầu bổ sung hàng

**Nhiệm vụ `1811-TV5` · 18/11/2026 · Lê Hoàng Trọng**

Bản thiết kế đề xuất để Huy (TV4) rà soát. Phạm vi gồm YC10–YC12 trong báo cáo ngày 18/11 của Thiên, tương ứng với gửi yêu cầu bổ sung hàng, xử lý yêu cầu và kiểm soát quyền. Bản đầu áp dụng cho một cửa hàng và mỗi phiếu có một sản phẩm. TC10–TC12 sẽ chạy sau khi có module và tài khoản thử.

## 1. Menu và danh sách

Menu **Yêu cầu bổ sung hàng → Phiếu bổ sung hàng** mở danh sách, bấm một dòng để mở form. Nhân viên kho thấy phiếu của mình và có nút **Tạo**. Quản lý thấy toàn bộ phiếu, mặc định lọc **Chờ duyệt**. Hai vai trò có thể lọc theo trạng thái và tìm theo mã phiếu hoặc sản phẩm. Quản lý có thêm bộ lọc theo người yêu cầu và có thể bỏ lọc mặc định để xem lịch sử.

```text
Yêu cầu bổ sung hàng  /  Phiếu bổ sung hàng            [Tạo]*
Tìm mã phiếu, sản phẩm                          [Bộ lọc ▾]

Mã phiếu   Sản phẩm          SL    Người yêu cầu    Ngày        Trạng thái
BSH-0001   Nước suối 500 ml  20    Nhân viên kho A  18/11/2026  Chờ duyệt
BSH-0002   Trà xanh 450 ml   12    Nhân viên kho A  18/11/2026  Từ chối

* Nút Tạo dành cho nhân viên kho.
```

## 2. Form và nút thao tác

```text
Phiếu bổ sung hàng  /  BSH-0001                      [Chờ duyệt]
[Gửi duyệt]*   [Duyệt]**   [Từ chối]**

Người yêu cầu   Nhân viên kho A       Ngày yêu cầu   18/11/2026
Sản phẩm        Nước suối 500 ml      Số lượng       20 Chai
Lý do           Tồn quầy thấp, cần bổ sung trước ca tối.

Xử lý phiếu  (hiện sau khi duyệt hoặc từ chối)
Người xử lý     …                    Thời gian xử lý  …
Lý do từ chối   …  (chỉ hiện khi từ chối)

* Chủ phiếu ở trạng thái Nháp.
** Quản lý xử lý phiếu Chờ duyệt của người khác.
```

| Nút | Ai dùng và khi nào | Kết quả |
| --- | --- | --- |
| **Gửi duyệt** | Nhân viên kho, phiếu nháp của mình | Kiểm tra sản phẩm, số lượng dương và lý do có nội dung. Nếu hợp lệ, chuyển sang **Chờ duyệt** và khóa nội dung phiếu. |
| **Duyệt** | Quản lý, phiếu chờ duyệt của người khác | Chuyển sang **Đã duyệt**, lưu người và thời gian xử lý. Việc nhập hàng tiếp tục theo quy trình Purchase và Inventory. Tồn kho giữ nguyên khi duyệt. |
| **Từ chối** | Quản lý, phiếu chờ duyệt của người khác | Mở hộp thoại có ô **Lý do từ chối** bắt buộc và hai nút **Xác nhận từ chối**, **Hủy**. Khi xác nhận hợp lệ, lưu lý do, người và thời gian xử lý rồi chuyển sang **Từ chối**. Bấm Hủy giữ nguyên phiếu. |

Sau khi gửi, các trường sản phẩm, số lượng và lý do chuyển sang chỉ đọc. **Đã duyệt** và **Từ chối** là trạng thái kết thúc. Khi cần gửi lại yêu cầu đã bị từ chối, nhân viên tạo phiếu mới để giữ lịch sử phiếu cũ.

## 3. Tên kỹ thuật đề xuất

| Thành phần | Tên kỹ thuật |
| --- | --- |
| Addon | `store_restock` |
| Model phiếu | `store.restock.request` |
| Model hộp thoại từ chối | `store.restock.reject.wizard` (transient, dành cho quản lý) |
| Menu chính và menu phiếu | `menu_store_restock_root`, `menu_store_restock_requests` |
| Action mở danh sách | `action_store_restock_requests` |
| Danh sách, form, tìm kiếm | `view_store_restock_request_list`, `view_store_restock_request_form`, `view_store_restock_request_search` |
| Hai nhóm quyền | `store_restock.group_restock_employee`, `store_restock.group_restock_manager` |
| Phương thức xử lý | `action_submit`, `action_approve`, `action_open_reject_wizard`, `action_confirm_reject` (xác nhận trên wizard) |

| Trường | Kiểu Odoo | Quy tắc |
| --- | --- | --- |
| `name` | Char | Mã phiếu do máy chủ cấp, đề xuất `BSH-0001`. |
| `requester_id` | Many2one → `res.users` | Người yêu cầu lấy từ tài khoản tạo phiếu, cố định. |
| `request_date` | Date | Ngày tạo theo ngày làm việc của người dùng, cố định. |
| `product_id` | Many2one → `product.product` | Sản phẩm. Có thể để trống khi lưu nháp, bắt buộc khi gửi. |
| `quantity` | Float | Số lượng theo đơn vị tồn kho của sản phẩm. Khi gửi, phải lớn hơn 0 theo độ làm tròn của đơn vị. |
| `reason` | Text | Lý do đề nghị. Bắt buộc khi gửi và phải có ký tự ngoài khoảng trắng. |
| `state` | Selection | Máy chủ quản lý trạng thái theo bảng bên dưới. |
| `reviewer_id` | Many2one → `res.users` | Máy chủ ghi người duyệt hoặc từ chối. |
| `reviewed_at` | Datetime | Máy chủ ghi thời điểm xử lý. |
| `rejection_reason` | Text | Lý do từ chối. Bắt buộc khi xác nhận từ chối. |

Wizard có `request_id` trỏ tới phiếu và `rejection_reason` để nhập lý do. Khi xác nhận, máy chủ kiểm tra lại phiếu được chọn, quyền và trạng thái hiện tại.

| Giá trị `state` | Nhãn | Chuyển tiếp hợp lệ |
| --- | --- | --- |
| `draft` | Nháp | Nhân viên gửi → `submitted` |
| `submitted` | Chờ duyệt | Quản lý duyệt → `approved`, hoặc từ chối → `rejected` |
| `approved` | Đã duyệt | Kết thúc |
| `rejected` | Từ chối | Kết thúc |

## 4. Bảng quyền

| Thao tác | Nhân viên kho | Quản lý |
| --- | --- | --- |
| Xem danh sách và mở phiếu | Phiếu của mình ở mọi trạng thái | Tất cả phiếu của cửa hàng |
| Tạo và sửa nội dung | Tạo phiếu cho mình, sửa sản phẩm, số lượng, lý do khi còn nháp | Chỉ xem nội dung khi xử lý |
| Gửi duyệt | Phiếu nháp của mình | Không theo vai trò quản lý |
| Duyệt hoặc từ chối | Không | Phiếu chờ duyệt của người khác |
| Sửa nội dung đã gửi, đổi trạng thái trực tiếp hoặc xóa phiếu | Không | Không |

Khi triển khai, ACL cấp quyền theo model và record rule giới hạn phạm vi phiếu. Đề xuất ACL của nhân viên gồm đọc, tạo, ghi và của quản lý gồm đọc, ghi. Quyền ghi của quản lý phục vụ việc xử lý phiếu qua hành động hợp lệ. Kiểm tra trên model phải chặn tạo phiếu giả danh, đổi trực tiếp trạng thái hoặc trường xử lý và sửa nội dung sau khi gửi, kể cả qua RPC. Kiểm tra lại nhóm, chủ phiếu và trạng thái ở mỗi nút xử lý. Giữ hai nhóm độc lập để quyền quản lý không tự bao gồm quyền lập phiếu. Nếu một tài khoản được cấp cả hai nhóm, vẫn chặn xử lý phiếu của chính họ. [Tài liệu Odoo 20 về kiểm soát truy cập](https://www.odoo.com/documentation/20.0/developer/tutorials/restrict_data_access.html)

## 5. Đối chiếu tiêu chí và bàn giao

| Yêu cầu | Kiểm tra sau khi có module |
| --- | --- |
| YC10 / TC10 | Gửi phiếu hợp lệ và thấy **Chờ duyệt**. Thử thiếu sản phẩm, số lượng bằng 0 hoặc âm, lý do rỗng và xác nhận máy chủ từ chối, phiếu vẫn là Nháp. |
| YC11 / TC11 | Quản lý duyệt một phiếu và từ chối một phiếu khác. Kiểm tra người, thời gian xử lý và lý do từ chối. Thử từ chối thiếu lý do, xử lý lại phiếu đã kết thúc và đối chiếu tồn trước/sau khi duyệt. |
| YC12 / TC12 | Dùng hai tài khoản nhân viên và một tài khoản quản lý để kiểm tra phạm vi xem. Thử tự duyệt, gọi nút trái quyền, sửa nội dung đã gửi hoặc ghi trực tiếp trạng thái và xác nhận máy chủ chặn. |

Huy rà soát tên model, trường, trạng thái và quy tắc xử lý. Trọng phụ trách danh sách, form, menu, nút và cấu hình nhóm quyền theo thiết kế. Hai bên xác nhận cách chia phần kiểm tra quyền trên model trước khi tích hợp để các thao tác qua máy chủ áp dụng cùng bộ quy tắc.
