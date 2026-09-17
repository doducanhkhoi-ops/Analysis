import os
import shutil
import json
import uuid

base_dir = r"c:\Users\ASUS\Documents\Năm III\CSDL"
reports_dir = os.path.join(base_dir, "reports")
data_bi_dir = os.path.join(base_dir, "data_bi")
proj_name = "Bundled_Orders_Diagnostic"

target_pbip = os.path.join(reports_dir, f"{proj_name}.pbip")
target_rep = os.path.join(reports_dir, f"{proj_name}.Report")
target_sm = os.path.join(reports_dir, f"{proj_name}.SemanticModel")
ref_rep = os.path.join(reports_dir, "Payment_Pro.Report")

if os.path.exists(target_pbip): os.remove(target_pbip)
if os.path.exists(target_rep): shutil.rmtree(target_rep)
if os.path.exists(target_sm): shutil.rmtree(target_sm)

os.makedirs(target_rep, exist_ok=True)
os.makedirs(target_sm, exist_ok=True)

# 1. PBIP file
pbip_data = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
    "version": "1.0",
    "artifacts": [{"report": {"path": f"{proj_name}.Report"}}],
    "settings": {"enableAutoRecovery": True}
}
with open(target_pbip, "w", encoding="utf-8") as f:
    json.dump(pbip_data, f, indent=2)

ref_platform = os.path.join(ref_rep, ".platform")
if os.path.exists(ref_platform):
    shutil.copy(ref_platform, os.path.join(target_rep, ".platform"))
    shutil.copy(ref_platform, os.path.join(target_sm, ".platform"))

# 2. SemanticModel
with open(os.path.join(target_sm, "definition.pbism"), "w", encoding="utf-8") as f:
    json.dump({
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
        "version": "4.2",
        "settings": {}
    }, f, indent=2)

sm_def = os.path.join(target_sm, "definition")
os.makedirs(sm_def, exist_ok=True)
sm_tables = os.path.join(sm_def, "tables")
os.makedirs(sm_tables, exist_ok=True)
sm_cultures = os.path.join(sm_def, "cultures")
os.makedirs(sm_cultures, exist_ok=True)

with open(os.path.join(sm_def, "database.tmdl"), "w", encoding="utf-8") as f:
    f.write("database\n\tcompatibilityLevel: 1606\n")

with open(os.path.join(sm_cultures, "vi-VN.tmdl"), "w", encoding="utf-8") as f:
    f.write("cultureInfo vi-VN\n")

with open(os.path.join(sm_def, "model.tmdl"), "w", encoding="utf-8") as f:
    f.write("""model Model
\tculture: vi-VN
\tdefaultPowerBIDataSourceVersion: powerBI_V3
\tsourceQueryCulture: en-US
\tvalueFilterBehavior: independent
\tdataAccessOptions
\t\tlegacyRedirects
\t\treturnErrorValuesAsNull

annotation __PBI_TimeIntelligenceEnabled = 1

annotation PBI_QueryOrder = ["fact_bundle_summary","fact_bundle_sla_crosstab","fact_bundle_item_tiers","fact_bundle_seller_tiers"]

annotation PBI_ProTooling = ["DevMode"]

ref table fact_bundle_summary
ref table fact_bundle_sla_crosstab
ref table fact_bundle_item_tiers
ref table fact_bundle_seller_tiers

ref cultureInfo vi-VN
""")

