# Olist Diagnostic: Nghịch Lý Giao Đơn Gộp vs Đơn Đơn & Sụp Đổ Đánh Giá Review
*(Bundled Orders Logistics SLA Audit & Review Collapse Paradox)*

Thư mục này đóng gói trọn vẹn toàn bộ ấn phẩm phân tích chuyên sâu, mô hình dữ liệu và mã nguồn tự động hóa cho chuyên đề **Chẩn đoán Đơn Gộp vs Đơn Đơn trên 96,478 đơn hàng delivered** của sàn thương mại điện tử Olist Brazil.

---

## 📂 Danh Mục Tài Nguyên Trong Thư Mục

| Hạng mục | Tên Tệp Tin | Mô Tả Nghiệp Vụ |
| :--- | :--- | :--- |
| **Báo Cáo Dashboard HTML** | `Olist_Bundled_Orders_Cockpit.html` | Báo cáo giao diện chuyển trang Tab/Slide, tích hợp Chart.js, bộ lọc Slicer động 2 chiều, copy SQL trực tiếp. |
| **Sổ Báo Cáo Excel** | `Olist_Bundled_Orders_SLA_Analysis.xlsx` | Sổ cái 5 sheet phân tích chuẩn tài chính: Executive Summary, Basket Types, Crosstab SLA, Item Tiers, Seller Tiers. |
| **Dự Án Power BI PBIP** | `reports/Bundled_Orders_Diagnostic.pbip` | Mô hình Microsoft Fabric PBIP (PBIR + TMDL), theme Dark Slate/Midnight Navy, 12 visuals tự động, validate 0 lỗi. |
| **Kho Data Mart CSV** | `data_bi/fact_bundle_*.csv` | 4 bảng dữ liệu tổng hợp siêu nhẹ (Summary, SLA Crosstab, Item Tiers, Seller Tiers). |
| **Mã Nguồn Khai Thác & Dựng** | `generate_bundled_data.py`<br>`build_adapted_bundled_pbip.py` | Pipeline trích xuất SQL từ MySQL `olist_raw` và dựng toàn bộ kiến trúc Fabric PBIP. |

---

## 🧭 Phát Hiện Nghiệp Vụ Cốt Lõi (Core Insights)

1. **Nghịch Lý Vận Tải vs Đánh Giá Review:**
   - Đơn gộp đa người bán (*Multi-Sellers Bundled*) được giao nhanh hơn **3.5 ngày** (9.12 ngày vs 12.61 ngày) và tỷ lệ vi phạm SLA trễ hạn chỉ **1.41%** (so với 8.29% của đơn đơn).
   - Tuy nhiên, điểm đánh giá của khách hàng lại **sụp đổ nghiêm trọng từ 4.21 sao xuống 2.85 sao**, và tỷ lệ khách hàng chấm 1 sao tăng vọt từ **8.43% lên 35.22%**.

2. **Bằng Chứng Thực Nghiệm Từ Ma Trận SLA Chéo:**
   - Dù đơn gộp đa người bán được giao **đúng hạn trong 8.88 ngày** (chiếm 98.59% số đơn), **tỷ lệ 1-sao vẫn đạt mức báo động 34.84%** (gấp 7 lần so với tỷ lệ 5.14% 1-sao của đơn đơn on-time).
   - Điều này chứng minh 100% sự bất mãn của khách hàng **không hề xuất phát từ lỗi giao trễ bưu cục**, mà do trải nghiệm nhận hàng tách kiện phân mảnh (*Split-Shipment Anxiety*) và cơ chế một form review chung kéo sập điểm toàn bộ đơn do mắt xích người bán yếu nhất (*Weakest-Link Friction*).

---

## 🛠️ Hướng Dẫn Sử Dụng & Mở Nhanh

- **Mở Dashboard Web**: Click đúp vào `Olist_Bundled_Orders_Cockpit.html` để mở trực tiếp trên Chrome/Edge/Firefox. Dùng phím mũi tên `←`/`→` để chuyển chặng phân tích.
- **Mở Báo Cáo Excel**: Mở `Olist_Bundled_Orders_SLA_Analysis.xlsx` để xem các bảng pivot và số liệu chi tiết.
- **Mở Dự Án Power BI**: Mở file `reports/Bundled_Orders_Diagnostic.pbip` bằng Power BI Desktop. Bấm **[Làm mới ngay]** (hoặc `Alt + H + R`), dữ liệu từ thư mục `data_bi/` sẽ tự động đổ đầy toàn bộ biểu đồ.
