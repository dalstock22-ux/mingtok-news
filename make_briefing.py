# 밍톡 뉴스 브리핑 생성기 (헤드라인 + 원문 링크만 수집 / 본문 복사 없음)
import json, urllib.request, xml.etree.ElementTree as ET, datetime, html, sys

FEEDS = [
    ("연합뉴스", "https://www.yna.co.kr/rss/economy.xml"),
    ("한국경제", "https://www.hankyung.com/feed/finance"),
]
PER_FEED = 8
KST = datetime.timezone(datetime.timedelta(hours=9))

def fetch(name, url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    data = urllib.request.urlopen(req, timeout=20).read()
    root = ET.fromstring(data)
    out = []
    for it in root.iter("item"):
        t = html.unescape((it.findtext("title") or "").strip())
        u = (it.findtext("link") or "").strip()
        if t and u.startswith("https://"):
            out.append({"t": t, "u": u, "s": name})
        if len(out) >= PER_FEED:
            break
    return out

def main(path):
    lists = []
    for name, url in FEEDS:
        try:
            lists.append(fetch(name, url))
        except Exception as e:
            print("실패:", name, e, file=sys.stderr)
    items, seen = [], set()
    for i in range(PER_FEED):
        for l in lists:
            if i < len(l) and l[i]["t"] not in seen:
                seen.add(l[i]["t"]); items.append(l[i])
    if not items:
        sys.exit("헤드라인을 하나도 못 받아 기존 파일을 유지합니다")
    now = datetime.datetime.now(KST)
    label = "아침 브리핑" if now.hour < 14 else "저녁 브리핑"
    json.dump({"updated": now.strftime("%Y-%m-%d %H:%M"), "label": label, "items": items},
              open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(label, len(items), "건")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "briefing.json")
