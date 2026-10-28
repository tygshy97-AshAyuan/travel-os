"""Generate fictional UI acceptance cases; no real booking or route advice."""
from pathlib import Path
from test_export import example_rows, next_version
from export_trip import make_payload, render

ROOT = Path(__file__).resolve().parents[1]


def scenario(locale, city, zone, activities, locations):
    rows = example_rows()
    rows["Travel Overview"][2][1] = city + ("，慢慢玩三天" if locale == "zh-CN" else " in three days")
    rows["Travel Overview"][2][2] = city
    rows["Travel Overview"][2][10] = zone
    for idx, row in enumerate(rows["Daily Plan"][2:]):
        row[5:9] = [zone, city, activities[idx], locations[idx]]
        row[9] = "步行 / 公共交通 · 待核实" if locale == "zh-CN" else "Walk / transit · to verify"
        row[14] = "虚构演示，非真实路线或预订" if locale == "zh-CN" else "Fictional demonstration; no verified route or reservation"
        row[16] = "时间与费用仅用于测试；出发前须重新核实。" if locale == "zh-CN" else "Times and costs are fictional; verify before travel."
    if locale == "en":
        rows["Checklist"][2][2] = "Verify reservation and local transport before departure"
        rows["Proposals"][2][4] = "Move afternoon walk later"
    rows = next_version(rows)
    rows["Daily Plan"][5][3:5] = ["15:00", "17:00"]
    for version in ("v0.1.0", "v0.1.1"):
        for n in (2, 3):
            row = rows["Daily Plan"][3][:]
            row[0:5] = [f"I-00{n+1}", version, f"2030-05-0{n}", "10:00", "12:00"]
            row[7:9] = [activities[n], locations[n]]
            row[12:14] = ["", ""]
            rows["Daily Plan"].append(row)
    return rows


def build():
    target = ROOT / "artifacts"
    target.mkdir(exist_ok=True)
    specs = [
        ("china-domestic", "zh-CN", "杭州", "Asia/Shanghai", "mainland-cn",
         ["抵达，放下行李", "沿西湖慢慢走", "龙井一带半日散步", "早餐后留白，准备返程"], ["杭州东站", "西湖", "龙井村", "杭州东站"]),
        ("china-outbound", "zh-CN", "东京 Tokyo", "Asia/Tokyo", "other",
         ["抵达，确认交通", "浅草周边散步", "公园与街区半日游", "早餐后准备返程"], ["東京駅", "浅草寺", "上野公園", "東京駅"]),
        ("china-inbound", "en", "上海", "Asia/Shanghai", "mainland-cn",
         ["Arrive and settle in", "Walk by the river", "Explore a neighborhood", "Leave time for departure"], ["上海虹桥站", "外滩", "静安寺", "上海虹桥站"]),
        ("international", "en", "Paris", "Europe/Paris", "other",
         ["Arrive and settle in", "Afternoon river walk", "Garden and neighborhood", "Leave time for departure"], ["Gare de Lyon", "Pont Neuf", "Jardin du Luxembourg", "Gare de Lyon"]),
    ]
    for name, locale, city, zone, region, activities, locations in specs:
        rows = scenario(locale, city, zone, activities, locations)
        p = make_payload(rows, locale=locale, region=region)
        if name == "china-inbound":
            p["title"] = "Shanghai in three days"
        p["demo_notice"] = "演示行程，日期与安排仅供试用。" if locale == "zh-CN" else "Sample itinerary with fictional dates and plans."
        (target / f"{name}.html").write_text(render(p), encoding="utf-8")
    p = make_payload(example_rows(), region="mainland-cn", audience="companion", share_items=["I-002"])
    p["demo_notice"] = "同行版功能演示 · 虚构内容"
    (target / "companion.html").write_text(render(p), encoding="utf-8")
    print("Generated four fictional scenario pages and one companion example in artifacts/")


if __name__ == "__main__":
    build()
