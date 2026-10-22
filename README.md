# Minesweeper AI 

Python 3.10+.

## Chạy demo

Mở Terminal trong thư mục này, chạy:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python runner.py
```

Mặc định: 8×8, 10 mìn, seed 11. Có thể chọn seed: `python runner.py --seed 42`.
Tọa độ trong bảng suy luận bắt đầu từ 0, theo `(hàng, cột)`.

- **Space / Step**: AI chọn một nước và cập nhật suy luận. Mở ô 0 có thể mở thêm cả vùng.
- **A / Auto**: chạy tự động, khoảng 450 ms mỗi nước.
- **R / Replay**: tạo lại cùng seed. **N / New**: seed mới.
- **1**: 8×8, 10 mìn. **2**: 9×9, 15 mìn.
- Click trái: mở ô. Click phải: bật/tắt cờ của người chơi.
- Chấm xanh: ô AI chứng minh an toàn. F đỏ: mìn AI suy ra. F vàng: cờ người chơi.
- Cờ người chơi chỉ là ghi chú, không được đưa vào tri thức của AI. AI có thể mở ô được người chơi cắm cờ nếu suy ra an toàn hoặc chọn đoán.
- Ô có viền vàng: nước vừa đi. Bảng phải hiện ràng buộc và lịch sử suy luận.

## Luồng hoạt động và phân công

| Phần | Nơi đọc mã | Đã có trong draft |
|---|---|---|
| 1. Biểu diễn tri thức | `Sentence` trong `minesweeper.py` | Tập ô + số mìn, `known_mines`, `known_safes`, `mark_mine`, `mark_safe` |
| 2. Suy luận | `MinesweeperAI.infer` | Luật count=0, count=len(cells), hiệu hai tập con; lặp đến khi không còn tri thức mới; bỏ ràng buộc trống/trùng |
| 3. Ra quyết định | `add_knowledge`, `make_safe_move`, `make_random_move` | Cập nhật clue, ưu tiên ô chắc chắn an toàn, đoán đều trên ô chưa mở chưa biết là mìn |
| 4. Tích hợp, đánh giá | `DemoSession`, `runner.py`, `benchmark.py`, `tests/` | GUI, chạy từng bước/tự động, CSV, kiểm thử logic |

Ví dụ suy luận: `{A,B}=1` và `{A,B,C}=1` → `{C}=0` → C an toàn.
Nếu thêm `{C,D}=1`, việc cập nhật C an toàn sẽ suy ra D là mìn.

Game giữ bản đồ mìn; agent chỉ nhận `(ô vừa mở, số mìn lân cận)`.
`DemoSession` chuyển các clue mới từ game sang AI. GUI chỉ hiện mìn thật sau khi kết thúc.
AI dùng ràng buộc đếm chính xác trên các biến Boolean, không có bộ giải SAT tổng quát.

## Quy ước và giới hạn draft

- Lượt mở đầu luôn an toàn: game sinh mìn sau click đầu và loại ô đó khỏi vị trí đặt mìn. Các ô lân cận vẫn có thể có mìn.
- Thắng khi mở hết ô không có mìn; không yêu cầu người chơi cắm đủ cờ.
- Khi suy luận không tìm được nước an toàn, AI **đoán ngẫu nhiên**, có thể thua. Chưa có ước lượng xác suất hay chiến lược tối thiểu hóa rủi ro.
- Chưa dùng tổng số mìn toàn bàn làm một ràng buộc bổ sung của agent.
- Chưa xử lý đồng thời nhiều lỗi dữ liệu đầu vào hay khôi phục sau mâu thuẫn; core báo `ValueError`, GUI dừng Auto và ghi lỗi.
- Bảng tri thức trên GUI chỉ hiện tối đa 5 ràng buộc và 8 sự kiện gần nhất; core giữ toàn bộ ràng buộc hiện tại.
- Thuật toán so sánh các cặp ràng buộc phù hợp bàn nhỏ; chưa đánh giá hiệu năng bàn lớn.

## Kiểm thử và lấy số liệu

Phần core và benchmark chỉ cần thư viện chuẩn Python; Pygame chỉ cần cho GUI.

```sh
python -m unittest discover -s tests -v
python benchmark.py --games 100 --seed 0 --output results/draft.csv
python runner.py --smoke-test --screenshot preview.png
```

Benchmark chạy `random` và `logic` trên cùng dải seed, cùng lượt đầu ở giữa bàn và cùng quy tắc mở vùng 0.
`random` chọn đều trong mọi ô chưa mở; `logic` tránh mìn đã suy ra và ưu tiên ô an toàn.
Cả hai hiện cùng cập nhật knowledge base để dùng chung controller; vì vậy cột thời gian **không phải** phép đo chi phí của một baseline random thuần túy.
Đây là so sánh tỷ lệ thắng ban đầu, chưa đủ để khẳng định chất lượng thuật toán.
`safe_moves` chỉ đếm nước do AI chủ động chọn từ tập an toàn; không đếm các ô tự mở theo vùng 0 hay lượt đầu được bảo vệ.
`guesses` không tính lượt đầu. CSV ghi seed, cấu hình, thắng/thua, số ô mở, số nước an toàn/đoán và số suy luận tập con.

Gợi ý kiểm tra trước khi duyệt: chạy từng bước, xem một dòng SUBSET; thử Auto đến thắng/thua; Replay cùng seed; tự chơi xen kẽ AI; chạy bộ test và xuất CSV.

## Có thể bổ sung sau khi nhóm duyệt

Ước lượng xác suất khi phải đoán, ràng buộc tổng số mìn, thống kê nhiều cấu hình,
giao diện tiếng Việt, cập nhật kết quả vào notebook giữa kỳ và ghi rõ đóng góp từng thành viên.
