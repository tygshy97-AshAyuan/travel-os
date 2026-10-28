#!/usr/bin/env python3
"""Export a validated active archive to a self-contained, read-only trip page.

No third-party packages, network requests, workbook writes or hidden telemetry.
"""
import argparse
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from html import escape
import json
from pathlib import Path
import sys

from build_map_url import build_place_url
from validate_archive import (ARCHIVE_ERRORS, ZoneInfo, ZoneInfoNotFoundError,
                              _clock_seconds, _date, validate_rows, workbook_rows)

REGIONS = ("mainland-cn", "hong-kong", "macao", "taiwan", "other", "unknown")
FIELDS = [("date", "日期", "Date"), ("start", "开始", "Start"), ("end", "结束", "End"),
          ("zone", "时区", "Time zone"), ("city", "城市", "City"),
          ("activity", "活动", "Activity"), ("location", "地点", "Place"),
          ("transport", "交通", "Transport"), ("booking", "关联预订", "Booking link"),
          ("cost", "费用", "Cost"), ("currency", "币种", "Currency"),
          ("notes", "备注", "Notes")]
TEXT = {
    "zh-CN": dict(plan="行程", next="接下来", todos="出发前记得", changes="这次改了什么",
        proposals="还没定的事", date="看哪一天", all="全部行程", today="今天", print="打印行程",
        personal="我的行程", companion="同行版", draft="尚未启用的草稿不能导出为当前行程。",
        snapshot="这是保存时的行程。改动后，记得换成新文件。", empty="没有需要显示的项目。",
        map="查找地点", copy="复制地点", copied="地点已复制", manual="请选中并复制下方文字。",
        source="费用与详情", checked="核对时间", notes="补充说明", unknown="待核实",
        complete="这一天没有待办行程了。", unscheduled="时间待确认", first="这一天从这里开始",
        nextday="次日", continuing="跨夜行程仍在进行",
        live="当地时间，按保存时的进度", blocked="这里需要先确认一下", overdue="时间已过，还没记为完成",
        offline="行程可以离线看，打开地图需要联网。",
        booking="预订编号", added="新增", removed="移除", changed="调整", before="原安排", after="当前安排",
        baseline="上一份", initial="还没有改动记录。", nochange="行程没有变化。",
        generated="保存时间", version="文件版本", dayempty="今天没有安排，仍显示所选行程。", region="可复制地点到地图中查找",
        travel="交通", money="费用", readonly="想换个安排？复制这段话，回到对话里接着改。",
        sharewarning="发给同伴前，看看里面有没有不想分享的地点或备注。",
        request="复制修改说明", requestdone="复制好了。回到对话里粘贴，再补上想怎么改。",
        requesttext="请读取我的最新 Travel OS 档案，检查当前版本是否仍为 {version}。我想调整 {scope}，原因：____。先展示改前改后及对时间、费用和已订安排的影响，等我确认再写入。",
        nojs="交互功能不可用时，可直接阅读下方完整行程，并使用浏览器打印。"),
    "en": dict(plan="Your itinerary", next="Up next", todos="Before you go", changes="What changed",
        proposals="Still to decide", date="Choose a date", all="All dates", today="Today locally", print="Print itinerary",
        personal="Private itinerary", companion="Companion copy · review before sharing", draft="A draft cannot be exported as the current plan.",
        snapshot="Read-only snapshot. Export again after changing the plan.", empty="Nothing to show here.",
        map="Find place", copy="Copy place", copied="Place copied", manual="Select and copy the text below.",
        source="Costs and details", checked="Recorded check time", notes="Notes", unknown="Needs verification",
        complete="No remaining activities for this date.", unscheduled="Time to confirm", first="Next on this day",
        nextday="next day", continuing="Overnight activity still underway",
        live="Local time, saved progress", blocked="Blocked: confirm before proceeding", overdue="Planned time passed; completion not recorded",
        offline="Your itinerary works offline. Maps need internet.",
        booking="Linked booking", added="Added", removed="Removed", changed="Changed", before="Before", after="Current",
        baseline="Compared with", initial="First version; no earlier plan to compare.", nochange="No itinerary field changes.",
        generated="Exported", version="Current version", dayempty="Nothing scheduled today. Still showing your selected date.", region="Map service not specified. Copy the place name instead.",
        travel="Transport", money="Cost recorded in itinerary", readonly="Want to change something? Copy a note and continue in your chat.",
        sharewarning="Only explicitly selected activities are included. Review names and places for private information before sharing.",
        request="Copy a change note", requestdone="Request copied. Paste it into your AI conversation and add your reason.",
        requesttext="Read my latest Travel OS archive and check whether {version} is still current. I want to change {scope}, because: ____. Show before/after and effects on time, cost and confirmed bookings; wait for my approval before writing.",
        nojs="If interactive controls are unavailable, read the complete itinerary below and use your browser's print command.")
}
STATUS_ZH = {"Planned": "计划中", "Ready": "待执行", "In progress": "进行中", "Done": "已完成", "Skipped": "已跳过", "Blocked": "受阻"}
STATUS_EN = {"待处理": "Pending", "进行中": "In progress", "已完成": "Completed", "已取消": "Cancelled", "阻塞": "Blocked", "接受": "Accepted", "拒绝": "Rejected", "需澄清": "Needs clarification"}


