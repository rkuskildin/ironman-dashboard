"""Календарь стартов в России: бег, трейл, велосипед, открытая вода, триатлон.

Источники (только публичные GET, с паузами по robots.txt; ошибка одного не ломает остальные):
  russiarunning (JSON API, координаты), probeg.org (год вперёд + трейлы + триатлон),
  marathonec.ru (бег, трейл, заплывы), swimcup.ru, x-waters.com, iron-star.com,
  reg.place, myrace.info, mountain-race.ru.
Обновляется раз в сутки; дубли с разных сайтов склеиваются по (имя, дата) или (дата, город, похожее имя).
Координаты для карты — из источника или через OpenStreetMap Nominatim (с кэшем).
"""
import datetime as dt
import hashlib
import html as htmlmod
import json
import re
import time

import httpx

from . import db

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126 Safari/537.36"
GEO_UA = "IronmanDashboard/1.0 (+https://github.com/rkuskildin/ironman-dashboard)"
MON = {m: i + 1 for i, m in enumerate("января февраля марта апреля мая июня июля августа сентября октября ноября декабря".split())}
MON_NOM = {m: i + 1 for i, m in enumerate("январь февраль март апрель май июнь июль август сентябрь октябрь ноябрь декабрь".split())}

SCHEMA = """
CREATE TABLE IF NOT EXISTS race_cal (id TEXT PRIMARY KEY, start TEXT, data TEXT);
CREATE TABLE IF NOT EXISTS race_cal_src (source TEXT PRIMARY KEY, ok INTEGER, count INTEGER, message TEXT, updated TEXT);
CREATE TABLE IF NOT EXISTS race_marks (id TEXT PRIMARY KEY, created TEXT DEFAULT (datetime('now','localtime')));
CREATE TABLE IF NOT EXISTS rr_cache (code TEXT PRIMARY KEY, data TEXT, fetched REAL);
CREATE TABLE IF NOT EXISTS geocache (q TEXT PRIMARY KEY, lat REAL, lon REAL, country TEXT, region TEXT);
"""


def init():
    with db.session() as c:
        c.executescript(SCHEMA)


# ---------------- общее ----------------
_last_hit: dict[str, float] = {}


def get(url: str, delay: float = 2.0, accept: str = "text/html") -> str:
    """GET с паузой между запросами к одному сайту (crawl-delay)."""
    host = url.split("/")[2]
    wait = delay - (time.time() - _last_hit.get(host, 0))
    if wait > 0:
        time.sleep(wait)
    r = httpx.get(url, headers={"User-Agent": UA, "Accept": accept}, timeout=40, follow_redirects=True)
    _last_hit[host] = time.time()
    r.raise_for_status()
    return r.text


