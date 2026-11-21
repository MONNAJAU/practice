import csv
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parent / "opentix_remain_seats.csv"


def load_seats(csv_path: Path = CSV_PATH) -> list[dict]:
    rows = []
    with open(csv_path, mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            area = (row.get("票區資訊") or "").strip()
            raw_seats = (row.get("剩餘座位數") or "").strip()
            try:
                seats = int(raw_seats)
            except ValueError:
                seats = 0
            rows.append({"area": area, "seats": seats})
    return rows


def query_seats(keyword: str = "") -> str:
    keyword = (keyword or "").strip()
    rows = load_seats()

    if not rows:
        return "目前找不到座位資料（opentix_remain_seats.csv 為空）。"

    # 依關鍵字篩選（例如輸入「1樓」、「2樓」、「輪椅」、「有票」）
    if keyword and keyword not in ("全部", "查全部", "餘票"):
        if keyword == "有票":
            matched = [r for r in rows if r["seats"] > 0]
        else:
            matched = [r for r in rows if keyword in r["area"]]
    else:
        matched = [r for r in rows if r["seats"] > 0]

    if not matched:
        return f"找不到符合「{keyword}」的票區資料，試試輸入 1樓、2樓、3樓、4樓、輪椅 或 有票。"

    total_matched_seats = sum(r["seats"] for r in matched)
    lines = [f"查詢結果（共 {len(matched)} 筆，合計 {total_matched_seats} 席）："]

    # 避免訊息過長，最多先列出前 20 筆
    for r in matched[:20]:
        lines.append(f"• {r['area']}：剩 {r['seats']} 席")

    if len(matched) > 20:
        lines.append(f"（還有 {len(matched) - 20} 筆未列出，可輸入更具體的樓層或關鍵字縮小範圍）")

    return "\n".join(lines)