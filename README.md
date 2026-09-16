# Olist E-Commerce Diagnostic & Strategic Analytics Engine
> **Dự án Nghiên cứu & Phân tích Dữ liệu Thương mại Điện tử Olist (Brazil)**  
> **Bộ môn:** Cơ sở dữ liệu (TINH313) · Đại học Ngoại thương (FTU) · Nhóm 6  
> **Phương pháp:** The Diagnostic Analyst Mindset (Luồng tư duy chẩn đoán 6 bước, Analysis-First, Anti-Cringe & Zero AI Watermark)

---

## 📌 Tổng Quan Dự Án

Kho lưu trữ chứa toàn bộ mã nguồn truy vấn SQL, luồng phân tích chẩn đoán kinh doanh đa chiều, hệ thống tự động hóa gửi báo cáo email hàng ngày qua GitHub Actions, và các báo cáo Dashboard HTML tương tác độc lập (Bespoke Interactive HTML Dashboards) xây dựng từ cơ sở dữ liệu thực tế sàn thương mại điện tử Olist (`olist_raw` với hơn 100,000 đơn hàng giai đoạn 2016–2018).

---

## 🗂️ Cấu Trúc Kho Lưu Trữ

```text
├── .github/
│   └── workflows/
│       └── strategic_report.yml         # GitHub Actions Cronjob (Chạy 08:00 AM VN hàng ngày)
├── reports/
│   ├── payment_financing_diagnostic.html # Dashboard HTML tương tác: Ma trận Thanh toán & Nghịch lý 10 kỳ
│   ├── year_end_logistics_diagnostic.html# Dashboard HTML tương tác: Chẩn đoán Logistics mùa cuối năm
│   ├── report_awesome_chocolates.html   # Báo cáo tham chiếu Awesome Chocolates
│   └── report_sakila.html               # Báo cáo tham chiếu Sakila
├── .env.example                         # File mẫu cấu hình biến môi trường
├── .gitignore                           # Danh mục loại trừ file nặng (>100MB) và cache
├── requirements.txt                     # Thư viện phụ thuộc Python
├── check_db_connection.py               # Script kiểm tra kết nối MySQL & đối soát bảng
├── strategic_report_flow.py             # Engine truy vấn SQL, render báo cáo & gửi Gmail SMTP
├── AnalyticFlow.md                      # Chuẩn tư duy phân tích 6 bước của Senior Data Analyst
├── GEMINI.md                            # Quy chuẩn tương tác và thiết kế hệ thống
└── README.md                            # Tài liệu hướng dẫn cài đặt & vận hành dự án
```

---

## 🚀 Hướng Dẫn Thiết Lập & Kết Nối CSDL MySQL (A - Z)

### Bước 1: Khởi Tạo Cơ Sở Dữ Liệu `olist_raw`

#### Lựa chọn A: Cài đặt Cục bộ (Local MySQL Server)
1. Đảm bảo MySQL Server (bản 8.0 trở lên) đang chạy trên máy (port mặc định `3306`).
2. Mở terminal hoặc PowerShell, tạo database và nạp dữ liệu từ file dump:
   ```bash
   # Đăng nhập MySQL và tạo database
   mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS olist_raw CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

   # Nạp dữ liệu từ olist_dump.sql (Lưu ý: file dung lượng ~159MB)
   mysql -u root -p olist_raw < olist_dump.sql
   ```
3. Sau khi import hoàn tất, database `olist_raw` sẽ bao gồm các bảng cốt lõi:
   - `orders` (99,441 dòng)
   - `order_items` (112,650 dòng)
   - `payments` (103,886 dòng)
   - `products` (32,951 dòng)
   - `reviews` (99,224 dòng)
   - `customers` (99,441 dòng)
   - `sellers` (3,095 dòng)
   - `category_translation` (71 dòng)
   - `geolocation` (1,000,163 dòng)

#### Lựa chọn B: Kết nối Cloud Database (Aiven MySQL / AWS RDS)
* Chuẩn bị thông tin kết nối từ nhà cung cấp: Hostname, Port (ví dụ `18064`), Username (`avnadmin`), Password và SSL CA Certificate (nếu bắt buộc).

