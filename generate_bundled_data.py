import os
import mysql.connector
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="@Kk1332006",
    database="olist_raw",
    port=3306
)

print("[*] 1. Extracting Basket Type Summary...")
q1 = """
SELECT 
    basket_type,
    COUNT(*) AS total_orders,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS order_share_pct,
    ROUND(SUM(total_order_val), 2) AS total_gmv,
    ROUND(AVG(total_order_val), 2) AS aov,
    ROUND(AVG(total_items), 2) AS avg_items,
    ROUND(AVG(total_sellers), 2) AS avg_sellers,
    ROUND(AVG(TIMESTAMPDIFF(HOUR, order_purchase_timestamp, order_delivered_customer_date) / 24.0), 2) AS avg_delivery_days,
    ROUND(AVG(TIMESTAMPDIFF(HOUR, order_purchase_timestamp, order_delivered_carrier_date) / 24.0), 2) AS avg_handling_days,
    ROUND(AVG(TIMESTAMPDIFF(HOUR, order_delivered_carrier_date, order_delivered_customer_date) / 24.0), 2) AS avg_transit_days,
    ROUND(SUM(CASE WHEN order_delivered_customer_date > order_estimated_delivery_date THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS late_delivery_pct,
    ROUND(AVG(review_score), 2) AS avg_review_score,
    ROUND(SUM(CASE WHEN review_score = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS pct_1_star,
    ROUND(AVG(freight_val / NULLIF(item_val, 0)) * 100, 2) AS freight_burden_pct
FROM (
    SELECT 
        o.order_id,
        o.order_purchase_timestamp,
        o.order_delivered_carrier_date,
        o.order_delivered_customer_date,
        o.order_estimated_delivery_date,
        COUNT(oi.order_item_id) AS total_items,
        COUNT(DISTINCT oi.seller_id) AS total_sellers,
        CASE 
            WHEN COUNT(oi.order_item_id) = 1 THEN '1. Don Don (Single Item)'
            WHEN COUNT(oi.order_item_id) > 1 AND COUNT(DISTINCT oi.seller_id) = 1 THEN '2. Don Gop Cung Seller'
            ELSE '3. Don Gop Da Seller'
        END AS basket_type,
        SUM(oi.price) AS item_val,
        SUM(oi.freight_value) AS freight_val,
        SUM(oi.price + oi.freight_value) AS total_order_val,
        AVG(r.review_score) AS review_score
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    LEFT JOIN reviews r ON o.order_id = r.order_id
    WHERE o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL
      AND o.order_delivered_carrier_date IS NOT NULL
    GROUP BY o.order_id, o.order_purchase_timestamp, o.order_delivered_carrier_date, o.order_delivered_customer_date, o.order_estimated_delivery_date
) sub
GROUP BY basket_type
ORDER BY basket_type;
"""
df_basket_summary = pd.read_sql(q1, conn)

print("[*] 2. Extracting Basket Type x SLA Cross Tab...")
q2 = """
SELECT 
    basket_type,
    is_late,
    COUNT(*) AS total_orders,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(PARTITION BY basket_type), 2) AS pct_within_basket,
    ROUND(AVG(review_score), 2) AS avg_review_score,
    ROUND(SUM(CASE WHEN review_score = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS pct_1_star,
    ROUND(AVG(total_order_val), 2) AS aov,
    ROUND(AVG(TIMESTAMPDIFF(HOUR, order_purchase_timestamp, order_delivered_customer_date) / 24.0), 2) AS avg_delivery_days
FROM (
    SELECT 
        o.order_id,
        o.order_purchase_timestamp,
        o.order_delivered_customer_date,
        o.order_estimated_delivery_date,
        CASE 
            WHEN COUNT(oi.order_item_id) = 1 THEN '1. Don Don'
            WHEN COUNT(oi.order_item_id) > 1 AND COUNT(DISTINCT oi.seller_id) = 1 THEN '2. Don Gop 1 Seller'
            ELSE '3. Don Gop Da Seller'
        END AS basket_type,
        CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 'Tre Han (Late)' ELSE 'Dung Han (On-time)' END AS is_late,
        SUM(oi.price + oi.freight_value) AS total_order_val,
        AVG(r.review_score) AS review_score
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    LEFT JOIN reviews r ON o.order_id = r.order_id
    WHERE o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL
    GROUP BY o.order_id, o.order_purchase_timestamp, o.order_delivered_customer_date, o.order_estimated_delivery_date
) sub
GROUP BY basket_type, is_late
ORDER BY basket_type, is_late;
"""
df_crosstab = pd.read_sql(q2, conn)