def records(rows, sheet):
    return [dict(zip(rows[sheet][1], row + [""] * (len(rows[sheet][1]) - len(row))))
            for row in rows[sheet][2:] if row and any(row)]


def day(value):
    parsed = _date(value)
    return parsed.isoformat() if parsed else ""


def clock(value):
    seconds = _clock_seconds(value)
    if seconds is None:
        return ""
    return f"{seconds // 3600:02}:{seconds % 3600 // 60:02}" + (f":{seconds % 60:02}" if seconds % 60 else "")


def epoch(date, time, zone, offset=0):
    """Do not guess ambiguous or non-existent DST wall times."""
    if not time or ZoneInfo is None:
        return None
    try:
        naive = datetime.fromisoformat(date + "T" + time) + timedelta(days=offset)
        tz = ZoneInfo(zone)
        candidates = set()
        for fold in (0, 1):
            aware = naive.replace(tzinfo=tz, fold=fold)
            if datetime.fromtimestamp(aware.timestamp(), tz).replace(tzinfo=None) == naive:
                candidates.add(aware.timestamp() * 1000)
        return next(iter(candidates)) if len(candidates) == 1 else None
    except (ValueError, ZoneInfoNotFoundError):
        return None


def make_payload(rows, *, locale="zh-CN", region="unknown", city_regions=None,
                 audience="personal", share_items=(), generated=None):
    if locale not in TEXT or region not in REGIONS or audience not in ("personal", "companion"):
        raise ValueError("Unsupported locale, destination region or audience")
    city_regions = city_regions or {}
    if any(value not in REGIONS for value in city_regions.values()):
        raise ValueError("Unsupported city region")
    errors = validate_rows(rows)
    if errors:
        raise ValueError("Invalid archive: " + "; ".join(errors))
    overview = records(rows, "Travel Overview")[0]
    active = overview["Active Version"]
    if overview["状态"] not in ("Active", "Completed") or not active:
        raise ValueError(TEXT[locale]["draft"])
    plans = records(rows, "Daily Plan")
    if set(city_regions) - {r["城市"] for r in plans if r["版本"] == active}:
        raise ValueError("City region keys must match a city in the active plan")
    booking_map = {r["预订ID"]: r for r in records(rows, "Bookings")}
    share_items = set(share_items)
    if audience == "companion":
        available = {r["项目ID"] for r in plans if r["版本"] == active}
        if not share_items or not share_items <= available:
            raise ValueError("Companion export requires explicit current --share-item IDs")
        if any(r["项目ID"] in share_items and r["版本"] == active and
               booking_map.get(r["预订ID"], {}).get("类别") == "住宿" for r in plans):
            raise ValueError("Lodging-linked activities are excluded from companion exports")

    def item(row):
        d, start, end = day(row["日期"]), clock(row["开始"]), clock(row["结束"])
        overnight = any(marker in row["备注"].lower() for marker in ("[overnight]", "跨夜", "过夜"))
        end_offset = int(bool(start and end and end <= start and overnight))
        area = city_regions.get(row["城市"], region)
        provider = "amap" if area == "mainland-cn" else "google" if area != "unknown" else None
        personal = audience == "personal"
        value = dict(id=row["项目ID"], date=d, start=start, end=end, zone=row["时区"],
                     end_date=(datetime.fromisoformat(d) + timedelta(days=end_offset)).date().isoformat(),
                     city=row["城市"], activity=row["活动"], location=row["地点"], transport=row["交通"],
                     status=row["执行状态"], booking=row["预订ID"] if personal else "",
                     cost=row["费用"] if personal else "", currency=row["币种"] if personal else "",
                     source=row["来源"] if personal else "", checked=row["核验时间"] if personal else "",
                     notes=row["备注"] if personal else "", provider=provider,
                     map_url=build_place_url(row["地点"], row["城市"], provider) if provider and row["地点"] else "",
                     start_epoch=epoch(d, start, row["时区"]),
                     end_epoch=epoch(d, end, row["时区"], end_offset))
        return value

    current = [item(r) for r in plans if r["版本"] == active and
               (audience == "personal" or r["项目ID"] in share_items)]
    current.sort(key=lambda r: (r["date"], r["start"] or "99", r["id"]))
    logs = records(rows, "Change Log")
    log = next(r for r in logs if r["版本"] == active)
    previous = log["上一版本"] if audience == "personal" else ""
    changes = []
    if previous:
        old = {r["项目ID"]: item(r) for r in plans if r["版本"] == previous}
        new = {r["id"]: r for r in current}
        for ident in sorted(old.keys() | new.keys()):
            before, after = old.get(ident), new.get(ident)
            fields = [key for key, _, _ in FIELDS if before and after and before[key] != after[key]]
            if fields or before is None or after is None:
                changes.append(dict(kind="added" if before is None else "removed" if after is None else "changed",
                                    before=before, after=after, fields=fields))
    return dict(locale=locale, audience=audience, version=active, previous=previous,
                title=overview["旅行标题"] if audience == "personal" else ("同行行程" if locale == "zh-CN" else "Shared itinerary"),
                destination=overview["目的地"] if audience == "personal" else "",
                start=day(overview["开始日期"]) if audience == "personal" else min(r["date"] for r in current),
                end=day(overview["结束日期"]) if audience == "personal" else max(r["date"] for r in current),
                generated=generated or datetime.now(timezone.utc).isoformat(timespec="seconds"),
                items=current, changes=changes,
                todos=records(rows, "Checklist") if audience == "personal" else [],
                proposals=[r for r in records(rows, "Proposals") if r["状态"] in ("待处理", "需澄清")] if audience == "personal" else [])