---

### Bước 2: Cài Đặt Môi Trường Python

Khởi tạo môi trường ảo và cài đặt các thư viện cần thiết:
```bash
# Tạo môi trường ảo (tùy chọn)
python -m venv venv
# Kích hoạt trên Windows:
.\venv\Scripts\activate
# Kích hoạt trên Linux/macOS:
source venv/bin/activate

# Cài đặt thư viện từ requirements.txt
pip install -r requirements.txt
```

---

### Bước 3: Cấu Hình Biến Môi Trường (`.env`)

Sao chép file `.env.example` thành `.env` và điền thông số kết nối:
```bash
cp .env.example .env
```

Nội dung cấu hình chuẩn trong file `.env`:
```ini
# --- MySQL Database Configuration ---
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=Mật_khẩu_MySQL_của_bạn
DB_NAME=olist_raw

# --- Email Reporting (Gmail SMTP App Password) ---
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
EMAIL_TO=recipient@gmail.com
```

> **Lưu ý về Gmail App Password:** Sử dụng *Mật khẩu ứng dụng 16 ký tự* từ Google Account (Bảo mật -> Xác minh 2 bước -> Mật khẩu ứng dụng), không dùng mật khẩu đăng nhập Gmail thông thường.

---

### Bước 4: Kiểm Tra Kết Nối Tức Thì (Diagnostic Check)

Chạy script kiểm tra để xác nhận kết nối và tình trạng các bảng:
```bash
python check_db_connection.py
```

**Kết quả kỳ vọng khi thành công:**
```text
======================================================================
OLIST STRATEGIC ANALYTICS: DATABASE CONNECTION CHECK
======================================================================
[*] Target Host : localhost:3306
[*] Target User : root
[*] Target DB   : olist_raw
----------------------------------------------------------------------
[+] Ket noi thanh cong! MySQL Server Version: 8.0.42

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

---

## 📊 Vận Hành Hệ Thống Báo Cáo

### 1. Thực Thi Báo Cáo Chiến Lược Tự Động (`strategic_report_flow.py`)
Script tự động truy vấn MySQL, tạo báo cáo phân tích kèm định dạng trực quan và gửi trực tiếp qua email:
```bash
# Chạy xoay vòng chuyên đề tự động (State-based rotation)
python strategic_report_flow.py