print("[*] 3. Extracting Item Count Tiers...")
q3 = """
SELECT 
    CASE 
        WHEN total_items = 1 THEN '1. Don 1 mon'
        WHEN total_items = 2 THEN '2. Don 2 mon'
        WHEN total_items BETWEEN 3 AND 5 THEN '3. Don 3-5 mon'
        ELSE '4. Don tren 5 mon'
    END AS item_bundle_tier,
    COUNT(*) AS total_orders,
    ROUND(SUM(total_order_val), 2) AS total_gmv,
    ROUND(AVG(total_order_val), 2) AS aov,
    ROUND(AVG(TIMESTAMPDIFF(HOUR, order_purchase_timestamp, order_delivered_customer_date) / 24.0), 2) AS avg_delivery_days,
    ROUND(AVG(TIMESTAMPDIFF(HOUR, order_purchase_timestamp, order_delivered_carrier_date) / 24.0), 2) AS avg_handling_days,
    ROUND(AVG(TIMESTAMPDIFF(HOUR, order_delivered_carrier_date, order_delivered_customer_date) / 24.0), 2) AS avg_transit_days,
    ROUND(SUM(CASE WHEN order_delivered_customer_date > order_estimated_delivery_date THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS late_delivery_pct,
    ROUND(AVG(review_score), 2) AS avg_review_score,
    ROUND(SUM(CASE WHEN review_score = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS pct_1_star
FROM (
    SELECT 
        o.order_id,
        o.order_purchase_timestamp,
        o.order_delivered_carrier_date,
        o.order_delivered_customer_date,
        o.order_estimated_delivery_date,
        COUNT(oi.order_item_id) AS total_items,
        SUM(oi.price + oi.freight_value) AS total_order_val,
        AVG(r.review_score) AS review_score
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    LEFT JOIN reviews r ON o.order_id = r.order_id
    WHERE o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL
      AND o.order_delivered_carrier_date IS NOT NULL
    GROUP BY o.order_id, o.order_purchase_timestamp, o.order_delivered_carrier_date, o.order_delivered_customer_date, o.order_estimated_delivery_date
) sub
GROUP BY item_bundle_tier
ORDER BY item_bundle_tier;
"""
df_item_tiers = pd.read_sql(q3, conn)

print("[*] 4. Extracting Seller Count Tiers...")
q4 = """
SELECT 
    CASE 
        WHEN total_sellers = 1 THEN '1. Don 1 Seller'
        WHEN total_sellers = 2 THEN '2. Don 2 Sellers'
        ELSE '3. Don 3+ Sellers'
    END AS seller_tier,
    COUNT(*) AS total_orders,
    ROUND(SUM(total_order_val), 2) AS total_gmv,
    ROUND(AVG(total_order_val), 2) AS aov,
    ROUND(AVG(TIMESTAMPDIFF(HOUR, order_purchase_timestamp, order_delivered_customer_date) / 24.0), 2) AS avg_delivery_days,
    ROUND(SUM(CASE WHEN order_delivered_customer_date > order_estimated_delivery_date THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS late_delivery_pct,
    ROUND(AVG(review_score), 2) AS avg_review_score,
    ROUND(SUM(CASE WHEN review_score = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS pct_1_star
FROM (
    SELECT 
        o.order_id,
        o.order_purchase_timestamp,
        o.order_delivered_customer_date,
        o.order_estimated_delivery_date,
        COUNT(DISTINCT oi.seller_id) AS total_sellers,
        SUM(oi.price + oi.freight_value) AS total_order_val,
        AVG(r.review_score) AS review_score
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    LEFT JOIN reviews r ON o.order_id = r.order_id
    WHERE o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL
    GROUP BY o.order_id, o.order_purchase_timestamp, o.order_delivered_customer_date, o.order_estimated_delivery_date
) sub
GROUP BY seller_tier
ORDER BY seller_tier;
"""
df_seller_tiers = pd.read_sql(q4, conn)
conn.close()

os.makedirs('data_bi', exist_ok=True)
df_basket_summary.to_csv('data_bi/fact_bundle_summary.csv', index=False, encoding='utf-8')
df_crosstab.to_csv('data_bi/fact_bundle_sla_crosstab.csv', index=False, encoding='utf-8')
df_item_tiers.to_csv('data_bi/fact_bundle_item_tiers.csv', index=False, encoding='utf-8')
df_seller_tiers.to_csv('data_bi/fact_bundle_seller_tiers.csv', index=False, encoding='utf-8')
print("[+] CSV Data Marts saved.")

wb = openpyxl.Workbook()
navy_header_fill = PatternFill(start_color='0A192F', end_color='0A192F', fill_type='solid')
sub_header_fill = PatternFill(start_color='1E293B', end_color='1E293B', fill_type='solid')
white_font_bold = Font(name='Calibri', size=11, bold=True, color='FFFFFF')
title_font = Font(name='Calibri', size=16, bold=True, color='0A192F')
subtitle_font = Font(name='Calibri', size=10, italic=True, color='475569')
regular_font = Font(name='Calibri', size=10)
bold_font = Font(name='Calibri', size=10, bold=True)