def create_table_tmdl(table_name, columns, csv_file):
    lines = ["table " + table_name, "\tlineageTag: " + str(uuid.uuid4()), ""]
    m_transform_list = []
    for c_name, d_type, f_str, m_type in columns:
        lines.append("\tcolumn " + c_name)
        lines.append("\t\tdataType: " + d_type)
        if f_str:
            lines.append("\t\tformatString: " + f_str)
        lines.append("\t\tlineageTag: " + str(uuid.uuid4()))
        lines.append("\t\tsummarizeBy: " + ("none" if d_type == "string" else "sum"))
        lines.append("\t\tsourceColumn: " + c_name)
        lines.append("\t\tannotation SummarizationSetBy = Automatic")
        if d_type == "double":
            lines.append('\t\tannotation PBI_FormatHint = {"isGeneralNumber":true}')
        lines.append("")
        m_transform_list.append('{"' + c_name + '", ' + m_type + '}')
    
    num_cols = len(columns)
    csv_abs_path = os.path.join(data_bi_dir, csv_file).replace('\\', '/')
    lines.append("\tpartition " + table_name + " = m")
    lines.append("\t\tmode: import")
    lines.append("\t\tsource =")
    lines.append("\t\t\t\tlet")
    lines.append('\t\t\t\t    Nguon = Csv.Document(File.Contents("' + csv_abs_path + '"),[Delimiter=",", Columns=' + str(num_cols) + ', Encoding=65001, QuoteStyle=QuoteStyle.None]),')
    lines.append('\t\t\t\t    #"Tieu de Duoc Tang cap" = Table.PromoteHeaders(Nguon, [PromoteAllScalars=true]),')
    lines.append('\t\t\t\t    #"Thay doi Loai" = Table.TransformColumnTypes(#"Tieu de Duoc Tang cap",{' + ', '.join(m_transform_list) + '})')
    lines.append("\t\t\t\tin")
    lines.append('\t\t\t\t    #"Thay doi Loai"')
    lines.append("")
    lines.append("\tannotation PBI_ResultType = Table")
    lines.append("")
    
    with open(os.path.join(sm_tables, table_name + ".tmdl"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

# 1. fact_bundle_summary
create_table_tmdl("fact_bundle_summary", [
    ("basket_type", "string", None, "type text"),
    ("total_orders", "int64", "#,##0", "Int64.Type"),
    ("order_share_pct", "double", None, "type number"),
    ("total_gmv", "double", "#,##0.00", "type number"),
    ("aov", "double", "#,##0.00", "type number"),
    ("avg_items", "double", None, "type number"),
    ("avg_sellers", "double", None, "type number"),
    ("avg_delivery_days", "double", None, "type number"),
    ("avg_handling_days", "double", None, "type number"),
    ("avg_transit_days", "double", None, "type number"),
    ("late_delivery_pct", "double", None, "type number"),
    ("avg_review_score", "double", None, "type number"),
    ("pct_1_star", "double", None, "type number"),
    ("freight_burden_pct", "double", None, "type number")
], "fact_bundle_summary.csv")

# 2. fact_bundle_sla_crosstab
create_table_tmdl("fact_bundle_sla_crosstab", [
    ("basket_type", "string", None, "type text"),
    ("is_late", "string", None, "type text"),
    ("total_orders", "int64", "#,##0", "Int64.Type"),
    ("pct_within_basket", "double", None, "type number"),
    ("avg_review_score", "double", None, "type number"),
    ("pct_1_star", "double", None, "type number"),
    ("aov", "double", "#,##0.00", "type number"),
    ("avg_delivery_days", "double", None, "type number")
], "fact_bundle_sla_crosstab.csv")

# 3. fact_bundle_item_tiers
create_table_tmdl("fact_bundle_item_tiers", [
    ("item_bundle_tier", "string", None, "type text"),
    ("total_orders", "int64", "#,##0", "Int64.Type"),
    ("total_gmv", "double", "#,##0.00", "type number"),
    ("aov", "double", "#,##0.00", "type number"),
    ("avg_delivery_days", "double", None, "type number"),
    ("avg_handling_days", "double", None, "type number"),
    ("avg_transit_days", "double", None, "type number"),
    ("late_delivery_pct", "double", None, "type number"),
    ("avg_review_score", "double", None, "type number"),
    ("pct_1_star", "double", None, "type number")
], "fact_bundle_item_tiers.csv")

# 4. fact_bundle_seller_tiers
create_table_tmdl("fact_bundle_seller_tiers", [
    ("seller_tier", "string", None, "type text"),
    ("total_orders", "int64", "#,##0", "Int64.Type"),
    ("total_gmv", "double", "#,##0.00", "type number"),
    ("aov", "double", "#,##0.00", "type number"),
    ("avg_delivery_days", "double", None, "type number"),
    ("late_delivery_pct", "double", None, "type number"),
    ("avg_review_score", "double", None, "type number"),
    ("pct_1_star", "double", None, "type number")
], "fact_bundle_seller_tiers.csv")

# 3. Report Definition
with open(os.path.join(target_rep, "definition.pbir"), "w", encoding="utf-8") as f:
    json.dump({
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
        "version": "4.0",
        "datasetReference": {"byPath": {"path": f"../{proj_name}.SemanticModel"}}
    }, f, indent=2)

rep_def = os.path.join(target_rep, "definition")
os.makedirs(rep_def, exist_ok=True)

with open(os.path.join(rep_def, "version.json"), "w", encoding="utf-8") as f:
    json.dump({
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/versionMetadata/1.0.0/schema.json",
        "version": "2.0.0"
    }, f, indent=2)

if os.path.exists(os.path.join(ref_rep, "StaticResources")):
    shutil.copytree(os.path.join(ref_rep, "StaticResources"), os.path.join(target_rep, "StaticResources"))

with open(os.path.join(ref_rep, "definition", "report.json"), "r", encoding="utf-8") as f:
    report_json = json.load(f)
with open(os.path.join(rep_def, "report.json"), "w", encoding="utf-8") as f:
    json.dump(report_json, f, indent=2)

page_id = "page_bundle_01"
rep_pages = os.path.join(rep_def, "pages")
os.makedirs(rep_pages, exist_ok=True)
with open(os.path.join(rep_pages, "pages.json"), "w", encoding="utf-8") as f:
    json.dump({
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json",
        "pageOrder": [page_id],
        "activePageName": page_id
    }, f, indent=2)

page_dir = os.path.join(rep_pages, page_id)
os.makedirs(page_dir, exist_ok=True)
visuals_dir = os.path.join(page_dir, "visuals")
os.makedirs(visuals_dir, exist_ok=True)

with open(os.path.join(page_dir, "page.json"), "w", encoding="utf-8") as f:
    json.dump({
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
        "name": page_id,
        "displayName": "Chẩn Đoán Đơn Gộp vs Đơn Đơn",
        "displayOption": "FitToPage",
        "height": 1080,
        "width": 1920
    }, f, indent=2)

ref_visuals_dir = os.path.join(ref_rep, "definition", "pages", "8f64cc421d0e0604367e", "visuals")

visual_configs = [
    # Header shape
    ("a1000000000000000001", "a1000000000000000001", {}),
    # Header title
    ("a1000000000000000002", "a1000000000000000002", {
        "text": "OLIST AUDIT: NGHỊCH LÝ GIAO ĐƠN GỘP VS ĐƠN ĐƠN & SỤP ĐỔ ĐÁNH GIÁ REVIEW"
    }),
    # Slicer
    ("a1000000000000000003", "a1000000000000000003", {
        "entity": "fact_bundle_summary",
        "property": "basket_type",
        "queryRef": "fact_bundle_summary.basket_type",
        "headerText": "LỌC THEO LOẠI GIỎ HÀNG:"
    }),
    # Card 1: Total Orders
    ("c1000000000000000001", "c1000000000000000001", {
        "entity": "fact_bundle_summary",
        "property": "total_orders",
        "labelText": "TỔNG ĐƠN GIAO THÀNH CÔNG",
        "color": "#38BDF8"
    }),
    # Card 2: Total GMV
    ("c1000000000000000002", "c1000000000000000002", {
        "entity": "fact_bundle_summary",
        "property": "total_gmv",
        "labelText": "TỔNG DOANH THU HOÀN TẤT (BRL)",
        "color": "#10B981"
    }),
    # Card 3: Avg Delivery Days
    ("c1000000000000000003", "c1000000000000000003", {
        "entity": "fact_bundle_summary",
        "property": "avg_delivery_days",
        "labelText": "THỜI GIAN GIAO TB (NGÀY)",
        "color": "#F59E0B"
    }),
    # Card 4: Review Score
    ("c1000000000000000004", "c1000000000000000004", {
        "entity": "fact_bundle_summary",
        "property": "avg_review_score",
        "labelText": "ĐIỂM ĐÁNH GIÁ REVIEW TB",
        "color": "#EC4899"
    }),
    # Card 5: 1-Star Pct
    ("c1000000000000000005", "c1000000000000000005", {
        "entity": "fact_bundle_summary",
        "property": "pct_1_star",
        "labelText": "TỶ LỆ KHÁCH CHẤM 1-SAO (%)",
        "color": "#EF4444"
    }),
    # Donut: Orders by Basket Type
    ("a1000000000000000005", "a1000000000000000005", {
        "cat_entity": "fact_bundle_summary",
        "cat_prop": "basket_type",
        "val_entity": "fact_bundle_summary",
        "val_prop": "total_orders",
        "title": "Cơ Cấu Số Lượng Đơn Theo Loại Giỏ Hàng"
    }),
    # Combo Chart: Delivery Days vs Late Delivery Pct
    ("a1000000000000000006", "a1000000000000000006", {
        "cat_entity": "fact_bundle_summary",
        "cat_prop": "basket_type",
        "y_entity": "fact_bundle_summary",
        "y_prop": "avg_delivery_days",
        "y2_entity": "fact_bundle_summary",
        "y2_prop": "late_delivery_pct",
        "title": "Nghịch Lý Thời Gian Giao & Tỷ Lệ Trễ Hạn Theo Giỏ Hàng"
    }),
    # Bar Chart: Item Count Tiers vs 1-Star Review
    ("a1000000000000000007", "a1000000000000000007", {
        "cat_entity": "fact_bundle_item_tiers",
        "cat_prop": "item_bundle_tier",
        "val_entity": "fact_bundle_item_tiers",
        "val_prop": "pct_1_star",
        "title": "Sự Leo Thang Đánh Giá 1-Sao Theo Số Lượng Món Trong Đơn (%)"
    }),
    # Table: Detailed Matrix Crosstab
    ("a1000000000000000008", "a1000000000000000008", {
        "entity": "fact_bundle_sla_crosstab",
        "title": "Ma Trận Đối Chiếu Tác Động Giao Đúng Hạn vs Trễ Hạn Đến Điểm Review"
    })
]

for src_name, dst_name, cfg in visual_configs:
    src_v_path = os.path.join(ref_visuals_dir, src_name, "visual.json")
    if not os.path.exists(src_v_path):
        continue
    with open(src_v_path, "r", encoding="utf-8") as f:
        v_data = json.load(f)
    
    v_data["$schema"] = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.9.0/schema.json"
    
    # Textbox title
    if "text" in cfg:
        objs = v_data.get("visual", {}).get("objects", {})
        if "general" in objs and "paragraphs" in objs["general"][0].get("properties", {}):
            objs["general"][0]["properties"]["paragraphs"][0]["textRuns"][0]["value"] = cfg["text"]
        elif "textbox" in objs and "paragraphs" in objs["textbox"][0].get("properties", {}):
            objs["textbox"][0]["properties"]["paragraphs"][0]["textRuns"][0]["value"] = cfg["text"]
    
    # Card visual
    if v_data.get("visual", {}).get("visualType") == "cardVisual" and "entity" in cfg:
        proj = v_data["visual"]["query"]["queryState"]["Data"]["projections"][0]
        proj["field"]["Aggregation"]["Expression"]["Column"]["Expression"]["SourceRef"]["Entity"] = cfg["entity"]
        proj["field"]["Aggregation"]["Expression"]["Column"]["Property"] = cfg["property"]
        proj["queryRef"] = f"Sum({cfg['entity']}.{cfg['property']})"
        proj["nativeQueryRef"] = cfg["property"]
        
        objs = v_data["visual"].get("objects", {})
        if "label" in objs and len(objs["label"]) > 0:
            objs["label"][0]["properties"]["text"]["expr"]["Literal"]["Value"] = f"'{cfg['labelText']}'"
        if "value" in objs and len(objs["value"]) > 0 and "color" in cfg:
            objs["value"][0]["properties"]["fontColor"]["solid"]["color"]["expr"]["Literal"]["Value"] = f"'{cfg['color']}'"
    
    # Slicer
    if v_data.get("visual", {}).get("visualType") == "slicer" and "entity" in cfg:
        proj = v_data["visual"]["query"]["queryState"]["Values"]["projections"][0]
        proj["field"]["Column"]["Expression"]["SourceRef"]["Entity"] = cfg["entity"]
        proj["field"]["Column"]["Property"] = cfg["property"]
        proj["queryRef"] = f"{cfg['entity']}.{cfg['property']}"
        proj["nativeQueryRef"] = cfg["property"]
        objs = v_data["visual"].get("objects", {})
        if "header" in objs and len(objs["header"]) > 0:
            objs["header"][0]["properties"]["text"]["expr"]["Literal"]["Value"] = f"'{cfg['headerText']}'"

    # Donut Chart
    if v_data.get("visual", {}).get("visualType") == "donutChart" and "cat_entity" in cfg:
        q_state = v_data["visual"]["query"]["queryState"]
        if "Category" in q_state:
            q_state["Category"]["projections"][0]["field"]["Column"]["Expression"]["SourceRef"]["Entity"] = cfg["cat_entity"]
            q_state["Category"]["projections"][0]["field"]["Column"]["Property"] = cfg["cat_prop"]
            q_state["Category"]["projections"][0]["queryRef"] = f"{cfg['cat_entity']}.{cfg['cat_prop']}"
        if "Y" in q_state:
            q_state["Y"]["projections"][0]["field"]["Aggregation"]["Expression"]["Column"]["Expression"]["SourceRef"]["Entity"] = cfg["val_entity"]
            q_state["Y"]["projections"][0]["field"]["Aggregation"]["Expression"]["Column"]["Property"] = cfg["val_prop"]
            q_state["Y"]["projections"][0]["queryRef"] = f"Sum({cfg['val_entity']}.{cfg['val_prop']})"

    # Combo Chart
    if v_data.get("visual", {}).get("visualType") == "lineClusteredColumnComboChart" and "cat_entity" in cfg:
        q_state = v_data["visual"]["query"]["queryState"]
        if "Category" in q_state:
            q_state["Category"]["projections"][0]["field"]["Column"]["Expression"]["SourceRef"]["Entity"] = cfg["cat_entity"]
            q_state["Category"]["projections"][0]["field"]["Column"]["Property"] = cfg["cat_prop"]
            q_state["Category"]["projections"][0]["queryRef"] = f"{cfg['cat_entity']}.{cfg['cat_prop']}"
        if "Y" in q_state:
            q_state["Y"]["projections"][0]["field"]["Aggregation"]["Expression"]["Column"]["Expression"]["SourceRef"]["Entity"] = cfg["y_entity"]
            q_state["Y"]["projections"][0]["field"]["Aggregation"]["Expression"]["Column"]["Property"] = cfg["y_prop"]
            q_state["Y"]["projections"][0]["queryRef"] = f"Sum({cfg['y_entity']}.{cfg['y_prop']})"
        if "Y2" in q_state:
            q_state["Y2"]["projections"][0]["field"]["Aggregation"]["Expression"]["Column"]["Expression"]["SourceRef"]["Entity"] = cfg["y2_entity"]
            q_state["Y2"]["projections"][0]["field"]["Aggregation"]["Expression"]["Column"]["Property"] = cfg["y2_prop"]
            q_state["Y2"]["projections"][0]["queryRef"] = f"Sum({cfg['y2_entity']}.{cfg['y2_prop']})"

    # Bar chart
    if v_data.get("visual", {}).get("visualType") == "barChart" and "cat_entity" in cfg:
        q_state = v_data["visual"]["query"]["queryState"]
        if "Category" in q_state:
            q_state["Category"]["projections"][0]["field"]["Column"]["Expression"]["SourceRef"]["Entity"] = cfg["cat_entity"]
            q_state["Category"]["projections"][0]["field"]["Column"]["Property"] = cfg["cat_prop"]
            q_state["Category"]["projections"][0]["queryRef"] = f"{cfg['cat_entity']}.{cfg['cat_prop']}"
        if "Y" in q_state:
            q_state["Y"]["projections"][0]["field"]["Aggregation"]["Expression"]["Column"]["Expression"]["SourceRef"]["Entity"] = cfg["val_entity"]
            q_state["Y"]["projections"][0]["field"]["Aggregation"]["Expression"]["Column"]["Property"] = cfg["val_prop"]
            q_state["Y"]["projections"][0]["queryRef"] = f"Sum({cfg['val_entity']}.{cfg['val_prop']})"

    # Table
    if v_data.get("visual", {}).get("visualType") == "tableEx" and "entity" in cfg:
        q_state = v_data["visual"]["query"]["queryState"]
        q_state["Values"]["projections"] = [
            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "fact_bundle_sla_crosstab"}}, "Property": "basket_type"}}, "queryRef": "fact_bundle_sla_crosstab.basket_type", "nativeQueryRef": "basket_type"},
            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "fact_bundle_sla_crosstab"}}, "Property": "is_late"}}, "queryRef": "fact_bundle_sla_crosstab.is_late", "nativeQueryRef": "is_late"},
            {"field": {"Aggregation": {"Expression": {"Column": {"Expression": {"SourceRef": {"Entity": "fact_bundle_sla_crosstab"}}, "Property": "total_orders"}}, "Function": 0}}, "queryRef": "Sum(fact_bundle_sla_crosstab.total_orders)", "nativeQueryRef": "total_orders"},
            {"field": {"Aggregation": {"Expression": {"Column": {"Expression": {"SourceRef": {"Entity": "fact_bundle_sla_crosstab"}}, "Property": "avg_delivery_days"}}, "Function": 0}}, "queryRef": "Sum(fact_bundle_sla_crosstab.avg_delivery_days)", "nativeQueryRef": "avg_delivery_days"},
            {"field": {"Aggregation": {"Expression": {"Column": {"Expression": {"SourceRef": {"Entity": "fact_bundle_sla_crosstab"}}, "Property": "avg_review_score"}}, "Function": 0}}, "queryRef": "Sum(fact_bundle_sla_crosstab.avg_review_score)", "nativeQueryRef": "avg_review_score"},
            {"field": {"Aggregation": {"Expression": {"Column": {"Expression": {"SourceRef": {"Entity": "fact_bundle_sla_crosstab"}}, "Property": "pct_1_star"}}, "Function": 0}}, "queryRef": "Sum(fact_bundle_sla_crosstab.pct_1_star)", "nativeQueryRef": "pct_1_star"}
        ]

    # Update Title nested inside visual.visualContainerObjects
    if "title" in cfg:
        v_data.setdefault("visual", {}).setdefault("visualContainerObjects", {})["title"] = [
            {"properties": {"text": {"expr": {"Literal": {"Value": f"'{cfg['title']}'"}}}}}
        ]
        
    dst_v_dir = os.path.join(visuals_dir, dst_name)
    os.makedirs(dst_v_dir, exist_ok=True)
    with open(os.path.join(dst_v_dir, "visual.json"), "w", encoding="utf-8") as f:
        json.dump(v_data, f, indent=2)

print("[+] Successfully generated 100% adapted bespoke PBIP for Bundled Orders Diagnostic!")