txt = lambda s: re.sub(r"\s+", " ", htmlmod.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def km_from_text(s: str) -> list[float]:
    out = set()
    for x in re.findall(r"(\d+(?:[.,]\d+)?)\s*км", s or ""):
        out.add(float(x.replace(",", ".")))
    for x in re.findall(r"(\d[\d ]*)\s*м\b", s or ""):
        v = float(x.replace(" ", "")) / 1000
        if 0.05 <= v <= 30:
            out.add(round(v, 3))
    return sorted(out)


def clean_name(n: str) -> str:
    n = re.sub(r"\s*Регистрация\s*$", "", (n or "").strip())
    n = re.sub(r"\s*\|\s*\d{1,2}\s+[а-я]+\s*$", "", n)          # «… | 31 октября»
    return n.strip(" |")


ONLINE = re.compile(r"(?i)онлайн|online|zwift|виртуальн|virtual")


def ev(source, name, start, end=None, city=None, sport="run", km=None, url=None, reg=None, site=None,
       lat=None, lon=None, extra=None) -> dict:
    name = clean_name(name)
    return {"source": source, "name": name, "online": bool(ONLINE.search(name or "")), "start": start, "end": end or start, "city": (city or "").strip(),
            "sport": sport, "km": sorted(set(km or [])), "url": url, "reg": reg, "site": site,
            "lat": lat, "lon": lon, **(extra or {})}


def sport_from_name(name: str, default: str) -> str:
    n = name.lower()
    if any(k in n for k in ("триатлон", "triathlon", "ironstar", "дуатлон", "акватлон", "swimrun")):
        return "tri"
    if any(k in n for k in ("трейл", "trail", "скайран", "горн", "ультра")):
        return "trail"
    if any(k in n for k in ("вело", "гранфондо", "gran fondo", "mtb", "мтб", "кросс-кантри", "шоссейн")):
        return "bike"
    if any(k in n for k in ("заплыв", "плаван", "swim", "x-waters")):
        return "swim"
    return default


# ---------------- источники ----------------
def src_russiarunning() -> list[dict]:
    xml = get("https://reg.russiarunning.com/sitemap.xml", 1)
    codes = re.findall(r"<loc>https://reg\.russiarunning\.com/event/([^<]+)</loc>", xml)
    now = time.time()
    with db.session() as c:
        cache = {r["code"]: (json.loads(r["data"]), r["fetched"]) for r in c.execute("SELECT * FROM rr_cache")}
    out, today = [], dt.date.today().isoformat()
    DISC = {"run": "run", "trail": "trail", "cycling": "bike", "swimming": "swim", "triathlon": "tri",
            "duathlon": "tri", "aquathlon": "tri", "swimrun": "tri"}
    for code in codes:
        d, fetched = cache.get(code, (None, 0))
        stale = not d or now - fetched > 7 * 86400 or (d.get("start", "") >= today and d.get("start", "") <= (dt.date.today() + dt.timedelta(days=14)).isoformat() and now - fetched > 86400)
        if stale:
            try:
                j = json.loads(get(f"https://reg.russiarunning.com/api/events/detailedEvent?Language=ru&EventCode={code}", 1, "application/json"))
            except Exception:
                if not d:
                    continue
            else:
                races = j.get("races") or []
                # только нужное, без данных организатора (ИНН, телефоны)
                d = {"name": j.get("title"), "start": (j.get("beginDate") or "")[:10], "end": (j.get("endDate") or "")[:10],
                     "place": j.get("place") or j.get("eventAddress"), "lat": j.get("latitude"), "lon": j.get("longitude"),
                     "disc": sorted({r.get("disciplineCode") or j.get("disciplineCode") or "run" for r in races} or {j.get("disciplineCode") or "run"}),
                     "km": sorted({r["distance"] for r in races if r.get("distance")}), "site": j.get("mainLink")}
                with db.session() as c:
                    c.execute("INSERT OR REPLACE INTO rr_cache VALUES (?,?,?)", (code, json.dumps(d), now))
        if not d or not d.get("start") or d["start"] < today:
            continue
        sports = [DISC.get(x, "run") for x in d["disc"]]
        sport = next((s for s in ("tri", "swim", "bike", "trail") if s in sports), "run")
        out.append(ev("russiarunning", d["name"], d["start"], d["end"], d["place"], sport, d["km"],
                      f"https://reg.russiarunning.com/event/{code}", f"https://reg.russiarunning.com/event/{code}",
                      d.get("site"), d.get("lat") or None, d.get("lon") or None))
    return out


def _probeg_rows_year(s: str) -> list[dict]:
    T = lambda x: re.sub(r"\s+", " ", htmlmod.unescape(re.sub(r"<br\s*/?>", " | ", re.sub(r"<(?!br)[^>]+>", "", x)))).strip(" |")
    year, prev, out = dt.date.today().year, 0, []
    for tr in re.findall(r'<tr style="font-size: 11px;">(.*?)</tr>', s, re.S):
        tds = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
        if len(tds) < 6:
            continue
        d = T(tds[1]).replace("–", "-")
        a, _, b = d.partition("-")
        b = b or a
        try:
            em = int(b.split(".")[1]); sm = int(a.split(".")[1]) if "." in a else em
        except (IndexError, ValueError):
            continue
        if sm < prev:
            year += 1
        prev = sm
        start = dt.date(year, sm, int(a.split(".")[0]))
        end = dt.date(year + (em < sm), em, int(b.split(".")[0]))
        m = re.search(r"/event/(\d+)/", tds[2])
        name = T(re.sub(r"<br/>.*|<span class=\"pull-right\">.*", "", tds[2], flags=re.S))
        links = re.findall(r'<a href="([^"]+)">([^<]+)</a>', tds[5])
        out.append(ev("probeg", name, start.isoformat(), end.isoformat(), T(tds[3]), sport_from_name(name, "run"),
                      km_from_text(T(tds[4])), f"https://probeg.org/event/{m.group(1)}/" if m else None,
                      next((u for u, t in links if "Регистр" in t), None), next((u for u, t in links if t == "Сайт"), None)))
    return out


def _probeg_rows_cal(s: str, sport: str) -> list[dict]:
    T = lambda x: re.sub(r"\s+", " ", htmlmod.unescape(re.sub(r"<br\s*/?>", " | ", re.sub(r"<(?!br)[^>]+>", "", x)))).strip(" |")
    out = []
    for tr in re.findall(r"<tr>(<td class=\"text-right\">\d+</td>.*?)</tr>", s, re.S):
        tds = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
        if len(tds) < 5:
            continue
        d = T(tds[1]).replace("–", "-")
        try:
            y = d[-4:]; a, _, b = d.partition("-"); b = b or a
            end = dt.date(int(y), int(b[3:5]), int(b[:2]))
            sa = a.split(".")
            start = dt.date(int(y), int(sa[1]) if len(sa) > 1 and sa[1] else end.month, int(sa[0]))
        except (ValueError, IndexError):
            continue
        m = re.search(r"/event/(\d+)/", tds[2])
        name = T(re.sub(r'<span class="pull-right">.*', "", tds[2], flags=re.S)).split(" | ")[0]
        links = re.findall(r'<a href="([^"]+)">([^<]+)</a>', tds[-1])
        out.append(ev("probeg", name, start.isoformat(), end.isoformat(), T(tds[3]), sport, km_from_text(T(tds[4])),
                      f"https://probeg.org/event/{m.group(1)}/" if m else None,
                      next((u for u, t in links if "Регистр" in t), None), next((u for u, t in links if t == "Сайт"), None)))
    return out


def src_probeg() -> list[dict]:
    out = _probeg_rows_year(get("https://probeg.org/races/year_ahead/", 31))
    out += _probeg_rows_cal(get("https://probeg.org/calendar/trails/", 31), "trail")
    out += _probeg_rows_cal(get("https://probeg.org/calendar/triathlon/", 31), "tri")
    return out


def src_marathonec() -> list[dict]:
    pages = {"run": "https://marathonec.ru/calendar-beg/", "trail": "https://marathonec.ru/kalendar-trejlovyx-zabegov-rossii/",
             "swim": "https://marathonec.ru/kalendar-zaplyvov/"}
    ROW = re.compile(r'<tr id="post-row-(\d+)"[^>]*>(.*?)</tr>', re.S)
    TD = re.compile(r'<td([^>]*)>(.*?)</td>', re.S)
    out = []
    for sport, url in pages.items():
        for pid, row in ROW.findall(get(url, 3)):
            tds = TD.findall(row)
            try:
                ts = int(re.search(r'data-sort="(\d+)"', tds[0][0]).group(1))
            except (AttributeError, IndexError):
                continue
            d = dt.datetime.fromtimestamp(ts, dt.timezone.utc).date().isoformat()
            href = (re.search(r'href="([^"#]+)', tds[1][1]) or [None, None])[1]
            km = [float(x.replace("-", ".")) for x in re.findall(r'data-slug="([\d-]+)-km"', tds[2][1])]
            name = txt(tds[1][1])
            out.append(ev("marathonec", name, d, d, txt(tds[3][1]) if len(tds) > 3 else "", sport_from_name(name, sport), km, href))
    return out


def src_swimcup() -> list[dict]:
    s = get("https://swimcup.ru/series/", 3)
    out = []
    for li in re.findall(r'<li class="results__list"[^>]*>(.*?)</li>', s, re.S):
        col = lambda c: txt((re.search(rf'results__col--{c}">(.*?)</span>\s*(?=<span class="results__|$)', li, re.S) or [0, ""])[1])
        name = col("name"); y = re.search(r"(20\d\d)", name)
        m = re.match(r"(\d+)(?:\s+(\w+))?(?:\s*-\s*(\d+)\s+(\w+))?", col("cal"))
        if not (y and m):
            continue
        d1, m1, d2, m2 = m.groups(); y = int(y.group(1))
        try:
            start = dt.date(y, MON[(m1 or m2).lower()], int(d1)); end = dt.date(y, MON[(m2 or m1).lower()], int(d2 or d1))
        except (KeyError, ValueError, AttributeError):
            continue
        dist = col("clock")
        nums = [float(x.replace(" ", "")) for x in re.findall(r"\d[\d ]*\d|\d", re.sub(r"\d+[хx]\d+", "", dist))]
        det = re.search(r'href="(/series/[^"]+)"', li); reg = re.search(r'href="(https?://[^"]+)"[^>]*>\s*Регистрация', li)
        out.append(ev("swimcup", name, start.isoformat(), end.isoformat(), col("city"), "swim", [round(n / 1000, 3) for n in nums if n],
                      "https://swimcup.ru" + det.group(1) if det else None, reg.group(1) if reg else None))
    return out


def src_xwaters() -> list[dict]:
    s = get("https://x-waters.com/events/", 3)
    out = []
    for href, body in re.findall(r'<a href="(https://x-waters\.com/events/[^"]+)" class="project_itm">(.*?)</a>', s, re.S):
        g = lambda c: txt((re.search(rf'class="{c}[^"]*">(.*?)</div>', body, re.S) or [None, ""])[1])
        m = re.match(r"(\d+)(?:\s*-\s*(\d+))?\s+(\w+)\s+(\d{4})", g("project_itm__date"))
        if not m:
            continue
        d1, d2, mon, y = m.groups()
        try:
            mo = MON[mon.lower()]
        except KeyError:
            continue
        name = g("project_itm__title")
        city = re.sub(r"(?i)x-waters|\d{4}|мск", "", name).strip(" -") or None
        out.append(ev("x-waters", name, dt.date(int(y), mo, int(d1)).isoformat(), dt.date(int(y), mo, int(d2 or d1)).isoformat(),
                      city, "swim", [], href, href + "#reg"))
    return out


def src_ironstar() -> list[dict]:
    s = get("https://iron-star.com/event", 3)
    out = []
    for href, title, body in re.findall(r'<a href="(/event/[a-z0-9-]+)" title="([^"]+)" class="event-item">(.*?)</a>', s, re.S):
        try:
            name, date, city = [x.strip() for x in htmlmod.unescape(title).rsplit(" - ", 2)]
            d = dt.datetime.strptime(date, "%d.%m.%Y").date().isoformat()
        except ValueError:
            continue
        legs = [re.sub(r"<!--.*?-->|<[^>]+>", "", x).strip() for x in re.findall(r'<div class="distance">(.*?)</div>', body, re.S)]
        km = []
        for x in legs:
            v = re.sub(r"[^\d.,]", "", x).replace(",", ".")
            if v:
                km.append(float(v) / (1000 if " м" in x and "км" not in x else 1))
        u = name.upper()
        sport = "swim" if "SWIMSTAR" in u else "run" if any(k in u for k in ("RUNSTAR", "MANSTAR", "ЗАБЕГ")) else "tri"
        out.append(ev("ironstar", name, d, d, city, sport, km, "https://iron-star.com" + href, "https://iron-star.com" + href,
                      extra={"legs": legs}))
    return out


def _nearest(day: int, mon: int) -> dt.date:
    t = dt.date.today()
    x = dt.date(t.year, mon, day)
    return x if x >= t - dt.timedelta(days=7) else x.replace(year=t.year + 1)


def src_regplace() -> list[dict]:
    out, page = [], 1
    SP = {"Бег": "run", "Плавание": "swim", "Велогонка": "bike", "Триатлон": "tri", "Трейл": "trail", "Велоспорт": "bike"}
    while page <= 12:
        s = get(f"https://reg.place/events?page={page}", 3)
        for c in re.findall(r'<article class="b-event-card[^"]*">(.*?)</article>', s, re.S):
            sl = re.search(r'href="/events/([^"?/]+)', c)
            meta = re.search(r'b-event-card__meta"><strong>(.*?)</strong>(.*?)</p>', c, re.S)
            title = re.search(r'b-event-card__title-link"[^>]*>(.*?)</a>', c, re.S)
            if not (sl and meta and title):
                continue
            when = txt(meta.group(1)).replace("—", "–")
            parts = [txt(p) for p in re.split(r'<span class="px-2">•</span>', meta.group(2))][1:]
            a, _, b = [x.strip() for x in when.partition("–")]
            if b and len(a.split()) == 1:
                a += " " + b.split()[1]
            try:
                da, ma = a.split()[:2]; start = _nearest(int(da), MON[ma])
                end = start
                if b:
                    db_, mb = b.split()[:2]; end = _nearest(int(db_), MON[mb])
            except (ValueError, KeyError):
                continue
            name = txt(title.group(1)); sport_txt = parts[-1] if parts else ""
            sport = SP.get(sport_txt, sport_from_name(name, "run"))
            if sport_txt == "Плавание" and "бассейн" in name.lower():
                continue  # соревнования в бассейне — не про открытую воду
            out.append(ev("reg.place", name, start.isoformat(), end.isoformat(), parts[0] if len(parts) == 2 else "",
                          sport, [], f"https://reg.place/events/{sl.group(1)}", f"https://reg.place/events/{sl.group(1)}"))
        if f'href="/events?page={page + 1}"' not in s:
            break
        page += 1
    return out


def src_myrace() -> list[dict]:
    s = get("https://myrace.info/events", 11)
    SP = {"Трейл": "trail", "Бег": "run", "Велоспорт": "bike", "Акватлон": "tri", "SwimRun": "tri", "Триатлон": "tri", "Плавание": "swim"}
    out = []
    for eid, body in re.findall(r'<a href="/events/(\d+)" class="events-list__item[^"]*">(.*?)</a>', s, re.S):
        g = lambda c: txt((re.search(rf'class="{c}">(.*?)</div>', body, re.S) or [0, ""])[1])
        m = re.match(r"(\d+)(?:\s+(\w+))?(?:\s*-\s*(\d+)\s+(\w+))?", g("date"))
        h2 = re.search(r"<h2>(.*?)</h2>", body, re.S)
        if not (m and h2):
            continue
        d1, m1, d2, m2 = m.groups()
        try:
            start = _nearest(int(d1), MON[(m1 or m2).lower()])
            end = _nearest(int(d2 or d1), MON[(m2 or m1).lower()])
            if end < start:
                end = end.replace(year=start.year + 1)
        except (KeyError, ValueError, AttributeError):
            continue
        name = txt(h2.group(1))
        out.append(ev("myrace", name, start.isoformat(), end.isoformat(), g("flag"), SP.get(g("type"), sport_from_name(name, "run")),
                      [], f"https://myrace.info/events/{eid}", f"https://myrace.info/events/{eid}"))
    return out


def src_mountainrace() -> list[dict]:
    s = get("https://mountain-race.ru/events/", 3)
    out, year = [], dt.date.today().year
    for part in re.split(r"(<h\d[^>]*>\s*(?:%s) \d{4}\s*</h\d>)" % "|".join(m.capitalize() for m in MON_NOM), s)[1:]:
        hm = re.search(r">\s*(\w+) (\d{4})\s*<", part)
        if hm and hm.group(1).lower() in MON_NOM:
            year = int(hm.group(2)); continue
        for row in re.findall(r'<div class="row g-2 mx-0 mt-0 px-1 py-3 border-bottom border-info">(.*?)(?=<div class="row g-2 mx-0 mt-0 px-1 py-3|$)', part, re.S):
            try:
                d = re.search(r'fs-4 fw-medium">([^<]+)', row).group(1).split("–")
                a = [int(x) for x in d[0].strip().split(".")]; b = [int(x) for x in d[-1].strip().split(".")]
                start = dt.date(year, a[1], a[0]); end = dt.date(year + (b[1] < a[1]), b[1], b[0])
                link = re.search(r'<a href="(/events/[^"]+)" class="d-block fs-lg fw-medium">(.*?)</a>', row, re.S)
                place = txt(re.search(r'map-marker"></use></svg>(.*?)</div>', row, re.S).group(1))
            except (AttributeError, ValueError, IndexError):
                continue
            tags = [txt(t) for t in re.findall(r'<span class="px-1">(.*?)</span>', row)]
            out.append(ev("mountain-race", txt(link.group(2)), start.isoformat(), end.isoformat(), place, "trail",
                          [float(t[:-3]) for t in tags if re.fullmatch(r"[\d.]+ км", t)], "https://mountain-race.ru" + link.group(1)))
    return out


SOURCES = {
    "russiarunning": src_russiarunning, "probeg": src_probeg, "marathonec": src_marathonec, "swimcup": src_swimcup,
    "x-waters": src_xwaters, "ironstar": src_ironstar, "reg.place": src_regplace, "myrace": src_myrace,
    "mountain-race": src_mountainrace,
}
SOURCE_NAMES = {"russiarunning": "RussiaRunning", "probeg": "ПроБЕГ", "marathonec": "Марафонец", "swimcup": "Swimcup",
                "x-waters": "X-WATERS", "ironstar": "IRONSTAR", "reg.place": "reg.place", "myrace": "MyRace", "mountain-race": "Mountain Race"}


# ---------------- склейка дублей ----------------
STOP = {"забег", "марафон", "полумарафон", "трейл", "заплыв", "the", "run", "race", "кубок", "фестиваль", "открытый", "открытая", "вода"}


def _norm(name: str) -> str:
    n = re.sub(r"20\d\d", "", name.lower().replace("ё", "е"))
    return re.sub(r"[^a-zа-я0-9]+", " ", n).strip()


def _tokens(name: str) -> set[str]:
    return {t for t in _norm(name).split() if len(t) > 2 and t not in STOP}


def _city_key(c: str) -> str:
    c = re.sub(r"(?i)\b(г|город|пос|п|с|д|обл|область|р-н|район|респ|республика)\.?\s", " ", (c or "").lower())
    parts = [p.strip() for p in re.split(r"[,(]", c) if p.strip()]
    return parts[-1] if parts else ""


def merge(events: list[dict]) -> list[dict]:
    PRIO = list(SOURCES)  # russiarunning первым — у него координаты и регистрация
    events = sorted(events, key=lambda e: PRIO.index(e["source"]))
    out: list[dict] = []
    by_date: dict[str, list[dict]] = {}
    for e in events:
        if not e["name"] or not e["start"]:
            continue
        cand = by_date.get(e["start"], [])
        tk, nk = _tokens(e["name"]), _norm(e["name"])
        hit = None
        for o in cand:
            ot = _tokens(o["name"])
            same_name = nk == _norm(o["name"]) or (tk and ot and len(tk & ot) / min(len(tk), len(ot)) >= 0.6)
            if same_name:
                hit = o
                break
        if hit:
            hit["sources"].append(e["source"])
            hit["links"].setdefault(e["source"], e["url"])
            hit["km"] = sorted(set(hit["km"]) | set(e["km"]))
            for k in ("reg", "site", "lat", "lon", "city"):
                if not hit.get(k) and e.get(k):
                    hit[k] = e[k]
            if hit["sport"] == "run" and e["sport"] != "run":
                hit["sport"] = e["sport"]
            continue
        e = {**e, "sources": [e["source"]], "links": {e["source"]: e["url"]}}
        e["id"] = hashlib.md5(f"{nk}|{e['start']}".encode()).hexdigest()[:12]
        out.append(e)
        by_date.setdefault(e["start"], []).append(e)
    return out


# ---------------- координаты ----------------
def geocode(city: str) -> tuple | None:
    q = re.sub(r"\s+", " ", (city or "").strip())
    if not q or len(q) < 2:
        return None
    with db.session() as c:
        row = c.execute("SELECT * FROM geocache WHERE q=?", (q,)).fetchone()
    if row:
        return (row["lat"], row["lon"], row["country"], row["region"]) if row["lat"] is not None else None
    res = None
    for query in (q, _city_key(q)):
        if not query:
            continue
        wait = 1.1 - (time.time() - _last_hit.get("nominatim", 0))
        if wait > 0:
            time.sleep(wait)
        try:
            r = httpx.get("https://nominatim.openstreetmap.org/search",
                          params={"q": query, "format": "jsonv2", "limit": 1, "accept-language": "ru", "addressdetails": 1},
                          headers={"User-Agent": GEO_UA}, timeout=20)
            _last_hit["nominatim"] = time.time()
            j = r.json() if r.status_code == 200 else []
        except Exception:
            j = []
        if j:
            a = j[0].get("address") or {}
            res = (float(j[0]["lat"]), float(j[0]["lon"]), a.get("country_code", ""), a.get("state") or a.get("region") or "")
            break
    with db.session() as c:
        c.execute("INSERT OR REPLACE INTO geocache VALUES (?,?,?,?,?)", (q, *(res or (None, None, None, None))))
    return res


def _region(e: dict) -> str:
    if e.get("online"):
        return "online"
    c = (e.get("country") or "").lower()
    if c and c != "ru":
        return "abroad"
    st = (e.get("state") or "") + " " + (e.get("city") or "")
    if re.search(r"москв|подмосков|московск", st, re.I):
        return "moscow"
    return "russia"


# ---------------- обновление ----------------
def refresh(sources: list[str] | None = None, geocode_limit: int = 400) -> dict:
    init()
    collected, report = [], {}
    for name, fn in SOURCES.items():
        if sources and name not in sources:
            continue
        try:
            items = fn()
            collected += items
            report[name] = len(items)
            ok, msg = 1, f"{len(items)} событий"
        except Exception as e:
            ok, msg = 0, f"{type(e).__name__}: {str(e)[:150]}"
            report[name] = msg
        with db.session() as c:
            c.execute("INSERT OR REPLACE INTO race_cal_src VALUES (?,?,?,?,datetime('now','localtime'))",
                      (name, ok, report[name] if ok else 0, msg))
    if sources:  # частичное обновление — добавить к уже собранным из других источников
        with db.session() as c:
            keep = [json.loads(r["data"]) for r in c.execute("SELECT data FROM race_cal")]
        for k in keep:
            for s in k["sources"]:
                if s not in sources:
                    collected.append({**k, "source": s, "url": k["links"].get(s)})
    today = dt.date.today().isoformat()
    merged = [e for e in merge(collected) if (e.get("end") or e["start"]) >= today]
    n_geo = 0
    for e in merged:
        if e.get("lat") and e.get("lon"):
            e.setdefault("country", "ru" if not re.search(r"(?i)армени|казах|беларус|груз|турц|египет|таиланд|оаэ|сербия|кипр", e.get("city") or "") else "")
            continue
        if n_geo >= geocode_limit:
            continue
        g = geocode(e.get("city") or "")
        n_geo += 1
        if g:
            e["lat"], e["lon"], e["country"], e["state"] = g
    for e in merged:
        e["region"] = _region(e)
    with db.session() as c:
        c.execute("DELETE FROM race_cal")
        c.executemany("INSERT INTO race_cal VALUES (?,?,?)", [(e["id"], e["start"], json.dumps(e, ensure_ascii=False)) for e in merged])
        c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('race_cal_updated', ?)", (json.dumps(time.strftime("%Y-%m-%d %H:%M")),))
    return {"events": len(merged), "by_source": report, "with_coords": sum(1 for e in merged if e.get("lat"))}


def list_events() -> dict:
    init()
    with db.session() as c:
        rows = [json.loads(r["data"]) for r in c.execute("SELECT data FROM race_cal ORDER BY start")]
        marks = {r["id"] for r in c.execute("SELECT id FROM race_marks")}
        src = [dict(r) for r in c.execute("SELECT * FROM race_cal_src ORDER BY source")]
        upd = c.execute("SELECT value FROM settings WHERE key='race_cal_updated'").fetchone()
    for e in rows:
        e["marked"] = e["id"] in marks
        e.pop("source", None)
        e.pop("url", None)
    return {"events": rows, "sources": src, "source_names": SOURCE_NAMES, "updated": json.loads(upd["value"]) if upd else None}


def toggle_mark(eid: str) -> bool:
    init()
    with db.session() as c:
        if c.execute("SELECT 1 FROM race_marks WHERE id=?", (eid,)).fetchone():
            c.execute("DELETE FROM race_marks WHERE id=?", (eid,))
            return False
        c.execute("INSERT INTO race_marks (id) VALUES (?)", (eid,))
        return True


def due() -> bool:
    with db.session() as c:
        row = c.execute("SELECT value FROM settings WHERE key='race_cal_updated'").fetchone()
    if not row:
        return True
    last = dt.datetime.strptime(json.loads(row["value"]), "%Y-%m-%d %H:%M")
    return (dt.datetime.now() - last).total_seconds() > 20 * 3600 and 2 <= dt.datetime.now().hour <= 6
