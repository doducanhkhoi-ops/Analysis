# Olist E-Commerce Diagnostic & Strategic Analytics Engine
> **Dự án Nghiên cứu & Phân tích Dữ liệu Thương mại Điện tử Olist (Brazil)**  
> **Bộ môn:** Cơ sở dữ liệu (TINH313) · Đại học Ngoại thương (FTU) · Nhóm 6  
> **Phương pháp:** The Diagnostic Analyst Mindset (Luồng tư duy chẩn đoán 6 bước, Analysis-First, Anti-Cringe & Zero AI Watermark)  
> **Mô hình triển khai:** Cục bộ (Local Machine Execution) · Chia sẻ kiến trúc mã nguồn mở (Architecture Showcase)

---

## 📌 1. Mục Đích Kho Lưu Trữ

Kho lưu trữ được thiết kế nhằm chia sẻ cấu trúc mã nguồn, tư duy kỹ thuật và cơ chế vận hành của một hệ thống chẩn đoán dữ liệu thương mại điện tử chuyên sâu. Toàn bộ mã nguồn tập trung vào:
1. **Khai thác dữ liệu thực chứng:** Dựa trên CSDL sàn thương mại điện tử Olist (`olist_raw`) với quy mô hơn 100.000 đơn hàng thực tế tại Brazil (2016–2018).
2. **Động cơ phân tích tự động (`strategic_report_flow.py`):** Tự động truy vấn SQL đa chiều, đo lường các nghịch lý kinh doanh, tính toán KPI, render báo cáo HTML và gửi qua Gmail SMTP.
3. **Báo cáo Dashboard HTML tương tác sâu (Bespoke Interactive HTML Dashboards):** Trực quan hóa dữ liệu độc lập với khả năng lọc 2 chiều giữa Slicer và Biểu đồ, đào sâu bản chất vấn đề thay vì dừng lại ở thống kê mô tả.

---

## 🗂️ 2. Cấu Trúc Mã Nguồn Chuẩn Hóa

```text
├── reports/
│   ├── payment_financing_diagnostic.html # Dashboard tương tác: Ma trận thanh toán & bẫy trả góp 10 kỳ
│   ├── year_end_logistics_diagnostic.html# Dashboard tương tác: Logistics & đứt gãy mùa cao điểm
│   └── Olist_Executive_Strategic_Report.html # Báo cáo điều hành tổng thể
├── .env.example                         # File mẫu tham số kết nối MySQL & Gmail SMTP
├── .gitignore                           # Danh mục loại trừ dữ liệu nặng (>100MB), installer và cache
├── requirements.txt                     # Danh mục thư viện Python tối giản
├── check_db_connection.py               # Script kiểm tra kết nối CSDL và đối soát số dòng các bảng
├── strategic_report_flow.py             # Động cơ phân tích tự động trung tâm (Core Engine)
├── AnalyticFlow.md                      # Chuẩn tư duy phân tích chẩn đoán 6 bước
├── GEMINI.md                            # Quy chuẩn chất lượng hiển thị và triệt tiêu AI watermark
└── README.md                            # Tài liệu thuyết minh kiến trúc và hướng dẫn cài đặt
```

### Quy ước quản lý tệp tin (File Management):
* **Tệp BẮT BUỘC có trên GitHub:** 7 thành phần cấu trúc ở trên (Mã nguồn, script kiểm thử, tài liệu phân tích và dashboard mẫu).
* **Tệp ĐÃ LOẠI TRỪ khỏi GitHub (`.gitignore`):**
  - `olist_dump.sql` (159 MB) & `OLIST.zip` (44 MB): GitHub từ chối tệp tin vượt quá 100 MB. Người dùng nạp dữ liệu từ file dump cục bộ vào MySQL cá nhân.
  - `.env`: Chứa mật khẩu máy chủ và mật khẩu ứng dụng Gmail của cá nhân.
  - Bộ cài đặt `.msi`, sách giáo trình PDF, thư mục `__pycache__/`, môi trường ảo `venv/` và các tệp CSV xuất bản tạm thời (`olist_strategic_*.csv`).

---

## ⚙️ 3. Cơ Chế Vận Hành Của Động Cơ Phân Tích (`strategic_report_flow.py`)

Hệ thống hoạt động theo mô hình xoay vòng trạng thái khép kín (State-based Diagnostic Loop):

