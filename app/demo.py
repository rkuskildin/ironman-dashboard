"""Демо-данные: 4 месяца базовой подготовки к Ironman + 3 недели плана вперёд."""
import random
from datetime import date, timedelta

from . import db

# (вид спорта, название, минуты, TSS) по дням недели, Пн = 0
TEMPLATE = {
    0: [("rest", "День отдыха", 0, 0)],
    1: [("swim", "Техника + 10×100 CSS", 60, 55), ("run", "Интервалы 6×3 мин Z4", 55, 65)],
    2: [("bike", "Sweet spot 3×15 мин", 75, 85)],
    3: [("swim", "Аэробная 3000 м", 60, 50), ("run", "Лёгкий бег Z2", 45, 40)],
    4: [("bike", "Восстановительная Z1", 45, 25), ("strength", "Силовая: кор + ноги", 40, 20)],
    5: [("bike", "Длинная Z2", 180, 150)],
    6: [("run", "Длинный бег Z2", 90, 95), ("swim", "Открытая вода / лёгкое", 40, 30)],
}
COACH = ["Держи пульс строго в Z2, не гонись за темпом.",
         "На интервалах каденс 90+, последний отрезок можно чуть быстрее.",
         "После тренировки — обязательно углеводы в первые 30 минут.",
         "Если HRV просел — замени на лёгкую 45 мин.",
         None, None, None]
ATHLETE = ["Тяжело в конце, ноги забиты", "Отлично, самочувствие бодрое", "Жарко, пульс выше обычного", None, None]


def generate(days_back: int = 120, days_forward: int = 21):
    rnd = random.Random(42)
    db.init()
    today = date.today()
    with db.session() as c:
        for t in ("planned_workouts", "activities", "daily_health", "fitness_daily", "sync_log"):
            c.execute(f"DELETE FROM {t}")
        d = today - timedelta(days=days_back)
        n = 0
        hrv_g, hrv_f, rhr = 55.0, 58.0, 52.0
        while d <= today + timedelta(days=days_forward):
            ds = d.isoformat()
            week_no = (d - (today - timedelta(days=days_back))).days // 7
            recovery = week_no % 4 == 3
            scale = (0.6 if recovery else 1.0) * (0.85 + week_no * 0.012)
            fatigue = 0.0
            for i, (sport, title, mins, tss) in enumerate(TEMPLATE[d.weekday()]):
                n += 1
                db.upsert(c, "planned_workouts", {
                    "source": "demo", "source_id": f"p{n}", "date": ds, "sport": sport,
                    "title": title, "description": f"Разминка 10 мин · основная часть · заминка 10 мин",
                    "coach_comments": rnd.choice(COACH),
                    "duration_s": round(mins * scale) * 60 if mins else None,
                    "distance_m": None, "tss": round(tss * scale) if tss else None,
                })
                if sport == "rest" or d > today or (d == today and i > 0):
                    continue
                if rnd.random() < 0.08:  # пропуск
                    continue
                k = rnd.uniform(0.75, 1.15)
                dur = mins * scale * 60 * k
                speed = {"swim": 0.75, "bike": 8.3, "run": 2.9, "strength": 0}.get(sport, 0)
                hr = {"swim": 132, "bike": 138, "run": 148, "strength": 110}.get(sport, 120) + rnd.randint(-6, 8)
                db.upsert(c, "activities", {
                    "source": "demo", "source_id": f"a{n}", "date": ds, "start_time": f"{ds} 07:{10 + i * 30}:00",
                    "sport": sport, "title": title, "duration_s": dur,
                    "distance_m": dur * speed * rnd.uniform(0.95, 1.05) or None,
                    "elevation_m": rnd.randint(50, 900) if sport in ("bike", "run") else None,
                    "avg_hr": hr, "max_hr": hr + rnd.randint(15, 30),
                    "avg_power": rnd.randint(145, 175) if sport == "bike" else None,
                    "np": rnd.randint(160, 190) if sport == "bike" else None,
                    "tss": round(tss * scale * k * rnd.uniform(0.9, 1.1)),
                    "calories": round(dur / 60 * rnd.uniform(9, 13)),
                    "athlete_comments": rnd.choice(ATHLETE),
                })
                fatigue += tss * scale * k
            if d <= today:
                hrv_g += (55 - hrv_g) * 0.2 - fatigue * 0.02 + rnd.uniform(-3, 3)
                hrv_f += (58 - hrv_f) * 0.2 - fatigue * 0.02 + rnd.uniform(-3, 3)
                rhr += (52 - rhr) * 0.25 + fatigue * 0.01 + rnd.uniform(-1, 1)
                sleep = rnd.uniform(6.0, 8.3) * 3600
                for src, hrv, delta in (("garmin", hrv_g, 0), ("fitbit", hrv_f, rnd.uniform(-1.5, 1.5))):
                    db.upsert_health(c, {
                        "date": ds, "source": src, "resting_hr": round(rhr + delta),
                        "hrv": round(hrv, 1), "sleep_s": sleep + rnd.uniform(-900, 900),
                        "deep_s": sleep * rnd.uniform(0.13, 0.2), "rem_s": sleep * rnd.uniform(0.18, 0.25),
                        "sleep_score": rnd.randint(62, 92), "steps": rnd.randint(6000, 16000),
                        "body_battery": rnd.randint(45, 98) if src == "garmin" else None,
                        "stress": rnd.randint(18, 40) if src == "garmin" else None,
                        "readiness": rnd.randint(35, 90) if src == "garmin" else None,
                    })
            d += timedelta(days=1)
    db.log("demo", True, "Демо-данные сгенерированы")
    print("Демо-база готова:", n, "плановых тренировок")
