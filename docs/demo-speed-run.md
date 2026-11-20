# Demo bổ sung hàng — 3 đến 4 phút

## Chuẩn bị trước khi chiếu

- Mở sẵn hai phiên đăng nhập: nhân viên ở cửa sổ ẩn danh, quản lý ở cửa sổ thường. Kiểm tra đúng tài khoản.
- Chọn sẵn sản phẩm Nước suối 500 ml; ghi rõ số lượng đang tính theo đơn vị của sản phẩm. Dùng sản phẩm đồ uống để ví dụ thống nhất.
- Chuẩn bị một phiếu Chờ duyệt thứ hai để demo từ chối nhanh. Không cần xóa dữ liệu hay đặt lại số phiếu.
- Mở sẵn ứng dụng, làm mới danh sách; giữ ảnh minh chứng dự phòng khi máy chiếu/mạng gặp trục trặc. Lưu phần đang nhập trước khi chuyển cửa sổ.

## Thứ tự trình bày

| Thời lượng | Thao tác | Lời nói gợi ý |
| --- | --- | --- |
| 20 giây | Mở danh sách nhân viên | “Chức năng giúp nhân viên gửi nhu cầu bổ sung hàng, quản lý duyệt hoặc từ chối và lưu kết quả xử lý.” |
| 60 giây | Nhân viên tạo phiếu, chọn Nước suối 500 ml, số lượng 20, lý do “Cần bổ sung cho ca chiều”, bấm Gửi duyệt | “Hệ thống tự cấp mã và người yêu cầu. Phiếu Nháp riêng cho người tạo; gửi xong chuyển Chờ duyệt và khóa nội dung.” |
| 45 giây | Chuyển sang quản lý, làm mới danh sách, mở đúng mã vừa tạo rồi Duyệt | “Quản lý thấy phiếu đã gửi. Khi duyệt, hệ thống lưu người xử lý và thời gian.” |
| 45 giây | Mở phiếu Chờ duyệt đã chuẩn bị, bấm Từ chối, nhập “Hàng hiện tại vẫn đủ cho ca bán”, xác nhận | “Nếu từ chối phải nhập lý do để nhân viên biết kết quả.” |
| 30 giây | Quay lại nhân viên, làm mới và mở kết quả | “Nhân viên theo dõi được Đã duyệt hoặc Từ chối. Chức năng hiện xử lý yêu cầu và phê duyệt; việc nhập hàng thực tế chưa làm tăng tồn kho tự động.” |

Nếu còn 30 giây: thử gửi một phiếu số lượng 0 để chứng minh kiểm tra dữ liệu, sau đó đóng thông báo. Không cần chạy lại mọi ca âm/thiếu trường hoặc đăng nhập nhân viên thứ hai trong buổi speed run; dùng ảnh/báo cáo nếu được hỏi.

## Câu hỏi thường gặp

- **Mã phiếu không bắt đầu từ 0001?** Sequence tiếp tục tăng dù xóa dữ liệu thử, tránh tái dùng mã.
- **Nhân viên sửa hoặc xóa được gì?** Sửa nội dung khi Nháp; xóa phiếu của mình khi Nháp/Chờ duyệt. Có thể Rút yêu cầu đang Chờ duyệt để giữ lịch sử. Phiếu đã xử lý bị khóa với nhân viên.
- **Phân quyền kiểm tra ở đâu?** Máy chủ kiểm tra, không chỉ ẩn nút; nhân viên khác không đọc được phiếu và không thể tự duyệt.
- **Đã hoàn chỉnh chưa?** Luồng yêu cầu/phê duyệt đủ để demo. Cần đối chiếu bộ kiểm thử của nhóm và chạy lại trên máy thành viên trước nghiệm thu; nhập kho tự động là phần mở rộng cần chốt riêng.

Không cần thêm tính năng mới ngay trước buổi demo. Tập chuyển hai cửa sổ và nhận diện đúng mã phiếu một lượt là ưu tiên.