```text
[Local MySQL Database: olist_raw]
            │
            ▼
[Query Dispatcher: 6 Chuyên Đề Chiến Lược]
            │
            ▼
[Data-Driven Heuristics / Gemini AI Engine]
 (Phát hiện nghịch lý, đo lường độ lệch, truy tìm căn nguyên)
            │
            ▼
[HTML Dashboard Builder] ──► [CSV Exporter]
            │
            ▼
[Gmail SMTP Dispatcher] ──► Hộp thư Giám đốc Chiến lược
```

### Sáu Chuyên Đề Chiến Lược Được Tích Hợp:
1. **`rfm` (Vòng đời & Phân khúc khách hàng):** Bóc tách 11 phân khúc RFM, định vị tỷ lệ khách hàng có nguy cơ rời bỏ (*About to Sleep*, *Hibernating*, *Lost* chiếm trên 60%) và đo lường tỷ lệ mua lại thực tế (*Repeat Purchase Rate* cực thấp ~3%).
2. **`seller` (Ma trận năng lực người bán):** Phân tích tương quan Volume vs Value giữa Seller Đa vùng (*Multi-region*) và Đơn vùng (*Single-region*); chỉ ra nguy cơ tập trung doanh thu khi 20% seller gánh 80% GMV toàn sàn.
3. **`basket` (Hành vi giỏ hàng & Nghịch lý Multi-seller):** Chứng minh nghịch lý: đơn hàng gồm nhiều shop khác nhau (*Multi-seller*) có AOV cao hơn +62.3% và tỷ lệ giao trễ thấp hơn đơn 1 shop (1.41% vs 8.20%).
4. **`category` (Sức khỏe ngành hàng & Danh mục đuôi dài):** Sàng lọc danh mục có nguy cơ bị gỡ bỏ theo bộ tiêu chuẩn 3/3 (Doanh số thấp, Đánh giá dưới 3.5 sao, Tỷ lệ hủy/hoàn cao).
5. **`logistics` (Vận hành giao vận theo địa lý):** Đo lường SLA giao trễ, độ lệch giữa ngày hẹn ước tính và thực tế nhận hàng, bóc tách gánh nặng chi phí vận chuyển tại các bang Đông Bắc và miền Bắc Brazil.
6. **`payment` (Cơ cấu thanh toán & Đòn bẩy tài chính):** Mổ xẻ hiện tượng trả góp dài hạn (>6 đến 10 kỳ) giúp nhân đôi AOV nhưng gia tăng áp lực thanh khoản và rủi ro gián đoạn giao hàng.

---

## 🚀 4. Hướng Dẫn Cài Đặt & Vận Hành Cục Bộ (Local Machine)

### Bước 1: Khởi Tạo Cơ Sở Dữ Liệu `olist_raw` Trên MySQL Local
1. Mở MySQL Workbench hoặc Command Prompt/PowerShell.
2. Tạo database và nạp dữ liệu từ file dump cục bộ:
   ```bash
   # Tạo database với bảng mã UTF-8 đầy đủ
   mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS olist_raw CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

   # Nạp dữ liệu (Yêu cầu file olist_dump.sql có sẵn trong thư mục máy tính)
   mysql -u root -p olist_raw < olist_dump.sql
   ```

### Bước 2: Chuẩn Bị Môi Trường Python
Chạy môi trường Python (khuyến nghị bản 3.10 – 3.12) và cài đặt gói kết nối:
```bash
pip install -r requirements.txt
```

### Bước 3: Cấu Hình Tệp Môi Trường (`.env`)
Sao chép `.env.example` thành `.env` tại thư mục gốc và điền thông tin máy chủ MySQL cục bộ:
```ini
# Cấu hình kết nối MySQL Localhost
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=Mật_khẩu_MySQL_của_bạn
DB_NAME=olist_raw

# Cấu hình gửi Email báo cáo (Tùy chọn nếu muốn nhận email thực tế)
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
EMAIL_TO=recipient@gmail.com
```
*(Ghi chú: `GMAIL_APP_PASSWORD` là Mật khẩu ứng dụng 16 ký tự do Google cấp, không phải mật khẩu đăng nhập cá nhân).*

