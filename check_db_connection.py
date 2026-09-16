"""
Diagnostic Database Connection Verifier
Script kiem tra ket noi MySQL va trang thai cac bang du lieu trong database olist_raw.
"""
import os
import sys
import mysql.connector

def verify_connection():
    host = os.getenv("DB_HOST", os.getenv("MYSQL_HOST", "localhost"))
    port = int(os.getenv("DB_PORT", os.getenv("MYSQL_PORT", 3306)))
    user = os.getenv("DB_USER", os.getenv("MYSQL_USER", "root"))
    password = os.getenv("DB_PASSWORD", os.getenv("MYSQL_PASSWORD", "@Kk1332006"))
    database = os.getenv("DB_NAME", os.getenv("MYSQL_DATABASE", "olist_raw"))

    print("=" * 70)
    print("OLIST STRATEGIC ANALYTICS: DATABASE CONNECTION CHECK")
    print("=" * 70)
    print(f"[*] Target Host : {host}:{port}")
    print(f"[*] Target User : {user}")
    print(f"[*] Target DB   : {database}")
    print("-" * 70)

    try:
        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        cur = conn.cursor()
        cur.execute("SELECT VERSION();")
        db_version = cur.fetchone()[0]
        print(f"[+] Ket noi thanh cong! MySQL Server Version: {db_version}\n")

        # Danh sach cac bang du lieu chinh trong schema olist_raw
        schema_tables = [
            ("orders", "olist_orders"),
            ("order_items", "olist_order_items"),
            ("payments", "olist_order_payments"),
            ("products", "olist_products"),
            ("reviews", "olist_order_reviews"),
            ("customers", "olist_customers"),
            ("sellers", "olist_sellers"),
            ("category_translation", "product_category_name_translation"),
            ("geolocation", "olist_geolocation"),
            ("analytics_rfm_segments", "analytics_rfm_segments")
        ]

        print("[*] Kiem tra trang thai du lieu cac bang:")
        print(f"{'Table Name':<28} | {'Resolved Table':<20} | {'Row Count':<12} | {'Status'}")
        print("-" * 70)

        for primary, fallback in schema_tables:
            resolved = None
            count = 0
            for tbl in [primary, fallback]:
                try:
                    cur.execute(f"SELECT COUNT(*) FROM `{tbl}`")
                    count = cur.fetchone()[0]
                    resolved = tbl
                    break
                except Exception:
                    continue

            if resolved:
                status = "READY" if count > 0 else "EMPTY"
                print(f"{primary:<28} | {resolved:<20} | {count:<12,d} | {status}")
            else:
                print(f"{primary:<28} | {'NOT FOUND':<20} | {'0':<12} | MISSING")

        cur.close()
        conn.close()
        print("-" * 70)
        print("[+] He thong san sang de thuc thi toan bo luong truy van va bao cao!")
        print("=" * 70)
        return True

    except mysql.connector.Error as err:
        print(f"[-] Loi ket noi MySQL: {err}")
        print("\n[!] Huong dan khac phuc:")
        print(" 1. Kiem tra MySQL service da khoi dong chua (services.msc -> MySQL80)")
        print(" 2. Kiem tra credentials trong file .env hoac bien moi truong DB_USER / DB_PASSWORD")
        print(" 3. Kiem tra da import file dump: mysql -u root -p olist_raw < olist_dump.sql")
        print("=" * 70)
        return False

if __name__ == "__main__":
    verify_connection()