# Chạy chỉ định chuyên đề cụ thể:
python strategic_report_flow.py rfm       # Phân khúc khách hàng RFM
python strategic_report_flow.py seller    # Năng lực người bán Đa vùng vs Đơn vùng
python strategic_report_flow.py basket    # Phân tích giỏ hàng & Đơn Multi-seller
python strategic_report_flow.py category  # Hiệu suất danh mục sản phẩm
python strategic_report_flow.py payment   # Ma trận thanh toán & Trả góp 10 kỳ
```

### 2. Tự Động Hóa Qua GitHub Actions (`.github/workflows/strategic_report.yml`)
Quy trình CI/CD tự động kích hoạt vào **08:00 sáng (Giờ Việt Nam)** mỗi ngày. Để vận hành trên GitHub:
1. Vào kho lưu trữ trên GitHub -> **Settings** -> **Secrets and variables** -> **Actions**.
2. Thêm các Secret:
   - `DB_HOST`: Hostname máy chủ MySQL (cần public IP hoặc Cloud DB)
   - `DB_PORT`: Cổng MySQL (mặc định 3306 hoặc port Cloud)
   - `DB_USER`: Tên người dùng MySQL
   - `DB_PASSWORD`: Mật khẩu người dùng MySQL
   - `DB_NAME`: Tên database (`olist_raw`)
   - `GMAIL_USER`: Địa chỉ Gmail gửi báo cáo
   - `GMAIL_APP_PASSWORD`: Mật khẩu ứng dụng 16 ký tự của Gmail
   - `EMAIL_TO`: Địa chỉ nhận báo cáo

---

## 🖥️ Khám Phá Dashboard HTML Tương Tác Sâu

Báo cáo trực quan độc lập được lưu trữ tại `reports/payment_financing_diagnostic.html`.

### Điểm nhấn kỹ thuật & nghiệp vụ:
* **Slicer: Phương thức thanh toán:** Thanh điều hướng lọc động giữa 4 phương thức (`Tất cả`, `Thẻ tín dụng`, `Boleto`, `Voucher`, `Thẻ ghi nợ`).
* **Bi-directional Cross-Filtering (Tương tác 2 chiều):**
  - Bấm chọn trên Slicer cập nhật KPI Hero Cards, lọc bảng dữ liệu và highlight biểu đồ.
  - Click trực tiếp vào bất kỳ lát cắt nào trên **Biểu đồ tròn (Doughnut Share)** sẽ kích hoạt ngược lại Slicer và cập nhật toàn bộ trang.
* **Biểu đồ Đối chuẩn Động (Dynamic Benchmark Chart):** Khi chọn các phương thức đơn kỳ (`Boleto`, `Voucher`, `Thẻ ghi nợ`), Biểu đồ 2 tự động chuyển đổi thành mô hình đối chuẩn (Benchmark View), so sánh trực tiếp chỉ số của phương thức đó với các nấc kỳ hạn Thẻ tín dụng và trung bình sàn.
* **Tab 5 - Định Vị Căn Bệnh Cốt Lõi:** Tổng hợp chẩn đoán 3 căn bệnh cấu trúc của Olist (Đứt gãy dòng tiền Boleto, Vòng lặp vết thương tài chính trả góp 10 kỳ, Đánh đổi tăng trưởng bằng rủi ro chất lượng vận chuyển).
* **Copyable SQL & In ấn:** Tích hợp nút Copy mã SQL từng phần và CSS tối ưu định dạng in/xuất PDF chuẩn báo cáo điều hành.

---

## 📦 Danh Mục Các Tệp Cần Cập Nhật Lên GitHub

| Tệp tin | Trạng thái | Mô tả nội dung cập nhật |
| :--- | :---: | :--- |
| `README.md` | **MỚI** | Hướng dẫn toàn diện từ kết nối MySQL, cấu trúc dự án, chạy code đến dashboard |
| `.gitignore` | **MỚI** | Chặn các file dump nặng (`olist_dump.sql` ~159MB), file cài đặt `.msi`, `.pbix`, cache |
| `.env.example` | **MỚI** | File mẫu cấu hình biến môi trường kết nối MySQL và Gmail SMTP |
| `check_db_connection.py` | **MỚI** | Script kiểm tra kết nối MySQL và tình trạng 10 bảng dữ liệu chính |
| `reports/payment_financing_diagnostic.html` | **CẬP NHẬT** | Dashboard HTML hoàn chỉnh với Slicer tương tác 2 chiều và Tab 5 chẩn đoán cốt lõi |
| `GEMINI.md` | **CẬP NHẬT** | Cập nhật quy tắc: Ngôn ngữ tinh gọn chống cringe, tương tác biểu đồ sâu, bắt buộc kết luận |
| `AnalyticFlow.md` | **CẬP NHẬT** | Đồng bộ quy chuẩn luồng tư duy phân tích chẩn đoán 6 bước |
| `.agents/rules/AnalyticFlow.md` | **CẬP NHẬT** | Đồng bộ rule hệ thống |

---

## 🛠️ Hướng Dẫn Lệnh Git Để Đẩy Cập Nhật Lên GitHub

Sau khi cài đặt Git trên máy (hoặc thông qua GitHub Desktop):

```bash
# 1. Kiểm tra trạng thái các tệp đã sửa đổi
git status

# 2. Thêm các tệp cập nhật vào Staging (đã được .gitignore bảo vệ khỏi file >100MB)
git add README.md .gitignore .env.example check_db_connection.py GEMINI.md AnalyticFlow.md .agents/ reports/payment_financing_diagnostic.html

# 3. Tạo commit với thông điệp chuẩn hóa
git commit -m "feat: complete mysql connectivity guide, interactive diagnostic dashboard and clean rules"

# 4. Đẩy mã nguồn lên branch chính (main hoặc master)
git push origin main
```