### Bước 4: Kiểm Tra Tình Trạng Kết Nối & Dữ Liệu
Chạy script kiểm tra để chắc chắn mọi bảng dữ liệu đã sẵn sàng:
```bash
python check_db_connection.py
```
**Đầu ra chuẩn xác:**
```text
======================================================================
OLIST STRATEGIC ANALYTICS: DATABASE CONNECTION CHECK
======================================================================
[*] Target Host : localhost:3306
[*] Target User : root
[*] Target DB   : olist_raw
----------------------------------------------------------------------
[+] Ket noi thanh cong! MySQL Server Version: 8.0.xx

[*] Kiem tra trang thai du lieu cac bang:
Table Name                   | Resolved Table       | Row Count    | Status
----------------------------------------------------------------------
orders                       | orders               | 99,441       | READY
order_items                  | order_items          | 112,650      | READY
payments                     | payments             | 103,886      | READY
products                     | products             | 32,951       | READY
reviews                      | reviews              | 99,224       | READY
customers                    | customers            | 99,441       | READY
sellers                      | sellers              | 3,095        | READY
category_translation         | category_translation | 71           | READY
geolocation                  | geolocation          | 1,000,163    | READY
analytics_rfm_segments       | analytics_rfm_segments | 93,358       | READY
----------------------------------------------------------------------
[+] He thong san sang de thuc thi toan bo luong truy van va bao cao!
======================================================================
```

### Bước 5: Thực Thi Xuất Báo Cáo
Chạy script thực thi trực tiếp tại terminal:
```bash
# 1. Chạy tự động xoay vòng chuyên đề
python strategic_report_flow.py

# 2. Hoặc chỉ định trực tiếp chuyên đề cụ thể
python strategic_report_flow.py payment     # Chuyên đề Tài chính & Thanh toán
python strategic_report_flow.py seller      # Chuyên đề Hiệu suất Người bán
python strategic_report_flow.py rfm         # Chuyên đề Phân khúc Khách hàng
python strategic_report_flow.py basket      # Chuyên đề Giỏ hàng & Multi-seller
python strategic_report_flow.py category    # Chuyên đề Danh mục Sản phẩm
python strategic_report_flow.py logistics   # Chuyên đề Vận hành Logistics
```
Sau 8–10 giây, file CSV số liệu sẽ tự động xuất ra thư mục hiện hành và nội dung email HTML chuyên nghiệp sẽ được chuyển đến hộp thư nhận.

---

## 🖥️ 5. Trực Quan Hóa Báo Cáo HTML Tương Tác Sâu (`reports/`)

Các báo cáo được xuất bản tại thư mục `reports/` (tiêu biểu: `reports/payment_financing_diagnostic.html`) tuân thủ nghiêm ngặt nguyên tắc thiết kế chống sáo rỗng (Anti-Cringe) và trực quan hóa dữ liệu thực chất:
* **Slicer Động:** Lọc phân khúc nhanh gọn (`Tất cả`, `Thẻ tín dụng`, `Boleto`, `Voucher`, `Thẻ ghi nợ`).
* **Cross-filtering 2 Chiều (Bi-directional):** Bấm chọn trên Slicer cập nhật biểu đồ và bảng; click trực tiếp vào lát cắt trên Doughnut Chart sẽ cập nhật ngược lại Slicer.
* **Góc Nhìn Đối Chuẩn Động (Benchmark View):** Khi chọn phương thức thanh toán 1 lần, biểu đồ tự động chuyển sang so sánh đối chuẩn với các kỳ hạn trả góp và trung bình toàn sàn.
* **Định Vị Căn Bệnh Cốt Lõi:** Phân tích cặn kẽ 3 nút thắt chí tử của mô hình kinh doanh Olist thay vì chỉ liệt kê các khuyến nghị sáo rỗng.
* **Tiện Ích Bản In & Mã Lệnh:** Tích hợp nút sao chép câu lệnh SQL thực thi từng phần và CSS tối ưu định dạng in/PDF chuẩn phòng họp ban giám đốc.

---

## 📜 6. Giấy Phép & Bản Quyền

Dự án phục vụ mục đích nghiên cứu học thuật, chia sẻ tri thức phân tích dữ liệu ứng dụng và trình diễn năng lực kỹ thuật cơ sở dữ liệu. Dữ liệu gốc thuộc bản quyền công khai của sàn thương mại điện tử Olist trên nền tảng Kaggle.
