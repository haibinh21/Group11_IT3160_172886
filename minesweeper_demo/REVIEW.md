# Bản draft để nhóm duyệt

Bản draft được duyệt để đưa lên GitHub ngày 22/10/2026. Phạm vi và các phần tiếp tục phát triển ghi trong README.

## Kết quả kiểm tra tại máy

- 8 kiểm thử core: cập nhật câu logic, suy luận tập con và lan truyền tiếp,
  trừ mìn đã biết khỏi clue, phát hiện mâu thuẫn, mở vùng 0, bảo vệ lượt đầu,
  loại nước đi không hợp lệ và tái lập seed.
- Trong kiểm thử core có chạy 100 ván 6×6, 6 mìn, seed 0–99:
  so sánh tập safe/mine mà AI suy ra với đáp án thật sau mỗi nước.
- Kiểm tra GUI bằng màn hình ảo và chụp preview; kiểm thử sự kiện Step,
  đổi mức chơi, Replay và New. Chưa thử thao tác chuột bằng tay trên cửa sổ thật.
- Benchmark 100 seed 0–99, bàn 8×8, 10 mìn: `logic` thắng 61/100;
  `random` thắng 0/100. Trung bình số ô mở: 39.5 và 26.2.
  Quy tắc lượt đầu an toàn và mở vùng 0 giống nhau ở cả hai phương pháp.
  CSV gốc nằm ở `results/draft.csv`. Đây là số liệu thăm dò của một cấu hình,
  chưa phải kết luận tổng quát hay kết quả báo cáo cuối kỳ.

## Những điểm cần bạn xem

1. Cách chia `Sentence`, AI, game/controller, GUI và benchmark có phù hợp phân công không?
2. Bạn muốn giữ chiến lược đoán ngẫu nhiên cho giữa kỳ hay bổ sung xác suất?
3. Nhóm có muốn dùng luật thắng hiện tại: mở hết ô an toàn, cờ chỉ hỗ trợ đánh dấu?
4. Sau khi duyệt có thể đưa cả thư mục này vào repo; notebook báo cáo cập nhật ở bước riêng.