thin_border = Border(
    left=Side(style='thin', color='CBD5E1'),
    right=Side(style='thin', color='CBD5E1'),
    top=Side(style='thin', color='CBD5E1'),
    bottom=Side(style='thin', color='CBD5E1')
)

def style_sheet(ws, title, subtitle, df, num_formats):
    ws.views.sheetView[0].showGridLines = True
    ws['A1'] = title
    ws['A1'].font = title_font
    ws['A2'] = subtitle
    ws['A2'].font = subtitle_font
    
    headers = list(df.columns)
    start_row = 4
    for col_idx, col_name in enumerate(headers, 1):
        cell = ws.cell(row=start_row, column=col_idx, value=col_name.replace('_', ' ').title())
        cell.fill = navy_header_fill
        cell.font = white_font_bold
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.border = thin_border
    
    for r_idx, row_data in enumerate(df.values, start_row + 1):
        for c_idx, val in enumerate(row_data, 1):
            cell = ws.cell(row=r_idx, column=c_idx, value=val)
            cell.font = regular_font
            cell.border = thin_border
            col_name = headers[c_idx - 1]
            if col_name in num_formats:
                cell.number_format = num_formats[col_name]
                cell.alignment = Alignment(horizontal='right', vertical='center')
            elif isinstance(val, (int, float)):
                cell.alignment = Alignment(horizontal='right', vertical='center')
            else:
                cell.alignment = Alignment(horizontal='left', vertical='center')
    
    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = max(len(str(cell.value or '')) for cell in col)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 13)

formats = {
    'total_orders': '#,##0',
    'order_share_pct': '0.00%',
    'total_gmv': 'R$ #,##0.00',
    'aov': 'R$ #,##0.00',
    'avg_items': '0.00',
    'avg_sellers': '0.00',
    'avg_delivery_days': '0.0',
    'avg_handling_days': '0.0',
    'avg_transit_days': '0.0',
    'late_delivery_pct': '0.00%',
    'avg_review_score': '0.00',
    'pct_1_star': '0.00%',
    'pct_within_basket': '0.00%',
    'freight_burden_pct': '0.00%'
}

ws1 = wb.active
ws1.title = 'Executive Summary'
ws1.views.sheetView[0].showGridLines = True
ws1['A1'] = 'OLIST BUNDLED VS SINGLE ORDER SLA & REVIEW AUDIT'
ws1['A1'].font = title_font
ws1['A2'] = 'Chan doan nghich ly giao don gop: Toc do giao nhanh nhat nhung ty le danh gia 1-sao cao nhat'
ws1['A2'].font = subtitle_font

kpis = [
    ('Tong Don Hang Phan Tich', 96478, '#,##0'),
    ('Ty Trong Don Don (Single Item)', 89.54, '0.00%'),
    ('Ty Trong Don Gop Cung Seller', 9.13, '0.00%'),
    ('Ty Trong Don Gop Da Seller', 1.32, '0.00%'),
    ('Ty Le Tre Han Don Don (%)', 8.29, '0.00%'),
    ('Ty Le Tre Han Don Gop Da Seller (%)', 1.41, '0.00%'),
    ('Ty Le 1-Sao Don Don (%)', 8.43, '0.00%'),
    ('Ty Le 1-Sao Don Gop Da Seller (%)', 35.22, '0.00%')
]

for idx, (label, val, fmt) in enumerate(kpis, 4):
    ws1.cell(row=idx, column=1, value=label).font = white_font_bold
    ws1.cell(row=idx, column=1).fill = sub_header_fill
    c = ws1.cell(row=idx, column=2, value=val)
    c.font = bold_font
    c.number_format = fmt
    c.alignment = Alignment(horizontal='right')
    c.border = thin_border
    ws1.row_dimensions[idx].height = 24

ws1.column_dimensions['A'].width = 40
ws1.column_dimensions['B'].width = 25

ws2 = wb.create_sheet('Basket Type Overview')
style_sheet(ws2, 'So Sanh Toan Dien Don Don vs Don Gop', 'Hieu nang van hanh logistics va danh gia chat luong', df_basket_summary, formats)

ws3 = wb.create_sheet('Basket x SLA Crosstab')
style_sheet(ws3, 'Doi Chieu Gio Hang x Tinh Trang Giao Tre', 'Ty le 1-sao va diem review khi don hang giao dung han vs tre han', df_crosstab, formats)

ws4 = wb.create_sheet('Item Count Tiers')
style_sheet(ws4, 'Phan Tang Theo So Luong Mon Hang', 'Moi quan he giua quy mo gio hang va su sut giam diem review', df_item_tiers, formats)

ws5 = wb.create_sheet('Seller Tiers')
style_sheet(ws5, 'Phan Tang Theo So Luong Seller Trong Don', 'Tac dong cua so luong seller doi voi diem danh gia', df_seller_tiers, formats)

excel_file = 'Olist_Bundled_Orders_SLA_Analysis.xlsx'
wb.save(excel_file)
print('[+] Excel file saved: ' + excel_file)