def render(payload):
    t, locale = TEXT[payload["locale"]], payload["locale"]
    def e(value):
        return escape(str(value), quote=True)
    def status(value):
        return (STATUS_ZH if locale == "zh-CN" else STATUS_EN).get(value, value)
    def amount(row):
        return f'{Decimal(row["cost"]):,.2f} {row["currency"]}' if row["cost"] else t["unknown"]
    def links(row):
        lookup = f'<a href="{e(row["map_url"])}" target="_blank" rel="noopener noreferrer">{e(t["map"])} · {("高德" if locale == "zh-CN" else "Amap") if row["provider"] == "amap" else "Google"}</a>' if row["map_url"] else f'<span class="muted">{e(t["region"])}</span>'
        return lookup + f'<button type="button" class="text-action copy-place" data-copy="{e(row["city"] + " " + row["location"])}">{e(t["copy"])}</button>'
    sections = []
    for d in sorted({r["date"] for r in payload["items"]}):
        cards = []
        for r in (r for r in payload["items"] if r["date"] == d):
            details = ""
            if payload["audience"] == "personal":
                booking = f'<p>{e(t["booking"])}: {e(r["booking"])}</p>' if r["booking"] else ""
                details = f'<details class="stop-details"><summary>{e(t["source"])}</summary><p>{e(t["money"])}: {e(amount(r))}</p>{booking}<p>{e(r["source"] or t["unknown"])}</p><p>{e(t["checked"])}: {e(r["checked"] or t["unknown"])}</p><p>{e(r["notes"])}</p></details>'
            end_label = (t["nextday"] + " " if r["end_date"] > r["date"] else "") + r["end"]
            state = f'<span class="status">{e(status(r["status"]))}</span>' if r["status"] not in ("Ready", "Planned") else ""
            cards.append(f'<article class="stop"><div class="stop-time"><span>{e(r["start"] or "—")}</span><span class="muted">{e(end_label)}</span></div><div class="stop-body"><div class="stop-heading"><h3>{e(r["activity"])}</h3>{state}</div><p class="place">{e(r["location"] or t["unknown"])}</p><p class="transport">{e(r["transport"] or t["unknown"])}</p><p class="zone">{e(r["city"])} / {e(r["zone"])}</p><div class="stop-actions">{links(r)}</div>{details}</div></article>')
        parsed = datetime.fromisoformat(d)
        label = f'{parsed.month}月{parsed.day}日' if locale == "zh-CN" else parsed.strftime("%b %d")
        sections.append(f'<section class="day" data-date="{e(d)}"><h2>{e(label)}</h2>{"".join(cards)}</section>')
    todo = "".join(f'<li><span>{e(r["任务"])}</span><small>{e(day(r["截止日期"]))} · {e(status(r["状态"]))}</small></li>' for r in payload["todos"] if r["状态"] not in ("已完成", "已取消"))
    proposals = "".join(f'<li><span>{e(r["提案"])}</span><small>{e(r["影响项目或日期"])} · {e(r["原因"])}</small></li>' for r in payload["proposals"])
    changes = []
    for c in payload["changes"]:
        target = c["after"] or c["before"]
        body = f'<h3>{e(t[c["kind"]])} · {e(target["activity"])}</h3>'
        if c["fields"]:
            body += '<dl class="diff">' + ''.join(f'<div><dt>{e(zh if locale == "zh-CN" else en)}</dt><dd><span>{e(t["before"])}: {e(c["before"][key] or "—")}</span><span>{e(t["after"])}: {e(c["after"][key] or "—")}</span></dd></div>' for key, zh, en in FIELDS if key in c["fields"]) + '</dl>'
        else:
            body += f'<p>{e(target["date"])} · {e(target["start"])} · {e(target["location"])}</p>'
        changes.append('<article class="change">' + body + '</article>')
    assets = Path(__file__).resolve().parents[1] / "assets"
    template = (assets / "trip-view.html").read_text(encoding="utf-8")
    data = json.dumps(dict(trip=payload, labels=t, statuses=STATUS_ZH if locale == "zh-CN" else STATUS_EN), ensure_ascii=False).replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
    values = dict(LANG=e(locale), TITLE=e(payload["title"]), CSS=(assets / "trip-view.css").read_text(encoding="utf-8"),
                  JS=(assets / "trip-view.js").read_text(encoding="utf-8"), DATA=data,
                  DEMO_NOTICE=f'<p class="notice">{e(payload["demo_notice"])}</p>' if payload.get("demo_notice") else '',
                  DESTINATION=e(payload["destination"]), RANGE=e(payload["start"] + " — " + payload["end"]),
                  VERSION=e(payload["version"]), GENERATED=e(payload["generated"].replace("T", " ").replace("+00:00", " UTC")),
                  DAYS=''.join(sections), DATE_OPTIONS=''.join(f'<option value="{e(d)}">{e(d)}</option>' for d in sorted({r["date"] for r in payload["items"]})),
                  TODOS=todo or f'<li>{e(t["empty"])}</li>', PROPOSALS=proposals or f'<li>{e(t["empty"])}</li>',
                  CHANGES=''.join(changes) or f'<p class="muted">{e(t["nochange"] if payload["previous"] else t["initial"])}</p>',
                  TODO_HIDDEN='' if todo else 'hidden', PROPOSALS_HIDDEN='' if proposals else 'hidden',
                  CHANGES_HIDDEN='' if changes else 'hidden',
                  FILE_DETAILS="关于这份行程" if locale == "zh-CN" else "About this copy",
                  BASELINE=e(payload["previous"]), PRIVATE_HIDDEN='hidden' if payload["audience"] != "personal" else '',
                  AUDIENCE=e(t[payload["audience"]]), WARNING=e(t["snapshot"] if payload["audience"] == "personal" else t["sharewarning"]))
    values.update({"L_" + key.upper(): e(value) for key, value in t.items()})
    import re
    return re.sub(r"\{\{([A-Z_]+)\}\}", lambda m: values[m[1]], template)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--locale", choices=TEXT, default="zh-CN")
    parser.add_argument("--region", choices=REGIONS, default="unknown")
    parser.add_argument("--city-region", action="append", default=[], metavar="CITY=REGION")
    parser.add_argument("--audience", choices=("personal", "companion"), default="personal")
    parser.add_argument("--share-item", action="append", default=[])
    args = parser.parse_args()
    try:
        if args.output.suffix.lower() != ".html" or args.output.exists():
            raise ValueError("Choose a new .html output path; existing files are not overwritten")
        regions = dict(value.split("=", 1) for value in args.city_region)
        content = render(make_payload(workbook_rows(args.workbook), locale=args.locale, region=args.region,
                                      city_regions=regions, audience=args.audience, share_items=args.share_item))
        with args.output.open("x", encoding="utf-8") as output:
            output.write(content)
    except ARCHIVE_ERRORS as error:
        print(f"Export failed: {error}", file=sys.stderr)
        return 1
    print(f"Exported read-only snapshot: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
