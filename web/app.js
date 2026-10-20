/* Ironman Dashboard — клиент. Без сборки: чистый JS + Chart.js. */
// Линейные значки 24×24 (stroke), чтобы не зависеть от эмодзи
const ICONS = {
  swim: '<path d="M2 12c1.7 0 2.3-1.5 4-1.5s2.3 1.5 4 1.5 2.3-1.5 4-1.5 2.3 1.5 4 1.5 2.3-1.5 4-1.5"/><path d="M2 17c1.7 0 2.3-1.5 4-1.5s2.3 1.5 4 1.5 2.3-1.5 4-1.5 2.3 1.5 4 1.5 2.3-1.5 4-1.5"/><circle cx="16" cy="6" r="1.6"/><path d="m6 9 4-3 3 3"/>',
  bike: '<circle cx="18.5" cy="17.5" r="3.5"/><circle cx="5.5" cy="17.5" r="3.5"/><circle cx="15" cy="5" r="1"/><path d="M12 17.5V14l-3-3 4-3 2 3h2"/>',
  run: '<circle cx="14" cy="4.5" r="1.8"/><path d="m8 21 3.5-6 3 2.5V22"/><path d="m6 12 3-4 5 1 2 3h3"/><path d="m11.5 15-2-4"/>',
  strength: '<path d="m6.5 6.5 11 11"/><path d="m21 21-1-1"/><path d="m3 3 1 1"/><path d="m18 22 4-4"/><path d="m2 6 4-4"/><path d="m3 10 7-7"/><path d="m14 21 7-7"/>',
  hockey: '<path d="M8 3l6 13a2 2 0 0 0 1.8 1.2H21"/><ellipse cx="7" cy="18.5" rx="3.5" ry="1.6"/>',
  football: '<circle cx="12" cy="12" r="9"/><path d="m12 7.5 3.2 2.3-1.2 3.8h-4l-1.2-3.8z"/><path d="M12 3v4.5M15.2 9.8l4.5-1.6M14 13.6l2.7 3.9M10 13.6l-2.7 3.9M8.8 9.8 4.3 8.2"/>',
  other: '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="2.5"/>',
  transition: '<path d="M4 8h13l-3-3M20 16H7l3 3"/>',
  trail: '<path d="m3 20 6-10 4 6 2.5-3.5L21 20z"/><circle cx="16" cy="5" r="1.6"/>',
  tri: '<circle cx="6" cy="15" r="3"/><circle cx="18" cy="15" r="3"/><circle cx="12" cy="7" r="3"/>',
  pin: '<path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
  star: '<path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1 6.2-5.5-2.9-5.5 2.9 1-6.2L3 9.6l6.2-.9z"/>',
  link: '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
  rest: '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>',
  home: '<path d="M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/>',
  calendar: '<rect x="3" y="4" width="18" height="17" rx="2.5"/><path d="M16 2.5v3M8 2.5v3M3 9.5h18"/>',
  trend: '<path d="m3 17 6-6 4 4 8-8"/><path d="M14 7h7v7"/>',
  heart: '<path d="M19 14c1.5-1.5 3-3.2 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.8 0-3 .5-4.5 2-1.5-1.5-2.7-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4 3 5.5l7 7Z"/>',
  sliders: '<path d="M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3M1 14h6M9 8h6M17 16h6"/>',
  refresh: '<path d="M21 12a9 9 0 1 1-2.6-6.4L21 8"/><path d="M21 3v5h-5"/>',
  alert: '<path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4M12 17h.01"/>',
  check: '<circle cx="12" cy="12" r="9"/><path d="m8 12 3 3 5-6"/>',
  moon: '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>',
  gauge: '<path d="M12 14l4-4"/><path d="M3.3 19a10 10 0 1 1 17.4 0"/>',
  flag: '<path d="M4 22V4a1 1 0 0 1 1-1h12l-2 4 2 4H5"/>',
  bolt: '<path d="M13 2 3 14h9l-1 8 10-12h-9z"/>',
  pulse: '<path d="M3 12h4l3-8 4 16 3-8h4"/>',
  target: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  chat: '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
  print: '<path d="M6 9V2h12v7"/><rect x="6" y="14" width="12" height="8" rx="1"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/>',
  scale: '<path d="M6 3h12l3 18H3z"/><path d="M12 8v4"/><circle cx="12" cy="13" r="1"/>',
  logout: '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="m16 17 5-5-5-5M21 12H9"/>',
};
const icon = (name, cls = "") => `<svg class="ico ${cls}" viewBox="0 0 24 24" aria-hidden="true">${ICONS[name] || ICONS.other}</svg>`;
const SPORT = {
  swim: { name: "Плавание" }, bike: { name: "Велосипед" }, run: { name: "Бег" }, strength: { name: "Силовая" },
  hockey: { name: "Хоккей" }, football: { name: "Футбол" }, transition: { name: "Переход" }, other: { name: "Другое" }, rest: { name: "Отдых" },
};
for (const k in SPORT) SPORT[k].ico = icon(k);
const sportColor = (s) => `var(--${s in SPORT && !["rest", "other"].includes(s) ? s : "other"})`;
const STATUS = {
  done: "Выполнено", partial: "Частично", off: "Отклонение", missed: "Пропущено",
  upcoming: "Запланировано", today: "Сегодня", unplanned: "Вне плана", rest: "Отдых",
};
const SRC = { garmin: "Garmin", fitbit: "Fitbit" };
const DOW = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"];
const MONTHS = ["янв", "фев", "мар", "апр", "мая", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"];

// ---------- Garmin: перевод разбора ----------
const TE_LABEL = {
  RECOVERY: "Восстановление", AEROBIC_BASE: "Аэробная база", TEMPO: "Темп", LACTATE_THRESHOLD: "Порог (ПАНО)",
  VO2MAX: "VO2 max", ANAEROBIC_CAPACITY: "Анаэробная ёмкость", SPEED: "Скорость", SPRINT: "Спринт",
};
const TE_OBJ = {
  AEROBIC_BASE: "аэробную базу", AEROBIC_FITNESS: "аэробную форму", LACTATE_THRESHOLD: "порог (ПАНО)",
  VO2_MAX: "VO2 max", TEMPO: "темповую выносливость", ANAEROBIC_CAPACITY: "анаэробную ёмкость",
  ANAEROBIC_FITNESS: "анаэробную форму", ANAEROBIC_POWER: "анаэробную мощность", SPEED: "скорость", ECONOMY: "экономичность",
};
function teMessage(code) {
  if (!code) return "";
  const c = code.replace(/_\d+$/, "");
  const fixed = {
    NO_AEROBIC_BENEFIT: "Нет аэробного эффекта", NO_ANAEROBIC_BENEFIT: "Нет анаэробного эффекта",
    MINOR_AEROBIC_BENEFIT: "Незначительный аэробный эффект", MINOR_ANAEROBIC_BENEFIT: "Незначительный анаэробный эффект",
    RECOVERY: "Восстановительная нагрузка", OVERREACHING: "Перегрузка — дайте организму восстановиться",
    AEROBIC_OVERREACHING: "Аэробная перегрузка", ANAEROBIC_OVERREACHING: "Анаэробная перегрузка",
  };
  if (fixed[c]) return fixed[c];
  const m = c.match(/^(HIGHLY_IMPROVING|IMPROVING|MAINTAINING)_(.+)$/);
  if (m) {
    const verb = { HIGHLY_IMPROVING: "Сильно развивает", IMPROVING: "Развивает", MAINTAINING: "Поддерживает" }[m[1]];
    return `${verb} ${TE_OBJ[m[2]] || m[2].toLowerCase().replaceAll("_", " ")}`;
  }
  return c.toLowerCase().replaceAll("_", " ");
}
const teScale = (v) => v == null ? "" : v < 1 ? "нет эффекта" : v < 2 ? "незначительный" : v < 3 ? "поддерживает" : v < 4 ? "улучшает" : v < 5 ? "сильно улучшает" : "перегрузка";
const STATUS_PHRASE = { NO_STATUS: "Нет статуса — мало данных", PRODUCTIVE: "Продуктивно", MAINTAINING: "Поддержание формы",
  RECOVERY: "Восстановление", UNPRODUCTIVE: "Непродуктивно", DETRAINING: "Потеря формы", PEAKING: "Пик формы",
  OVERREACHING: "Перегрузка", STRAINED: "Напряжение" };
const ACWR = { LOW: "низкая", OPTIMAL: "оптимальная", HIGH: "высокая", VERY_HIGH: "очень высокая" };
const BALANCE_PHRASE = { BELOW_TARGETS: "Ниже целей по всем видам нагрузки", BALANCED: "Сбалансировано",
  ABOVE_TARGETS: "Выше целей", AEROBIC_LOW_SHORTAGE: "Не хватает низкой аэробной нагрузки",
  AEROBIC_HIGH_SHORTAGE: "Не хватает высокой аэробной нагрузки", ANAEROBIC_SHORTAGE: "Не хватает анаэробной нагрузки",
  AEROBIC_LOW_FOCUS: "Фокус на низкой аэробной", AEROBIC_HIGH_FOCUS: "Фокус на высокой аэробной", ANAEROBIC_FOCUS: "Фокус на анаэробной" };
const ENDURANCE = ["", "Начальный", "Средний", "Тренированный", "Хорошо тренированный", "Эксперт", "Превосходный", "Элита"];
const fmtHMS = (s) => { if (!s) return "—"; const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), x = Math.round(s % 60);
  return (h ? `${h}:${String(m).padStart(2, "0")}` : `${m}`) + `:${String(x).padStart(2, "0")}`; };

function zonesBar(zones, title, names) {
  const total = (zones || []).reduce((a, b) => a + b, 0);
  if (!total) return "";
  return `<div class="zones"><div class="zl">${title}</div>
    <div class="zbar">${zones.map((z, i) => z ? `<span class="z${i + 1}" style="flex:${z}" title="Зона ${i + 1}: ${fmtDur(z)} (${Math.round((z / total) * 100)}%)"></span>` : "").join("")}</div>
    <div class="zlegend num">${zones.map((z, i) => `<span><i class="z${i + 1}"></i>${names ? names[i] : "Z" + (i + 1)} ${Math.round(z / 60)}′</span>`).join("")}</div></div>`;
}

function hrSpark(curve) {
  if (!curve?.length) return "";
  const vals = curve.map((c) => c[1]), lo = Math.min(...vals) - 5, hi = Math.max(...vals) + 5, W = 600, H = 90;
  const pts = vals.map((v, i) => `${(i / Math.max(1, vals.length - 1)) * W},${H - ((v - lo) / (hi - lo)) * H}`).join(" ");
  return `<div class="zl" style="margin-top:10px">Пульс по минутам · ${curve[0][0]}–${curve[curve.length - 1][0]} · ${lo + 5}–${hi - 5} уд/мин</div>
    <svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="none" style="width:100%;height:70px;display:block">
      <polyline points="${pts}" fill="none" stroke="var(--critical)" stroke-width="2" vector-effect="non-scaling-stroke" stroke-linejoin="round"/></svg>`;
}

const STYLE_COL = { "кроль": "var(--swim)", "брасс": "var(--run)", "на спине": "var(--strength)", "баттерфляй": "var(--hockey)" };
function swimBlock(a) {
  const s = a?.swim; if (!s) return "";
  const maxT = Math.max(...s.lengths.map((l) => l.t || 0), 1);
  const pool = s.pool_used;
  return `<div class="analysis swim-block"><div class="row-between" style="margin-bottom:8px"><b>Плавание: отрезки, гребки, SWOLF</b>
      <span class="pill">бассейн ${pool} м</span></div>
    <div class="grid g4 an-cells" style="margin-top:0">
      <div class="stat"><div class="label">Гребков всего</div><div class="value num" style="font-size:20px">${n0(s.strokes)}</div>
        <div class="delta">${s.spl ? `≈${s.spl} на ${pool} м (ваши)` : `у Garmin ≈${s.avg_strokes ?? "—"} на отрезок`}</div></div>
      <div class="stat"><div class="label">SWOLF на ${pool} м</div><div class="value num" style="font-size:20px">${s.swolf_real ?? "—"}</div>
        <div class="delta">${s.swolf_real ? "время отрезка + гребки" : `у Garmin ${s.swolf ?? "—"} — по его отрезкам`}</div></div>
      <div class="stat"><div class="label">Отрезков по ${pool} м</div><div class="value num" style="font-size:20px">${s.est_lengths ?? s.garmin_lengths}</div>
        <div class="delta">${s.est_lengths ? `у Garmin ${s.garmin_lengths}` : `${s.rest_counted} пауз`}</div></div>
      <div class="stat"><div class="label">Дистанция</div><div class="value num" style="font-size:20px">${n0(s.fixed_distance || s.est_distance || s.garmin_distance)}<small>м</small></div>
        <div class="delta">${s.fixed_distance || s.est_distance ? `у Garmin ${n0(s.garmin_distance)} м` : "по данным Garmin"} · ${Object.entries(s.styles).map(([k, v]) => `${esc(k)} ${v}`).join(", ")}</div></div>
    </div>
    ${s.pool_hint ? `<div class="stale" style="margin-top:12px">${icon("alert")}<span>${esc(s.pool_hint)}</span></div>` : ""}
    <div class="zl" style="margin-top:12px">Отрезки, как их записали часы · высота — время, цвет — стиль${s.spl ? " · ⚠ — вероятная ошибка часов (наведите)" : ""}</div>
    <div class="lengths">${s.lengths.map((l) => `<span class="len ${l.strokes ? "" : "rest"} ${l.flag && l.strokes ? "bad" : ""}"
        style="height:${Math.max(8, (l.t / maxT) * 100)}%;${l.strokes ? `background:${STYLE_COL[l.style_ru] || "var(--other)"}` : ""}"
        title="${l.i}: ${l.t} с${l.strokes ? `, ${l.strokes} гребков, ${l.style_ru}` : ""}${l.flag ? " — " + l.flag : ""}">${l.flag && l.strokes ? "<i>⚠</i>" : ""}</span>`).join("")}</div>
    <div class="legend" style="margin-top:6px">${Object.entries(STYLE_COL).filter(([k]) => s.styles[k]).map(([k, c]) => `<span><i class="sw" style="background:${c}"></i>${k}</span>`).join("")}
      <span><i class="sw" style="background:var(--surface-3)"></i>пауза</span></div>
    <form class="swim-fix athlete-only" onsubmit="event.preventDefault();fixSwim(this,'${esc(a.source)}','${esc(a.source_id)}')">
      <label>Бассейн <select name="pool">${[25, 50].map((v) => `<option value="${v}" ${v == pool ? "selected" : ""}>${v} м</option>`).join("")}</select></label>
      <label>моих гребков на отрезок <input name="spl" type="number" step="0.5" value="${s.spl || ""}" placeholder="напр. 36" style="width:80px"></label>
      <label>или дистанция <input name="dist" type="number" step="25" placeholder="м" value="${s.fix?.distance_m || ""}" style="width:80px"></label>
      <button class="btn primary" type="submit">Пересчитать</button>
      ${s.fix ? `<button class="btn" type="button" onclick="fixSwim(null,'${esc(a.source)}','${esc(a.source_id)}')">Как в Garmin</button>` : ""}
    </form>
    ${s.fixed_distance ? `<div class="muted" style="font-size:12px;margin-top:6px">Темп, рекорды и прогноз считаются по ${n0(s.fixed_distance)} м вместо ${n0(s.garmin_distance)} м.
      Число гребков на отрезок запомнено — на следующих тренировках в этом бассейне пересчёт подскажется сам.</div>` : ""}
  </div>`;
}
async function fixSwim(form, src, id) {
  const body = form ? { pool_m: form.pool.value || null, distance_m: form.dist.value || null, spl: form.spl.value || null } : {};
  if (form && !body.spl && !body.distance_m) return toast("Впишите гребки на отрезок или дистанцию");
  await api(`swim-fix/${encodeURIComponent(src)}/${encodeURIComponent(id)}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  toast(form ? "Дистанция исправлена" : "Вернул данные Garmin"); route();
}

function analysisBlock(an, a) {
  if (an?.manual) {
    return `<div class="analysis"><div class="row-between" style="margin-bottom:6px"><b>Пульс Fitbit</b>
      <span class="pill">${n0(an.hr_samples)} замеров</span></div>
      ${hrSpark(an.hr_curve)}
      ${zonesBar(an.hr_zones, "Время в зонах (от пульса ПАНО)")}
      <div style="margin-top:10px" class="athlete-only"><button class="btn ghost" onclick="event.stopPropagation(); delManual('${esc(a.source_id)}')">Удалить тренировку</button></div></div>`;
  }
  if (an?.fitbit_zones) {
    return `<div class="analysis"><div class="row-between" style="margin-bottom:6px"><b>Fitbit</b>
      ${an.azm != null ? `<span class="pill">Минуты в активных зонах: ${n0(an.azm)}</span>` : ""}</div>
      ${zonesBar(an.fitbit_zones, "Время в пульсовых зонах Fitbit", ["Лёгкая", "Умеренная", "Высокая", "Пиковая"])}</div>`;
  }
  if (!an || an.aerobic_te == null) return "";
  const meter = (label, v, msg) => `<div class="te"><div class="te-head"><span>${label}</span><b class="num">${v.toFixed(1)}</b><span class="muted">${teScale(v)}</span></div>
      <div class="meter"><div style="width:${Math.min(100, (v / 5) * 100)}%"></div></div><div class="te-msg">${esc(teMessage(msg))}</div></div>`;
  const vo2d = an.vo2max && an.vo2max_prev ? an.vo2max - an.vo2max_prev : null;
  const cells = [
    ["Нагрузка", n0(an.training_load), ""],
    an.vo2max ? ["VO2 max", n0(an.vo2max), vo2d != null ? `${vo2d > 0 ? "▲ +" : vo2d < 0 ? "▼ " : "= "}${vo2d || ""} к прошлой` : ""] : null,
    an.body_battery_diff != null ? ["Body Battery", `${an.body_battery_diff > 0 ? "+" : ""}${an.body_battery_diff}`, ""] : null,
    an.vigorous_min != null ? ["Интенсивные мин.", `${n0(an.moderate_min)} + ${n0(an.vigorous_min)}`, "умерен. + высокие"] : null,
  ].filter(Boolean);
  return `<div class="analysis"><div class="row-between" style="margin-bottom:6px"><b>Анализ Garmin</b>
      ${TE_LABEL[an.te_label] ? `<span class="pill">Фокус: ${TE_LABEL[an.te_label]}</span>` : ""}</div>
    <div class="grid g2" style="gap:10px">${meter("Аэробный эффект", an.aerobic_te, an.aerobic_msg)}${meter("Анаэробный эффект", an.anaerobic_te || 0, an.anaerobic_msg)}</div>
    <div class="grid g4 an-cells">${cells.map(([l, v, d]) => `<div class="stat"><div class="label">${l}</div><div class="value num" style="font-size:20px">${v}</div>${d ? `<div class="delta">${d}</div>` : ""}</div>`).join("")}</div>
    ${zonesBar(an.hr_zones, "Время в пульсовых зонах")}${zonesBar(an.power_zones, "Время в зонах мощности")}
  </div>`;
}

const fmtMin = (m) => { const t = (18 * 60 + m + 1440) % 1440; return `${String(Math.floor(t / 60)).padStart(2, "0")}:${String(t % 60).padStart(2, "0")}`; };
const fmtLate = (m) => (m >= 60 ? `${Math.floor(m / 60)} ч ${m % 60} мин` : `${m} мин`);

function regimeCard(r) {
  if (!r || !r.nights.length) return "";
  const last = r.last, nights = r.nights.slice(-14);
  return `<div class="card">
    <div class="card-h"><h3>${icon("moon")}Режим</h3><span class="meta">отбой до ${r.target} МСК</span></div>
    <div class="grid g3" style="gap:10px">
      <div class="stat"><div class="label">Лёг · ${fmtShort(last.night_of)}</div><div class="value num">${last.bed_time}</div>
        <div class="delta" style="color:var(${last.on_time ? "--good-ink" : "--critical"})">${last.on_time ? "✓ вовремя" : "✗ позже на " + fmtLate(last.late_min)}</div></div>
      <div class="stat"><div class="label">Вовремя</div><div class="value num">${r.on_time_14}<small>из ${r.count_14}</small></div>
        <div class="delta">${r.streak ? `серия ${r.streak} ноч.` : "серии пока нет"}</div></div>
      <div class="stat"><div class="label">В среднем</div><div class="value num">${r.avg_bed_14}</div>
        <div class="delta">${r.avg_late_14 ? "в среднем +" + fmtLate(r.avg_late_14) : "в цели"}</div></div>
    </div>
    <div class="nights" title="Последние 14 ночей">${nights.map((n) => `<span class="night ${n.on_time ? "ok" : n.late_min <= 30 ? "near" : "late"}"
        title="${fmtShort(n.night_of)}: лёг ${n.bed_time}, встал ${n.wake_time}, сон ${n.sleep_h} ч"><i></i>${parseD(n.night_of).getDate()}</span>`).join("")}</div>
  </div>`;
}

function trainingCard(gs) {
  if (!gs) return "";
  const vo2d = gs.vo2max && gs.vo2max_week_ago ? (gs.vo2max - gs.vo2max_week_ago).toFixed(1) : null;
  const nextLim = [0, 5100, 5800, 6600, 7300, 8100, 8800, null][gs.endurance_class];
  const bal = gs.balance ? [["AerobicLow", "Низкая аэробная"], ["AerobicHigh", "Высокая аэробная"], ["Anaerobic", "Анаэробная"]].map(([k, l]) => {
    const [v, lo, hi] = gs.balance[k]; const max = Math.max(hi || 0, v || 0) * 1.15 || 1;
    const ok = v >= lo && v <= hi;
    return `<div class="bal"><div class="bal-h"><span>${l}</span><span class="num">${n0(v)} <span class="muted">/ ${n0(lo)}–${n0(hi)}</span></span></div>
      <div class="brange"><div class="band" style="left:${(lo / max) * 100}%;width:${((hi - lo) / max) * 100}%"></div>
      <div class="val ${ok ? "ok" : ""}" style="width:${Math.max(1, (v / max) * 100)}%"></div></div></div>`;
  }).join("") : "";
  const r = gs.race || {};
  return `<div class="card-h"><h3>${icon("gauge")}Тренированность · Garmin</h3><span class="meta">${fmtShort(gs.date)}</span></div>
    <div class="training-grid">
      <div class="mini-stats">
        <div class="stat"><div class="label">VO2 max</div><div class="value num">${gs.vo2max ?? "—"}</div><div class="delta ${vo2d > 0 ? "up" : ""}">${vo2d != null ? `${vo2d > 0 ? "+" : ""}${vo2d} за неделю` : ""}</div></div>
        <div class="stat"><div class="label">Endurance Score</div><div class="value num">${n0(gs.endurance_score)}</div>
          <div class="delta">${ENDURANCE[gs.endurance_class] || ""}${nextLim ? ` · ещё ${n0(nextLim - gs.endurance_score)}` : ""}</div></div>
        <div class="stat"><div class="label">Статус</div><div class="value" style="font-size:15px;line-height:1.3">${STATUS_PHRASE[(gs.status_phrase || "").replace(/_\d+$/, "")] || "—"}</div></div>
        <div class="stat"><div class="label">Нагрузка остр./хрон.</div><div class="value num">${n0(gs.acute_load)}<small>/ ${n0(gs.chronic_load)}</small></div>
          <div class="delta">${gs.acwr != null ? `${gs.acwr} — ${ACWR[gs.acwr_status] || ""}` : ""}</div></div>
      </div>
      <div>${bal ? `<div class="src-tag">Баланс за 4 недели</div>${bal}<div class="muted" style="font-size:12px">${BALANCE_PHRASE[gs.balance_phrase] || ""}</div>` : ""}</div>
      <div>${gs.race ? `<div class="src-tag">Прогноз забегов</div><div class="race-list">${[["5 км", r.time5K], ["10 км", r.time10K], ["Полумарафон", r.timeHalfMarathon], ["Марафон", r.timeMarathon]].map(([l, t]) =>
        `<div class="stat"><div class="label">${l}</div><div class="value num" style="font-size:18px">${fmtHMS(t)}</div></div>`).join("")}</div>` : ""}
        ${gs.heat_acclimation != null ? `<div class="muted" style="font-size:12px;margin-top:12px">Акклиматизация к жаре: ${gs.heat_acclimation}%</div>` : ""}</div>
    </div>`;
}

const $ = (s, el = document) => el.querySelector(s);
const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const api = async (path, opts) => {
  const r = await fetch("/api/" + path, opts);
  if (r.status === 401) { location.replace("/login"); throw new Error("Нужно войти"); }
  if (!r.ok) { const t = await r.text(); let m = t; try { m = JSON.parse(t).detail || t; } catch {} throw new Error(m); }
  return r.json();
};

// ---------- форматирование ----------
const parseD = (s) => new Date(s + "T00:00:00");
const iso = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
const addDays = (d, n) => { const x = new Date(d); x.setDate(x.getDate() + n); return x; };
const mondayOf = (d) => addDays(d, -((d.getDay() + 6) % 7));
const fmtDay = (s) => { const d = parseD(s); return `${DOW[(d.getDay() + 6) % 7]}, ${d.getDate()} ${MONTHS[d.getMonth()]}`; };
const fmtShort = (s) => { const d = parseD(s); return `${d.getDate()} ${MONTHS[d.getMonth()]}`; };
const fmtDur = (s) => {
  if (!s) return "—";
  const m = Math.round(s / 60);
  return m >= 60 ? `${Math.floor(m / 60)}:${String(m % 60).padStart(2, "0")}` : `${m} мин`;
};
const fmtDist = (m, sport) => {
  if (!m) return "—";
  return sport === "swim" ? `${Math.round(m)} м` : `${(m / 1000).toFixed(1)} км`;
};
const fmtPace = (a) => {
  if (!a?.distance_m || !a?.duration_s) return "—";
  if (a.sport === "run") { const p = a.duration_s / (a.distance_m / 1000); return `${Math.floor(p / 60)}:${String(Math.round(p % 60)).padStart(2, "0")} /км`; }
  if (a.sport === "swim") { const p = a.duration_s / (a.distance_m / 100); return `${Math.floor(p / 60)}:${String(Math.round(p % 60)).padStart(2, "0")} /100м`; }
  if (a.sport === "bike") return `${(a.distance_m / a.duration_s * 3.6).toFixed(1)} км/ч`;
  return "—";
};
const n0 = (v) => (v == null ? "—" : Math.round(v).toLocaleString("ru-RU"));
const hrs = (s) => (s ? (s / 3600).toFixed(1) : "—");

function toast(msg, ms = 3500) {
  const t = $("#tooltip");
  t.textContent = msg; t.hidden = false;
  clearTimeout(toast._t); toast._t = setTimeout(() => (t.hidden = true), ms);
}

// ---------- компоненты ----------
function statusPill(row) {
  const label = STATUS[row.status] + (row.compliance != null && row.status !== "missed" ? ` · ${row.compliance}%` : "");
  return `<span class="pill"><span class="dot ${row.status}"></span>${label}</span>`;
}

function workoutRow(row) {
  const p = row.planned, a = row.actual, sp = SPORT[row.sport] || SPORT.other;
  const title = p?.title || a?.title || sp.name;
  const meta = [];
  const approx = (x, k) => (x?.[k + "_estimated"] ? "≈" : "");
  if (p && row.sport !== "rest") meta.push(p.distance_m
    ? `план ${fmtDist(p.distance_m, row.sport)} (${approx(p, "duration")}${fmtDur(p.duration_s)})`
    : `план ${fmtDur(p.duration_s)}${p.tss ? ` · ${Math.round(p.tss)} TSS` : ""}`);
  if (a) meta.push(`факт ${a.distance_m ? fmtDist(a.distance_m, row.sport) + " · " : ""}${fmtDur(a.duration_s)}${a.tss ? ` · ${Math.round(a.tss)} TSS` : ""}`);
  if (row.moved_to) meta.push(`выполнено ${fmtShort(row.moved_to)}`);
  if (a?.swim) meta.push(`${n0(a.swim.strokes)} гребков${a.swim.swolf_real ? ` · SWOLF ${a.swim.swolf_real}` : ""}${a.swim.pool_hint ? " · ⚠ проверьте отрезки" : ""}`);
  if (a?.analysis?.aerobic_te != null) meta.push(`TE ${a.analysis.aerobic_te.toFixed(1)}${TE_LABEL[a.analysis.te_label] ? " · " + TE_LABEL[a.analysis.te_label] : ""}`);
  const lines = [
    ["Длительность", (p?.duration_estimated ? "≈" : "") + fmtDur(p?.duration_s), fmtDur(a?.duration_s)],
    ["Дистанция", fmtDist(p?.distance_m, row.sport), fmtDist(a?.distance_m, row.sport)],
    ["TSS", (p?.tss_estimated && p?.tss ? "≈" : "") + n0(p?.tss), a?.tss != null ? n0(a.tss) + (a.tss_estimated ? "*" : "") : "—"],
  ];
  if (a) {
    lines.push(["Темп / скорость", "", fmtPace(a)]);
    if (a.avg_hr) lines.push([`Пульс ср. / макс.${a.hr_source === "fitbit" ? " · Fitbit" : ""}`, "", `${n0(a.avg_hr)} / ${n0(a.max_hr)}`]);
    if (a.garmin_avg_hr) lines.push(["Пульс · Garmin", "", `${n0(a.garmin_avg_hr)} / ${n0(a.garmin_max_hr)}`]);
    if (a.avg_power) lines.push(["Мощность ср. / NP", "", `${n0(a.avg_power)} / ${n0(a.np)} Вт`]);
    if (a.elevation_m) lines.push(["Набор высоты", "", `${n0(a.elevation_m)} м`]);
    if (a.calories) lines.push(["Калории", "", n0(a.calories)]);
  }
  const details = row.sport === "rest" ? "" : `
    <div class="details">
      ${p?.description ? `<div class="muted" style="white-space:pre-line">${esc(p.description)}</div>` : ""}
      ${p?.coach_comments ? `<div class="coach"><b>Тренер:</b> ${esc(p.coach_comments)}</div>` : ""}
      ${a?.athlete_comments ? `<div class="coach"><b>Мой комментарий:</b> ${esc(a.athlete_comments)}</div>` : ""}
      ${a?.has_gps && a.source === "garmin" ? `<div class="map map-mini" data-track="${esc(a.source)}|${esc(a.source_id)}" data-sport="${row.sport}"></div>${zoneLegend()}` : ""}
      ${swimBlock(a)}
      ${analysisBlock(a?.analysis, a)}
      <table class="pf num"><thead><tr><th></th><th>План</th><th>Факт</th></tr></thead>
        <tbody>${lines.map((l) => `<tr><td>${l[0]}</td><td>${l[1]}</td><td>${l[2]}</td></tr>`).join("")}</tbody></table>
      ${a?.tss_estimated ? `<div class="muted" style="font-size:12px;margin-top:6px">* TSS оценён по пульсу/темпу</div>` : ""}
      ${p?.duration_estimated ? `<div class="muted" style="font-size:12px;margin-top:4px">≈ время плана оценено по дистанции в спокойном темпе</div>` : ""}
      ${a ? `<div class="muted" style="font-size:12px;margin-top:4px">Источник: ${esc(a.source)}</div>` : ""}
      ${a ? `<label class="excl athlete-only"><input type="checkbox" ${a.excluded ? "checked" : ""}
        onchange="toggleExclude('${esc(a.source)}','${esc(a.source_id)}',this.checked)"> Не учитывать в статистике (сбойная запись: неверная длина бассейна, GPS)</label>` : ""}
      <div class="thread" data-key="${esc(commentKey(row))}" data-date="${row.date}"></div>
    </div>`;
  return `<div class="workout" ${row._k != null ? `id="w-${row._k}"` : ""} style="--c:${sportColor(row.sport)}" onclick="if(!event.target.closest('.details')){this.classList.toggle('open');openMaps(this)}">
      <div class="bar" style="background:${sportColor(row.sport)}"></div>
      <div><div class="t">${sp.ico}${esc(title)}</div><div class="meta num">${meta.join(" &nbsp;·&nbsp; ") || sp.name}</div></div>
      <div class="wo-right">${(_comments[row.planned || row.actual ? commentKey(row) : ""] || []).length ? `<span class="pill cmt-pill">${icon("chat")}${_comments[commentKey(row)].length}</span>` : ""}${statusPill(row)}</div>
      ${details}
    </div>`;
}

// ---------- комментарии к тренировкам ----------
const commentKey = (row) => row.planned ? `p:${row.planned.source}:${row.planned.source_id}` : `a:${row.actual.source}:${row.actual.source_id}`;
let _me = null, _comments = {};
async function loadComments(start, end) {
  const list = await api(`comments?start=${start}&end=${end}`);
  _comments = {};
  list.forEach((c) => (_comments[c.key] ||= []).push(c));
  return list;
}
const commentHtml = (c) => `<div class="cmt ${c.role}"><div class="cmt-h"><b>${esc(c.author_name)}</b><span class="muted">${c.role === "coach" ? "тренер" : "спортсмен"} · ${esc(`${c.created.slice(8, 10)}.${c.created.slice(5, 7)} в ${c.created.slice(11, 16)}`)}</span>
  ${_me && c.author === _me.login ? `<button class="cmt-del" onclick="event.stopPropagation();delComment(${c.id})" title="Удалить">×</button>` : ""}</div><div>${esc(c.text)}</div></div>`;
function renderThread(el) {
  const list = _comments[el.dataset.key] || [];
  el.innerHTML = `<div class="src-tag" style="margin-top:14px">Комментарии${list.length ? ` · ${list.length}` : ""}</div>
    ${list.map(commentHtml).join("")}
    <form class="cmt-form" onsubmit="event.preventDefault();sendComment(this)"><input name="t" placeholder="${_me?.role === "coach" ? "Комментарий спортсмену…" : "Комментарий тренеру…"}" autocomplete="off">
      <button class="btn primary" type="submit">Отправить</button></form>`;
}
async function sendComment(form) {
  const th = form.closest(".thread"), text = form.t.value.trim(); if (!text) return;
  const c = await api("comments", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ key: th.dataset.key, date: th.dataset.date, text }) });
  (_comments[c.key] ||= []).push(c); renderThread(th); th.querySelector("input").focus();
}
async function delComment(id) {
  await api(`comments/${id}`, { method: "DELETE" });
  for (const k in _comments) _comments[k] = _comments[k].filter((c) => c.id !== id);
  document.querySelectorAll(".thread").forEach(renderThread);
}
async function toggleExclude(src, id, on) {
  await api(`exclude/${encodeURIComponent(src)}/${encodeURIComponent(id)}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ excluded: on }) });
  toast(on ? "Тренировка не учитывается в темпе, рекордах и прогнозе" : "Тренировка снова учитывается");
}

function openMaps(root) {
  root.querySelectorAll(".thread:not(.ready)").forEach((el) => { el.classList.add("ready"); renderThread(el); });
  root.querySelectorAll(".map-mini[data-track]:not(.ready)").forEach((el) => {
    el.classList.add("ready");
    const [src, id] = el.dataset.track.split("|");
    miniMap(el, src, id, css("--" + el.dataset.sport) || css("--accent"));
  });
}

// ---------- две линии: План сверху, Факт снизу, стрелки — сопоставления ----------
function chip(row, side) {
  const sp = SPORT[row.sport] || SPORT.other, w = row[side];
  const title = (side === "planned" ? w.title : w.title) || sp.name;
  const size = w.distance_m ? fmtDist(w.distance_m, row.sport) : row.sport === "rest" ? "" : (w.duration_estimated ? "≈" : "") + fmtDur(w.duration_s);
  const st = side === "planned" ? row.status : row.planned ? row.status : "unplanned";
  const badge = side === "planned" && row.compliance != null && row.status !== "missed" ? `<span class="cp num">${row.compliance}%</span>` : "";
  return `<button class="chip s-${st} ${row.sport === "rest" ? "rest" : ""}" data-k="${row._k}" data-side="${side}"
      style="--c:${sportColor(row.sport)}"
      title="${esc(title)} · ${STATUS[st]}${row.moved_to && side === "planned" ? " · выполнено " + fmtShort(row.moved_to) : ""}">
    <span class="ci">${sp.ico}</span><span class="ct">${esc(title)}</span><span class="cs num">${size}${badge}</span></button>`;
}

function weekLanes(days) {
  const today = iso(new Date());
  const cells = (side, pick) => days.map((d) => `<div class="lane-cell ${d.date === today ? "is-today" : ""}">${
    days.flatMap((x) => x.items).filter((i) => i[side] && pick(i) === d.date).map((i) => chip(i, side)).join("")}</div>`).join("");
  return `<div class="lanes">
    <div class="lane-grid">
      <div></div>${days.map((d) => { const dt = parseD(d.date);
        return `<div class="lane-head ${d.date === today ? "is-today" : ""}"><span>${DOW[(dt.getDay() + 6) % 7]}</span> <b>${dt.getDate()}</b></div>`; }).join("")}
      <div class="lane-label">План</div>${cells("planned", (i) => i.planned.date)}
      <div class="lane-gap"></div>${days.map(() => `<div class="lane-gap"></div>`).join("")}
      <div class="lane-label">Факт</div>${cells("actual", (i) => i.actual.date)}
    </div>
    <svg class="lane-arrows" aria-hidden="true"></svg>
  </div>`;
}

const ARROW_COLOR = { done: "--good", partial: "--warning", off: "--serious" };
function drawArrows() {
  document.querySelectorAll(".lanes").forEach((root) => {
    const svg = root.querySelector(".lane-arrows"), box = root.getBoundingClientRect();
    svg.setAttribute("width", box.width); svg.setAttribute("height", box.height);
    svg.setAttribute("viewBox", `0 0 ${box.width} ${box.height}`);
    let out = `<defs>${Object.entries(ARROW_COLOR).map(([k, v]) => `<marker id="ah-${k}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(${v})"/></marker>`).join("")}</defs>`;
    root.querySelectorAll('.chip[data-side="planned"]').forEach((pc) => {
      const fc = root.querySelector(`.chip[data-side="actual"][data-k="${pc.dataset.k}"]`);
      if (!fc) return;
      const a = pc.getBoundingClientRect(), b = fc.getBoundingClientRect();
      const st = [...pc.classList].find((c) => c.startsWith("s-"))?.slice(2) || "done";
      const x1 = a.left + a.width / 2 - box.left, y1 = a.bottom - box.top + 1;
      const x2 = b.left + b.width / 2 - box.left, y2 = b.top - box.top - 2;
      const dy = Math.max(14, (y2 - y1) / 2);
      out += `<path d="M${x1},${y1} C${x1},${y1 + dy} ${x2},${y2 - dy} ${x2},${y2}" fill="none" stroke="var(${ARROW_COLOR[st] || "--good"})"
        stroke-width="2" ${x1 !== x2 ? 'stroke-dasharray="5 3"' : ""} marker-end="url(#ah-${st in ARROW_COLOR ? st : "done"})"/>`;
    });
    svg.innerHTML = out;
  });
}
window.addEventListener("resize", () => requestAnimationFrame(drawArrows));
document.addEventListener("click", (e) => {
  const c = e.target.closest(".chip");
  if (!c) return;
  const row = document.getElementById("w-" + c.dataset.k);
  if (row) { row.classList.add("open"); openMaps(row); row.scrollIntoView({ behavior: "smooth", block: "center" }); }
  else if (location.hash !== "#calendar") location.hash = "#calendar";
});
const keyRows = (days) => { let k = 0; days.forEach((d) => d.items.forEach((i) => (i._k = k++))); return days; };
const lanesLegend = () => `<div class="legend" style="margin-top:8px">
  <span><svg width="22" height="10"><line x1="0" y1="5" x2="22" y2="5" stroke="var(--good)" stroke-width="2"/></svg>в тот же день</span>
  <span><svg width="22" height="10"><line x1="0" y1="5" x2="22" y2="5" stroke="var(--good)" stroke-width="2" stroke-dasharray="5 3"/></svg>перенесено</span>
  ${["done", "partial", "off", "missed", "unplanned"].map((s) => `<span><span class="dot ${s}" style="width:8px;height:8px;border-radius:50%;display:inline-block"></span>${STATUS[s]}</span>`).join("")}
</div>`;

function stat(label, value, unit = "", delta = "", deltaCls = "") {
  return `<div class="card stat"><div class="label">${label}</div>
    <div class="value num">${value}${unit ? `<small>${unit}</small>` : ""}</div>
    ${delta ? `<div class="delta ${deltaCls}">${delta}</div>` : ""}</div>`;
}

// ---------- Сегодня ----------
// Вердикт дня: сводим сон, режим, HRV, пульс покоя и свежесть в одну рекомендацию
function readiness(o) {
  const rec = o.recovery_source ? o.health[o.recovery_source] : null, f = o.form, r = o.regime?.last;
  const fx = [];
  if (rec?.sleep_s) { const h = rec.sleep_s / 3600; fx.push({ k: h < 6 ? "bad" : h < 7 ? "warn" : "good", label: "Сон", val: `${h.toFixed(1)} ч` }); }
  if (r) fx.push({ k: r.on_time ? "good" : r.late_min > 90 ? "bad" : "warn", label: "Отбой", val: r.bed_time });
  if (rec?.hrv && rec?.hrv_baseline) { const d = Math.round((rec.hrv / rec.hrv_baseline - 1) * 100);
    fx.push({ k: d < -15 ? "bad" : d < -5 ? "warn" : "good", label: "HRV", val: `${d >= 0 ? "+" : ""}${d}%` }); }
  if (rec?.resting_hr && rec?.rhr_baseline) { const d = Math.round(rec.resting_hr - rec.rhr_baseline);
    fx.push({ k: d > 5 ? "bad" : d > 2 ? "warn" : "good", label: "Пульс покоя", val: `${d >= 0 ? "+" : ""}${d}` }); }
  if (f) fx.push({ k: f.tsb < -30 ? "bad" : f.tsb < -20 ? "warn" : "good", label: "Свежесть", val: Math.round(f.tsb) });
  const bad = fx.filter((x) => x.k === "bad").length, warn = fx.filter((x) => x.k === "warn").length;
  const level = bad >= 2 ? "bad" : bad || warn >= 2 ? "warn" : "good";
  const verdict = { good: "Готов к нагрузке — работай по плану",
    warn: "Восстановление неполное — держи интенсивность пониже",
    bad: "Организм не восстановился — лучше облегчить день и обсудить с тренером" }[level];
  return { level, verdict, fx };
}

// ---------- восстановление и нагрузка (как WHOOP) ----------
const REC_COL = { green: "var(--good)", yellow: "var(--warning)", red: "var(--critical)" };
function ring(value, max, color, label, sub, band) {
  const R = 46, C = 2 * Math.PI * R, frac = Math.max(0, Math.min(1, (value ?? 0) / max));
  const arc = (a0, a1, col, w) => `<circle cx="60" cy="60" r="${R}" fill="none" stroke="${col}" stroke-width="${w}" stroke-linecap="round"
    stroke-dasharray="${Math.max(0.01, (a1 - a0) * C)} ${C}" stroke-dashoffset="${-a0 * C}" transform="rotate(-90 60 60)"/>`;
  return `<div class="ring-box"><svg viewBox="0 0 120 120" class="ring">
    <circle cx="60" cy="60" r="${R}" fill="none" stroke="var(--surface-2)" stroke-width="10"/>
    ${band ? arc(band[0] / max, band[1] / max, "color-mix(in srgb, var(--good) 30%, transparent)", 10) : ""}
    ${value != null ? arc(0, frac, color, 10) : ""}
    <text x="60" y="58" text-anchor="middle" class="ring-val">${value ?? "—"}</text>
    <text x="60" y="78" text-anchor="middle" class="ring-sub">${sub}</text></svg><div class="ring-label">${label}</div></div>`;
}
function readinessCard(r) {
  const rec = r.recovery, z = rec.zone;
  const zoneText = { green: "Зелёная зона — организм готов к нагрузке", yellow: "Жёлтая зона — работайте, но без лишней интенсивности", red: "Красная зона — день для восстановления" }[z] || "Копим вашу норму — оценка появится через несколько дней";
  const left = r.remaining > 0.3 ? `Осталось ≈ <b>${r.remaining}</b> до оптимума: ${r.remaining_z2_min > 180 ? "больше 3 ч" : `≈ ${r.remaining_z2_min} мин`} в Z2 (пульс ~${r.z2_hr})
      или ≈ ${r.remaining_z4_min} мин в Z4 (~${r.z4_hr})` : r.strain > r.target[1] ? `Нагрузка выше оптимума — на сегодня хватит, лучше растяжка и сон` : `Оптимальная нагрузка набрана — можно заканчивать`;
  const fx = [
    rec.hrv != null && { k: rec.hrv_z == null ? "" : rec.hrv_z < -1 ? "bad" : rec.hrv_z < -0.3 ? "warn" : "good", t: `HRV <b>${n0(rec.hrv)}</b> · норма ${rec.hrv_base ?? "—"}` },
    rec.rhr != null && { k: rec.rhr_z == null ? "" : rec.rhr_z > 1 ? "bad" : rec.rhr_z > 0.3 ? "warn" : "good", t: `Пульс покоя <b>${n0(rec.rhr)}</b> · норма ${rec.rhr_base ?? "—"}` },
    rec.sleep_h != null && { k: rec.sleep_perf < 75 ? "bad" : rec.sleep_perf < 90 ? "warn" : "good", t: `Сон <b>${rec.sleep_h} ч</b> из ${rec.sleep_need} нужных` },
    rec.sleep_gap_min >= 20 && { k: rec.sleep_gap_min >= 60 ? "warn" : "", t: `Сон прерывался на <b>${fmtLate(rec.sleep_gap_min)}</b>` },
    rec.nap_min && { k: "good", t: `Дневной сон <b>${rec.nap_min} мин</b>` },
    rec.bed_time && { k: rec.late_min > 90 ? "bad" : rec.late_min > 0 ? "warn" : "good", t: `Отбой <b>${rec.bed_time}</b>` },
    rec.yesterday_strain != null && { k: "", t: `Вчера нагрузка <b>${rec.yesterday_strain}</b>` },
  ].filter(Boolean);
  return `<div class="card whoop">
    <div class="whoop-rings">
      ${ring(rec.score, 100, REC_COL[z] || "var(--axis)", "Восстановление", rec.score != null ? "%" : "нет данных")}
      ${ring(r.strain, 21, "var(--accent)", "Нагрузка дня", `цель ${r.target[0]}–${r.target[1]}`, r.target)}
    </div>
    <div class="whoop-text">
      <div class="verdict">${zoneText}</div>
      <div class="whoop-left">${left}</div>
      ${r.planned.length ? `<div class="whoop-plan ${r.over_plan ? "t-bad" : ""}">${icon("calendar")}По плану: ${r.planned.map((p) => esc(p.title || SPORT[p.sport]?.name)).join(", ")} —
        нагрузка ≈ <b>${r.planned_strain}</b>${r.over_plan ? ` · выше оптимума ${r.target[1]}, стоит обсудить облегчение с тренером` : " · укладывается в оптимум"}</div>` : ""}
      <div class="factors">${fx.map((x) => `<span class="factor ${x.k}"><i></i>${x.t}</span>`).join("")}</div>
      ${r.hr_stale_min > 60 ? `<div class="stale">${icon("alert")}<span>Пульс есть только до <b>${r.hr_updated || "начала дня"}</b> — браслет и часы с тех пор не синхронизировались.
        Откройте приложение Fitbit (или Garmin Connect) на телефоне — нагрузка дня сейчас неполная.</span></div>` : ""}
      <div class="muted" style="font-size:11.5px;margin-top:6px">Пульс до ${r.hr_updated || "—"} · норма по ${rec.baseline_days} ночам${rec.baseline_days < 14 ? " (оценка грубая, пока меньше 2 недель)" : ""}</div>
    </div></div>`;
}

function sparkline(vals, color) {
  const v = vals.filter((x) => x != null);
  if (v.length < 2) return "";
  const lo = Math.min(...v), hi = Math.max(...v), W = 120, H = 36, span = hi - lo || 1;
  const pts = vals.map((x, i) => `${(i / (vals.length - 1)) * W},${H - 3 - ((x - lo) / span) * (H - 6)}`).join(" ");
  return `<svg class="spark" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none"><polyline points="${pts}" fill="none" stroke="${color}" stroke-width="2" vector-effect="non-scaling-stroke" stroke-linejoin="round" stroke-linecap="round"/></svg>`;
}

function todayWorkout(i) {
  const p = i.planned, a = i.actual, sp = SPORT[i.sport] || SPORT.other;
  const facts = [];
  if (p?.distance_m) facts.push(`<span><b>${fmtDist(p.distance_m, i.sport)}</b></span>`);
  if (p?.duration_s) facts.push(`<span>${p.duration_estimated ? "≈" : ""}<b>${fmtDur(p.duration_s)}</b></span>`);
  if (p?.tss) facts.push(`<span>${p.tss_estimated ? "≈" : ""}<b>${Math.round(p.tss)}</b> TSS</span>`);
  if (a) facts.push(`<span>факт <b>${a.distance_m ? fmtDist(a.distance_m, i.sport) + " · " : ""}${fmtDur(a.duration_s)}</b></span>`);
  return `<div class="wo-today" style="--c:${sportColor(i.sport)}">
    <div class="sport-badge">${icon(i.sport)}</div>
    <div><div class="t">${esc(p?.title || a?.title || sp.name)}</div><div class="facts num">${facts.join("") || sp.name}</div></div>
    <div class="pill-wrap">${statusPill(i)}</div>
    ${p?.description ? `<div class="desc ${p.description.split("\n").length > 7 || p.description.length > 420 ? "clamp" : ""}">${esc(p.description)}
      <button class="more" onclick="this.parentElement.classList.toggle('expanded')"></button></div>` : ""}
    ${p?.coach_comments ? `<div class="desc"><b>Тренер:</b> ${esc(p.coach_comments)}</div>` : ""}
  </div>`;
}

async function renderToday() {
  const [o, fit, rc, rdy] = await Promise.all([api("overview"), api("fitness?days=42&forward=0"), api("comments?recent=5"), api("readiness").catch(() => null)]);
  const el = $("#view-today");
  const f = o.form, fw = o.form_week_ago, ws = o.week_stats;
  const d0 = parseD(o.today);
  const weekNo = Math.ceil(((d0 - new Date(d0.getFullYear(), 0, 1)) / 864e5 + new Date(d0.getFullYear(), 0, 1).getDay() + 1) / 7);
  const rd = readiness(o);
  const tsbHint = !f ? "" : f.tsb > 5 ? "свежесть, можно нагружать" : f.tsb > -10 ? "оптимальная нагрузка" : f.tsb > -30 ? "продуктивная усталость" : "перегрузка";
  const tsbCls = !f ? "" : f.tsb < -30 ? "t-bad" : f.tsb < -20 ? "t-warn" : "";
  const rs = o.recovery_source, rec = rs ? o.health[rs] : null, g = o.health.garmin;
  const hv = rec?.hrv && rec?.hrv_baseline ? Math.round((rec.hrv / rec.hrv_baseline - 1) * 100) : null;
  const reg = o.regime, last = reg?.last;
  const progress = Math.max(0, Math.min(100, (1 - o.race.days_left / 730) * 100));
  const sigIcon = (t) => (/Пропущено|Режим|сна/.test(t) ? "warn" : /HRV|Пульс|усталость/.test(t) ? "bad" : "warn");
  const weekPct = ws.plan_hours ? Math.min(100, (ws.actual_hours / ws.plan_hours) * 100) : 0;

  el.innerHTML = `
    <div class="page-head">
      <div><h1>${["Воскресенье", "Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"][d0.getDay()]}, ${d0.getDate()} ${MONTHS[d0.getMonth()]}</h1>
        <div class="sub">${weekNo}-я неделя года · подготовка к ${esc(o.race.name)}</div></div>
      <div class="race-pill">${icon("flag")}<div><div class="muted" style="font-size:12px">до старта · ${fmtShort(o.race.date)} ${o.race.date.slice(0, 4)}</div>
        <b class="num">${o.race.days_left} дн.</b> <span class="muted">${Math.floor(o.race.days_left / 7)} нед.</span></div>
        <div class="progress" title="Пройдено ${progress.toFixed(1)}% пути"><div style="width:${Math.max(progress, 1.5)}%"></div></div></div>
    </div>

    ${rdy && rdy.recovery ? readinessCard(rdy) : `<div class="card ready ${rd.level}">
      <div class="ring">${icon(rd.level === "good" ? "check" : "alert")}</div>
      <div class="verdict">${rd.verdict}</div>
      <div class="factors">${rd.fx.map((x) => `<span class="factor ${x.k}"><i></i>${x.label} <b class="num">${x.val}</b></span>`).join("")}</div>
    </div>`}

    <div class="kpis">
      <div class="card kpi"><div class="stat"><div class="label">Фитнес · CTL</div><div class="value num">${f ? Math.round(f.ctl) : "—"}</div>
        <div class="delta ${f && fw && f.ctl >= fw.ctl ? "up" : ""}">${f && fw ? `${f.ctl - fw.ctl >= 0 ? "+" : ""}${(f.ctl - fw.ctl).toFixed(1)} за неделю` : ""}</div></div>
        ${sparkline(fit.map((d) => d.ctl), css("--s1"))}</div>
      <div class="card kpi"><div class="stat"><div class="label">Свежесть · TSB</div><div class="value num ${tsbCls}">${f ? Math.round(f.tsb) : "—"}</div>
        <div class="delta">${tsbHint} · ATL ${f ? Math.round(f.atl) : "—"}</div></div>
        ${sparkline(fit.map((d) => d.tsb), css("--s2"))}</div>
      <div class="card kpi"><div class="stat"><div class="label">Неделя · выполнено</div><div class="value num">${ws.done}<small>из ${ws.planned}</small></div>
        <div class="delta num">${ws.actual_hours} из ${ws.plan_hours} ч · ${ws.actual_tss} из ${ws.plan_tss} TSS</div></div>
        <div class="progress bar-mini"><div style="width:${weekPct}%"></div></div></div>
      <div class="card kpi"><div class="stat"><div class="label">Сон · ночь на ${rec ? fmtShort(rec.date) : "—"}</div>
        <div class="value num">${rec ? hrs(rec.sleep_s) : "—"}<small>ч</small></div>
        <div class="delta ${last && !last.on_time ? "t-bad" : "t-good"}">${last ? `отбой ${last.bed_time}${last.on_time ? " ✓" : ` · +${fmtLate(last.late_min)}`}` : ""}</div></div>
        ${reg ? sparkline(reg.nights.slice(-14).map((n) => -n.bed_min), css("--muted")) : ""}</div>
    </div>

    <div class="today-grid">
      <div class="card"><div class="card-h"><h3>${icon("target")}Тренировка на сегодня</h3><span class="meta">из TrainingPeaks</span></div>
        ${o.today_items.length ? o.today_items.map(todayWorkout).join("") : `<div class="empty">Тренер ничего не поставил — день отдыха</div>`}</div>
      <div class="stack">
        <div class="card"><div class="card-h"><h3>${icon("alert")}Сигналы</h3><span class="meta">${o.alerts.length || "нет"}</span></div>
          ${o.alerts.length ? `<div class="signals">${o.alerts.map((a) => `<div class="signal ${sigIcon(a)}">${icon("alert")}<span>${esc(a)}</span></div>`).join("")}</div>`
            : `<div class="signal good">${icon("check")}<span>Всё в порядке</span></div>`}</div>
        ${regimeCard(reg)}
        ${rc.length ? `<div class="card"><div class="card-h"><h3>${icon("chat")}Комментарии</h3><a class="meta" href="#calendar">к тренировкам →</a></div>
          ${rc.map((c) => `<div class="cmt ${c.role}"><div class="cmt-h"><b>${esc(c.author_name)}</b><span class="muted">${fmtShort(c.date)}</span></div><div>${esc(c.text)}</div></div>`).join("")}</div>` : ""}
      </div>
    </div>

    <div class="card section"><div class="card-h"><h3>${icon("calendar")}Неделя: план и факт</h3>
      <a class="meta" href="#calendar">все тренировки →</a></div>
      ${weekLanes(keyRows(o.week))}
      <div style="margin-top:14px">${lanesLegend()}</div></div>

    <div class="today-grid">
      ${o.garmin_status ? `<div class="card">${trainingCard(o.garmin_status)}</div>` : `<div></div>`}
      <div class="card"><div class="card-h"><h3>${icon("heart")}Восстановление</h3><span class="meta">${rec ? "ночь на " + fmtShort(rec.date) : ""}</span></div>
          ${rec ? `<div class="src-tag">${SRC[rs]}</div><div class="mini-stats">
            <div class="stat"><div class="label">Сон</div><div class="value num">${hrs(rec.sleep_s)}<small>ч</small></div>
              <div class="delta">${rec.deep_s ? `глуб. ${hrs(rec.deep_s)} · REM ${hrs(rec.rem_s)}` : ""}${rec.sleep_gap_s >= 1200 ? ` · перерыв ${fmtLate(Math.round(rec.sleep_gap_s / 60))}` : ""}</div></div>
            <div class="stat"><div class="label">Эффективность</div><div class="value num">${n0(rec.sleep_score)}<small>%</small></div></div>
            <div class="stat"><div class="label">HRV</div><div class="value num">${n0(rec.hrv)}<small>мс</small></div>
              <div class="delta ${hv != null && hv < -10 ? "t-bad" : ""}">${hv != null ? `${hv >= 0 ? "+" : ""}${hv}% к норме ${n0(rec.hrv_baseline)}` : ""}</div></div>
            <div class="stat"><div class="label">Пульс покоя</div><div class="value num">${n0(rec.resting_hr)}<small>уд/мин</small></div>
              <div class="delta">${rec.rhr_baseline ? `норма ${rec.rhr_baseline}` : ""}</div></div></div>` : `<div class="empty">Нет данных</div>`}
          ${g && (g.body_battery != null || g.readiness != null) ? `<div class="divider"></div><div class="src-tag">Garmin · ${fmtShort(g.date)}</div>
            <div class="mini-stats">
              <div class="stat"><div class="label">Body Battery</div><div class="value num">${n0(g.body_battery)}</div></div>
              <div class="stat"><div class="label">Готовность</div><div class="value num">${n0(g.readiness)}</div></div>
              <div class="stat"><div class="label">Стресс</div><div class="value num">${n0(g.stress)}</div></div>
              <div class="stat"><div class="label">Шаги</div><div class="value num">${n0(g.steps)}</div></div></div>` : ""}
        </div>
    </div>`;
  requestAnimationFrame(drawArrows);
}

// ---------- План / факт ----------
let calStart = mondayOf(new Date());
let calWeeks = 1;
async function renderCalendar() {
  const start = iso(calStart), end = iso(addDays(calStart, calWeeks * 7 - 1));
  // запас ±1 день, чтобы стрелки переносов на краях недели тоже находились
  const [cal] = await Promise.all([api(`calendar?start=${iso(addDays(calStart, -1))}&end=${iso(addDays(calStart, calWeeks * 7))}`),
    loadComments(iso(addDays(calStart, -1)), iso(addDays(calStart, calWeeks * 7)))]);
  const daysAll = keyRows(cal);
  const days = daysAll.slice(1, -1);
  const todayIso = iso(new Date());
  const items = days.flatMap((d) => d.items).filter((i) => i.sport !== "rest");
  const sum = (arr, side, k) => arr.reduce((s, i) => s + (i[side]?.[k] || 0), 0);
  const bySport = ["swim", "bike", "run", "strength"].map((s) => {
    const arr = items.filter((i) => i.sport === s);
    return { s, ph: sum(arr, "planned", "duration_s"), ah: sum(arr, "actual", "duration_s"), pd: sum(arr, "planned", "distance_m"), ad: sum(arr, "actual", "distance_m") };
  });
  $("#view-calendar").innerHTML = `
    <div class="page-head"><div><h1>План и факт</h1><div class="sub">что поставил тренер и что выполнено</div></div></div>
    <div class="cal-nav">
      <button class="btn" id="cal-prev" aria-label="Назад">←</button>
      <button class="btn" id="cal-today">Сегодня</button>
      <button class="btn" id="cal-next" aria-label="Вперёд">→</button>
      <span class="range">${fmtShort(start)} – ${fmtShort(end)}</span>
      <a class="btn" href="#report/${start}">${icon("print")}Отчёт за неделю</a>
      <div class="seg" style="margin-left:auto">${[1, 2, 4].map((w) => `<button data-w="${w}" class="${w === calWeeks ? "on" : ""}">${w} нед</button>`).join("")}</div>
    </div>
    <div class="card table-wrap" style="margin-bottom:16px">
      <table class="data num"><thead><tr><th>Вид</th><th>План, ч</th><th>Факт, ч</th><th>%</th><th>Факт, дистанция</th></tr></thead><tbody>
      ${bySport.map((r) => `<tr><td><span class="sport-cell" style="--c:${sportColor(r.s)}">${SPORT[r.s].ico}${SPORT[r.s].name}</span></td><td>${hrs(r.ph)}</td><td>${hrs(r.ah)}</td>
        <td>${r.ph ? Math.round((r.ah / r.ph) * 100) + "%" : "—"}</td><td>${fmtDist(r.ad, r.s)}</td></tr>`).join("")}
      <tr><td><b>Всего</b></td><td><b>${hrs(sum(items, "planned", "duration_s"))}</b></td><td><b>${hrs(sum(items, "actual", "duration_s"))}</b></td>
        <td></td><td>TSS ${n0(sum(items, "actual", "tss"))} из ${n0(sum(items, "planned", "tss"))}</td></tr>
      </tbody></table>
    </div>
    <details class="card add-form athlete-only" style="margin-bottom:16px"><summary>${icon("plus")}<b>Добавить тренировку по пульсу Fitbit</b>
        <span class="muted" style="font-size:13px"> — хоккей и всё, что не записывали на часы</span></summary>
      <form id="manual-form" class="grid g4" style="margin-top:12px;align-items:end">
        <label>Дата<input type="date" name="date" required value="${iso(addDays(new Date(), -1))}"></label>
        <label>Начало<input type="time" name="start" required value="22:30"></label>
        <label>Конец<input type="time" name="end" required value="23:45"></label>
        <label>Вид<select name="sport">${["hockey", "football", "run", "bike", "swim", "strength", "other"].map((k) => `<option value="${k}">${SPORT[k].name}</option>`).join("")}</select></label>
        <label class="wide">Название<input name="title" placeholder="Хоккей"></label>
        <button class="btn primary" type="submit">Добавить</button>
      </form></details>
    ${Array.from({ length: calWeeks }, (_, w) => `<div class="card" style="margin-bottom:12px">${weekLanes(days.slice(w * 7, w * 7 + 7))}</div>`).join("")}
    ${lanesLegend()}
    <div style="margin-top:14px">
    ${days.map((d) => `<div class="cal-day ${d.date === todayIso ? "is-today" : ""}">
        <div class="head"><b>${fmtDay(d.date)}${d.date === todayIso ? " · сегодня" : ""}${d.items.some((i) => i.actual?.kind === "leg") ? ` <span class="pill race-pill-sm">${icon("flag")}Старт</span>` : ""}</b>
          <span class="muted num" style="font-size:12px">${d.items.some((i) => i.actual) ? `${fmtDur(d.items.reduce((s, i) => s + (i.actual?.duration_s || 0), 0))} · ${n0(d.items.reduce((s, i) => s + (i.actual?.tss || 0), 0))} TSS` : ""}</span></div>
        <div class="card">${d.items.length ? d.items.map(workoutRow).join("") : `<div class="empty">Ничего не запланировано</div>`}</div>
      </div>`).join("")}
    </div>`;
  requestAnimationFrame(drawArrows);
  $("#manual-form").onsubmit = async (e) => {
    e.preventDefault();
    const f = Object.fromEntries(new FormData(e.target));
    const b = e.target.querySelector("button"); b.disabled = true; toast("Загружаю пульс Fitbit…", 30000);
    try {
      const r = await api("manual", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(f) });
      toast(r.avg_hr ? `Добавлено: пульс ср. ${r.avg_hr}, макс. ${r.max_hr}, TSS ${r.tss}` : "Добавлено, но пульса Fitbit за это время нет", 6000);
      calStart = mondayOf(parseD(f.date)); renderCalendar();
    } catch (err) { toast("Ошибка: " + err.message, 6000); b.disabled = false; }
  };
  $("#cal-prev").onclick = () => { calStart = addDays(calStart, -7 * calWeeks); renderCalendar(); };
  $("#cal-next").onclick = () => { calStart = addDays(calStart, 7 * calWeeks); renderCalendar(); };
  $("#cal-today").onclick = () => { calStart = mondayOf(new Date()); renderCalendar(); };
  document.querySelectorAll("#view-calendar .seg button").forEach((b) => (b.onclick = () => { calWeeks = +b.dataset.w; renderCalendar(); }));
}

async function delManual(id) {
  if (!confirm("Удалить эту тренировку?")) return;
  await fetch("/api/manual/" + encodeURIComponent(id), { method: "DELETE" });
  route();
}

// ---------- графики ----------
const charts = {};
function chartDefaults() {
  Chart.defaults.font.family = '"Inter", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif';
  Chart.defaults.font.size = 12;
  Chart.defaults.color = css("--muted");
  Chart.defaults.borderColor = css("--grid");
  Chart.defaults.plugins.tooltip.backgroundColor = css("--ink");
  Chart.defaults.plugins.tooltip.titleColor = css("--page");
  Chart.defaults.plugins.tooltip.bodyColor = css("--page");
  Chart.defaults.plugins.tooltip.padding = 10;
  Chart.defaults.plugins.tooltip.cornerRadius = 8;
  Chart.defaults.plugins.tooltip.boxPadding = 4;
  Chart.defaults.plugins.legend.labels.usePointStyle = true;
  Chart.defaults.plugins.legend.labels.pointStyle = "rectRounded";
  Chart.defaults.plugins.legend.labels.color = css("--ink-2");
  Chart.defaults.plugins.legend.align = "start";
}
function mkChart(id, cfg) {
  charts[id]?.destroy();
  const ctx = document.getElementById(id);
  if (!ctx) return;
  charts[id] = new Chart(ctx, cfg);
}
const lineDs = (label, data, color, extra = {}) => ({
  label, data, borderColor: color, backgroundColor: color, borderWidth: 2, pointRadius: 0,
  pointHoverRadius: 5, pointHoverBorderWidth: 2, pointHoverBorderColor: css("--surface"), tension: 0.25, spanGaps: true, ...extra,
});
const timeOpts = (extra = {}) => ({
  responsive: true, maintainAspectRatio: false, interaction: { mode: "index", intersect: false },
  scales: {
    x: { grid: { display: false }, ticks: { maxTicksLimit: 8, maxRotation: 0 }, border: { color: css("--axis") } },
    y: { grid: { color: css("--grid") }, border: { display: false }, ...extra.y },
  },
  plugins: { legend: { display: extra.legend ?? true }, tooltip: extra.tooltip || {} },
});

// ---------- карты тренировок (Leaflet, грузится по требованию) ----------
let _leaflet;
function loadLeaflet() {
  if (window.L) return Promise.resolve();
  return (_leaflet ||= new Promise((ok, fail) => {
    const l = document.createElement("link"); l.rel = "stylesheet";
    l.href = "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css"; document.head.append(l);
    const sc = document.createElement("script"); sc.src = "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js";
    sc.onload = ok; sc.onerror = fail; document.head.append(sc);
  }));
}
const trackCache = {};
const getTrack = (src, id) => (trackCache[src + id] ||= api(`track/${src}/${encodeURIComponent(id)}`));
const ZONE_COL = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#104281"];
const LTHR_DEFAULT = 165;
let _lthr = LTHR_DEFAULT;
let _zones = null;
const hrZone = (hr) => { if (_zones) { let z = 0; _zones.forEach((f, i) => { if (hr >= f) z = i; }); return z; }
  const r = hr / _lthr; return r < 0.85 ? 0 : r < 0.9 ? 1 : r < 0.95 ? 2 : r < 1 ? 3 : 4; };
const dark = () => matchMedia("(prefers-color-scheme: dark)").matches && document.documentElement.dataset.theme !== "light";
function baseMap(el) {
  const m = L.map(el, { zoomControl: true, attributionControl: true, scrollWheelZoom: false });
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19, className: "osm-tiles", attribution: "© OpenStreetMap" }).addTo(m);
  el.addEventListener("click", () => m.scrollWheelZoom.enable(), { once: true });
  return m;
}
// маршрут, раскрашенный по пульсовым зонам; без пульса — цветом вида спорта
function drawRoute(m, pts, color, byHr = true) {
  const layers = [];
  const hasHr = byHr && pts.some((p) => p[2]);
  if (!hasHr) { layers.push(L.polyline(pts.map((p) => [p[0], p[1]]), { color, weight: 4, opacity: .9 }).addTo(m)); }
  else {
    let seg = [pts[0]], z = hrZone(pts[0][2] || 0);
    for (let i = 1; i < pts.length; i++) {
      const zi = pts[i][2] ? hrZone(pts[i][2]) : z;
      seg.push(pts[i]);
      if (zi !== z || i === pts.length - 1) {
        layers.push(L.polyline(seg.map((p) => [p[0], p[1]]), { color: ZONE_COL[z], weight: 5, opacity: .95 }).addTo(m));
        seg = [pts[i]]; z = zi;
      }
    }
  }
  const s = pts[0], e = pts[pts.length - 1];
  layers.push(L.circleMarker([s[0], s[1]], { radius: 6, color: "#fff", weight: 2, fillColor: "#0ca30c", fillOpacity: 1 }).addTo(m));
  layers.push(L.circleMarker([e[0], e[1]], { radius: 6, color: "#fff", weight: 2, fillColor: "#d03b3b", fillOpacity: 1 }).addTo(m));
  return L.featureGroup(layers);
}
const zoneLegend = () => `<div class="legend map-legend">${ZONE_COL.map((c, i) => `<span><i class="sw" style="background:${c}"></i>Z${i + 1}</span>`).join("")}
  <span><i class="sw" style="background:#0ca30c;border-radius:50%"></i>старт</span><span><i class="sw" style="background:#d03b3b;border-radius:50%"></i>финиш</span></div>`;

async function miniMap(el, src, id, color) {
  try {
    await loadLeaflet();
    const t = await getTrack(src, id);
    if (!t.points?.length) { el.outerHTML = ""; return; }
    const m = baseMap(el);
    const g = drawRoute(m, t.points, color);
    m.fitBounds(g.getBounds(), { padding: [16, 16] });
  } catch { el.innerHTML = `<div class="empty" style="padding:12px">Карта недоступна</div>`; }
}

// ---------- Дисциплины: цель 10:00 и витрины ----------
const DISC = { swim: { name: "Плавание", dist: "3,8 км" }, bike: { name: "Велосипед", dist: "180 км" }, run: { name: "Бег", dist: "42,2 км" } };
const SEG = [["swim", "Плавание"], ["t1", "T1"], ["bike", "Велосипед"], ["t2", "T2"], ["run", "Бег"]];
const hms = (s) => { if (s == null) return "—"; s = Math.round(Math.abs(s)); const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), x = s % 60;
  return h ? `${h}:${String(m).padStart(2, "0")}:${String(x).padStart(2, "0")}` : `${m}:${String(x).padStart(2, "0")}`; };
const hm = (s) => { if (s == null) return "—"; s = Math.round(s); return `${Math.floor(s / 3600)}:${String(Math.floor((s % 3600) / 60)).padStart(2, "0")}`; };
const mmss = (s) => (s == null ? "—" : `${Math.floor(s / 60)}:${String(Math.round(s % 60)).padStart(2, "0")}`);
// темп в принятом для вида спорта виде: плавание — /100 м, бег — /км, вело — км/ч
const fmtPaceS = (sport, pace) => (pace == null ? "—" : sport === "bike" ? `${(3600 / pace).toFixed(1)} км/ч` : `${mmss(pace)} /${sport === "swim" ? "100 м" : "км"}`);
const parseHMS = (v) => { const p = String(v).trim().split(":").map(Number); if (p.some(isNaN)) return null;
  // как и при выводе: «ч:мм:сс» или «мм:сс» (T1 «6:00» — это 6 минут)
  return p.length === 3 ? p[0] * 3600 + p[1] * 60 + p[2] : p.length === 2 ? p[0] * 60 + p[1] : p[0] * 60; };
const gapText = (g) => (g == null ? "нет данных" : g <= 0 ? `в цели (запас ${hm(-g)})` : `+${hm(g)} до цели`);
const gapCls = (g) => (g == null ? "" : g <= 0 ? "t-good" : g < 1800 ? "t-warn" : "t-bad");

function progressRow(label, done, target, fmt) {
  const pct = Math.min(100, (done / target) * 100);
  return `<div class="bal"><div class="bal-h"><span>${label}</span><span class="num">${fmt(done)} <span class="muted">/ ${fmt(target)}</span></span></div>
    <div class="progress"><div style="width:${Math.max(pct, 1)}%;${pct >= 100 ? "background:var(--good)" : ""}"></div></div></div>`;
}
const km = (m, sport) => (sport === "swim" ? `${n0(m)} м` : `${(m / 1000).toFixed(m >= 100000 ? 0 : 1)} км`);

let goalTab = "summary";
async function renderGoal() {
  const sub = (location.hash.split("/")[1] || goalTab);
  const TABS = [["summary", "Свод", "flag"], ["path", "Путь", "trend"], ["swim", "Плавание", "swim"], ["bike", "Велосипед", "bike"],
    ["run", "Бег", "run"], ["records", "Рекорды", "target"], ["race", "Гонка", "flag"], ["gear", "Снаряжение", "sliders"]];
  goalTab = TABS.some((t) => t[0] === sub) ? sub : "summary";
  const el = $("#view-goal");
  const tabs = `<div class="seg goal-tabs">${TABS.map(([k, l, ic]) => `<button data-t="${k}" class="${k === goalTab ? "on" : ""}">${icon(ic)}${l}</button>`).join("")}</div>`;
  const R = { summary: renderGoalSummary, path: renderPath, records: renderRecords, race: renderRace, gear: renderGear };
  if (R[goalTab]) await R[goalTab](el, tabs); else await renderDiscipline(el, tabs, goalTab);
  el.querySelectorAll(".goal-tabs button").forEach((b) => (b.onclick = () => { location.hash = b.dataset.t === "summary" ? "#goal" : "#goal/" + b.dataset.t; }));
}

function splitBar(label, parts, total, scale) {
  return `<div class="split-row"><div class="split-label"><b>${label}</b><span class="num">${hm(total)}</span></div>
    <div class="split-bar" style="width:${(total / scale) * 100}%">${parts.map(([k, t]) => `<span class="sb-${k}" style="flex:${t}" title="${(SEG.find((x) => x[0] === k) || [])[1]}: ${hms(t)}">${t / total > 0.08 ? hm(t) : ""}</span>`).join("")}</div></div>`;
}

async function renderGoalSummary(el, tabs) {
  const s = await api("goals");
  const g = s.goals, d = s.disciplines;
  const proj = { swim: d.swim.projection.time, t1: g.t1, bike: d.bike.projection.time, t2: g.t2, run: d.run.projection.time };
  const scale = Math.max(s.goal_total, s.projection_total || 0);
  const gap = s.projection_total ? s.projection_total - s.goal_total : null;
  el.innerHTML = `
    <div class="page-head"><div><h1>Цель: Ironman за ${hm(s.goal_total)}</h1>
      <div class="sub">3,8 км плавания · 180 км велосипеда · 42,2 км бега · старт ${fmtShort(o_race().date)} ${o_race().date.slice(0, 4)}</div></div>${tabs}</div>

    <div class="card section"><div class="card-h"><h3>${icon("target")}Цель и текущий прогноз</h3>
      <span class="meta ${gapCls(gap)}" style="font-size:13px;font-weight:600">${s.projection_total ? `прогноз ${hm(s.projection_total)} · ${gapText(gap)}` : ""}</span></div>
      ${splitBar("Цель", SEG.map(([k]) => [k, g[k]]), s.goal_total, scale)}
      ${s.projection_total ? splitBar("Сейчас", SEG.map(([k]) => [k, proj[k]]), s.projection_total, scale) : ""}
      <div class="legend" style="margin-top:12px">${SEG.map(([k, l]) => `<span><i class="sw sb-${k}"></i>${l}</span>`).join("")}</div>
    </div>

    <div class="grid g3 section">${["swim", "bike", "run"].map((k) => { const x = d[k];
      return `<a class="card disc-card" href="#goal/${k}" style="--c:${sportColor(k)}">
        <div class="card-h"><h3><span class="sport-badge sm">${icon(k)}</span>${DISC[k].name}</h3><span class="meta">${DISC[k].dist}</span></div>
        <div class="mini-stats">
          <div class="stat"><div class="label">Цель</div><div class="value num">${hm(x.goal.time)}</div><div class="delta">${fmtPaceS(k, x.goal.pace)}</div></div>
          <div class="stat"><div class="label">Прогноз сейчас</div><div class="value num ${gapCls(x.gap_s)}">${hm(x.projection.time)}</div><div class="delta ${gapCls(x.gap_s)}">${gapText(x.gap_s)}</div></div>
          <div class="stat"><div class="label">Темп на тренировках</div><div class="value num" style="font-size:17px">${fmtPaceS(k, x.current.pace_28)}</div><div class="delta">за ${x.current.pace_basis}</div></div>
          <div class="stat"><div class="label">Объём за 4 недели</div><div class="value num" style="font-size:17px">${km(x.current.distance_28, k)}</div><div class="delta">${x.current.sessions_28} трен.</div></div>
        </div>
        <div class="divider"></div>
        ${progressRow("Самая длинная за 90 дней", x.milestones.long.done, x.milestones.long.target, (m) => km(m, k))}
        ${progressRow("Пиковая неделя", x.milestones.week.done, x.milestones.week.target, (m) => km(m, k))}
      </a>`; }).join("")}</div>

    <div class="today-grid">
      <div class="card athlete-only"><div class="card-h"><h3>${icon("sliders")}Раскладка цели</h3><span class="meta">формат ч:мм:сс</span></div>
        <form id="goal-form" class="goal-form">
          ${SEG.map(([k, l]) => `<label><span>${l}</span><input name="${k}" value="${hms(g[k])}" inputmode="numeric">
            <em class="muted num" data-pace="${k}"></em></label>`).join("")}
          <div class="goal-total"><span>Итого</span><b class="num" id="goal-total">${hms(s.goal_total)}</b></div>
          <button class="btn primary" type="submit">Сохранить цель</button>
        </form></div>
      <div class="card"><div class="card-h"><h3>${icon("flag")}Прошедшие старты</h3></div>
        ${s.races.length ? s.races.map((r) => `<div class="src-tag">${fmtShort(r.date)} ${r.date.slice(0, 4)}${r.title ? " · " + esc(r.title) : ""} · итог <b style="color:var(--ink)">${hms(r.total_s)}</b></div>
          <table class="data num" style="margin-bottom:14px"><tbody>${r.legs.map((l) => `<tr><td><span class="sport-cell" style="--c:${sportColor(l.sport)}">${icon(l.sport)}${l.label || DISC[l.sport]?.name || SPORT[l.sport]?.name}</span></td>
            <td>${l.sport === "transition" ? "" : km(l.distance_m, l.sport)}</td><td>${hms(l.time_s)}</td>
            <td>${l.sport === "transition" || !l.distance_m ? "" : fmtPaceS(l.sport, l.time_s / (l.distance_m / (l.sport === "swim" ? 100 : 1000)))}</td>
            <td>${l.avg_hr ? n0(l.avg_hr) + " уд" : ""}</td><td>${l.te ? "TE " + (+l.te).toFixed(1) : ""}</td></tr>`).join("")}</tbody></table>`).join("")
          : `<div class="empty">Стартов пока не найдено</div>`}
        <div class="muted" style="font-size:12.5px;margin-top:12px">Прогноз по плаванию и велосипеду — по лучшей четверти ваших тренировок с поправкой на дистанцию (формула Ригеля),
          по бегу — прогноз Garmin на марафон × 1,12 на усталость после велоэтапа. Чем больше тренировок, тем точнее.</div>
      </div>
    </div>`;
  const form = $("#goal-form");
  const DIST = { swim: 38, bike: 180, run: 42.195 };
  const upd = () => {
    let tot = 0;
    SEG.forEach(([k]) => { const v = parseHMS(form[k].value); tot += v || 0;
      const em = form.querySelector(`[data-pace="${k}"]`);
      if (em && DIST[k] && v) em.textContent = fmtPaceS(k, v / DIST[k]); });
    $("#goal-total").textContent = hms(tot);
  };
  form.oninput = upd; upd();
  form.onsubmit = async (e) => {
    e.preventDefault();
    const body = Object.fromEntries(SEG.map(([k]) => [k, parseHMS(form[k].value)]));
    if (Object.values(body).some((v) => !v)) return toast("Проверьте формат времени: ч:мм:сс");
    await api("goals", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    toast("Цель сохранена"); renderGoal();
  };
}
let _race = null;
const o_race = () => _race || { date: "2028-09-30" };

async function renderDiscipline(el, tabs, sport) {
  const d = await api(`discipline/${sport}`);
  const c = d.current, ss = d.sessions;
  const better = sport === "bike" ? "выше — быстрее" : "ниже — быстрее";
  el.innerHTML = `
    <div class="page-head"><div><h1 style="display:flex;align-items:center;gap:12px"><span class="sport-badge" style="--c:${sportColor(sport)}">${icon(sport)}</span>${DISC[sport].name} · ${DISC[sport].dist}</h1>
      <div class="sub">${d.projection.basis}</div></div>${tabs}</div>

    <div class="kpis">
      <div class="card kpi"><div class="stat"><div class="label">Цель</div><div class="value num">${hm(d.goal.time)}</div>
        <div class="delta">${fmtPaceS(sport, d.goal.pace)}${sport !== "bike" ? ` · ${d.goal.speed_kmh} км/ч` : ""}</div></div></div>
      <div class="card kpi"><div class="stat"><div class="label">Прогноз сейчас</div><div class="value num ${gapCls(d.gap_s)}">${hm(d.projection.time)}</div>
        <div class="delta ${gapCls(d.gap_s)}">${gapText(d.gap_s)}</div></div></div>
      <div class="card kpi"><div class="stat"><div class="label">Темп на тренировках · ${c.pace_basis}</div><div class="value num" style="font-size:24px">${fmtPaceS(sport, c.pace_28)}</div>
        <div class="delta ${d.pace_gap_pct > 0 ? "t-bad" : "t-good"}">${d.pace_gap_pct != null ? (d.pace_gap_pct > 0 ? `на ${d.pace_gap_pct}% медленнее целевого` : `быстрее целевого на ${-d.pace_gap_pct}%`) : ""}</div></div></div>
      <div class="card kpi"><div class="stat"><div class="label">Лучший темп · 90 дней</div><div class="value num" style="font-size:24px">${fmtPaceS(sport, c.best_pace_90)}</div>
        <div class="delta">${c.avg_hr_90 ? `средний пульс ${c.avg_hr_90}` : ""}${c.power_90 ? ` · мощность ${c.power_90} Вт` : ""}</div></div></div>
    </div>

    <div class="today-grid">
      <div class="card chart-card"><h3>Темп по тренировкам</h3><div class="sub">${sport === "bike" ? "км/ч" : "мин:сек"} · ${better} · пунктир — целевой темп на старте</div>
        <div class="chart-box"><canvas id="c-pace"></canvas></div></div>
      <div class="card"><div class="card-h"><h3>${icon("target")}Вехи подготовки</h3></div>
        ${progressRow("Самая длинная тренировка · 90 дней", d.milestones.long.done, d.milestones.long.target, (m) => km(m, sport))}
        ${progressRow("Самая длинная · за год", c.longest_all, d.milestones.long.target, (m) => km(m, sport))}
        ${progressRow("Пиковая неделя · 4 недели", d.milestones.week.done, d.milestones.week.target, (m) => km(m, sport))}
        ${progressRow("Средняя неделя · 4 недели", c.avg_week_28, d.milestones.week.target, (m) => km(m, sport))}
        <div class="muted" style="font-size:12.5px;margin-top:6px">Ориентиры пиковой фазы подготовки к Ironman: самая длинная сессия
          ${km(d.milestones.long.target, sport)}, неделя до ${km(d.milestones.week.target, sport)}. Точный план — за тренером.</div>
        ${d.garmin ? `<div class="divider"></div><div class="src-tag">Garmin · бег отдельно</div><div class="mini-stats">
          <div class="stat"><div class="label">VO2 max</div><div class="value num">${d.garmin.vo2max ?? "—"}</div></div>
          <div class="stat"><div class="label">Марафон</div><div class="value num" style="font-size:18px">${fmtHMS(d.garmin.race?.timeMarathon)}</div></div>
          <div class="stat"><div class="label">Полумарафон</div><div class="value num" style="font-size:18px">${fmtHMS(d.garmin.race?.timeHalfMarathon)}</div></div>
          <div class="stat"><div class="label">10 км</div><div class="value num" style="font-size:18px">${fmtHMS(d.garmin.race?.time10K)}</div></div></div>` : ""}
      </div>
    </div>

    ${ss.some((x) => x.has_gps) ? `<div class="card section"><div class="card-h"><h3>${icon("target")}Карты тренировок</h3>
      <span class="meta">${ss.filter((x) => x.has_gps).length} маршрутов с GPS · клик по тренировке — маршрут по пульсовым зонам</span></div>
      <div class="map-wrap"><div><div class="map map-big" id="disc-map"></div><div id="disc-map-info"></div></div>
        <div class="route-list">${ss.filter((x) => x.has_gps).slice().reverse().map((x, i) => `<button class="route ${i === 0 ? "on" : ""}" data-id="${esc(x.source_id)}" data-src="${esc(x.source)}">
          <b>${fmtShort(x.date)} ${x.date.slice(2, 4)}</b><span>${esc(x.title || "")}</span>
          <span class="num muted">${km(x.distance_m, sport)} · ${fmtPaceS(sport, x.pace)}${x.avg_hr ? ` · ${n0(x.avg_hr)} уд` : ""}</span></button>`).join("")}
          <button class="route" data-id="__all">Все маршруты на одной карте</button></div></div></div>` : ""}

    ${sport !== "swim" ? `<div class="card chart-card section"><h3>Аэробная эффективность</h3>
      <div class="sub" id="ef-sub">скорость на один удар сердца в спокойных тренировках (пульс ниже Z4) · растёт — значит, аэробная база строится</div>
      <div class="chart-box sm"><canvas id="c-ef"></canvas></div></div>` : ""}

    <div class="card chart-card section"><h3>Объём по неделям</h3><div class="sub">${sport === "swim" ? "метры" : "километры"} за 16 недель</div>
      <div class="chart-box sm"><canvas id="c-dvol"></canvas></div></div>

    <div class="card section"><div class="card-h"><h3>${icon("calendar")}Тренировки</h3><span class="meta">за год, без коротких и сбойных записей</span></div>
      <div class="table-wrap"><table class="data num"><thead><tr><th>Дата</th><th>Тренировка</th><th>Дистанция</th><th>Время в движении</th><th>${sport === "bike" ? "Скорость" : "Темп"}</th><th>Пульс</th>${sport === "bike" ? "<th>Мощность</th>" : ""}</tr></thead><tbody>
      ${ss.slice().reverse().map((x) => `<tr><td>${fmtShort(x.date)} ${x.date.slice(2, 4)}</td><td style="text-align:left">${esc(x.title || "")}</td><td>${km(x.distance_m, sport)}</td>
        <td>${hms(x.moving_s)}</td><td class="${x.pace <= d.goal.pace ? "t-good" : ""}">${fmtPaceS(sport, x.pace)}</td><td>${n0(x.avg_hr)}</td>${sport === "bike" ? `<td>${n0(x.np || x.avg_power)}</td>` : ""}</tr>`).join("") || `<tr><td colspan="7" class="muted">Нет тренировок</td></tr>`}
      </tbody></table></div></div>`;

  if (ss.some((x) => x.has_gps)) discMaps(sport, ss.filter((x) => x.has_gps));
  if (sport !== "swim") api(`efficiency/${sport}`).then((ef) => {
    const tr = ef.trend_90d_pct;
    $("#ef-sub").innerHTML += tr == null ? " · мало данных для тренда" : ` · тренд за 90 дней: <b class="${tr >= 0 ? "t-good" : "t-bad"}">${tr >= 0 ? "+" : ""}${tr}%</b>`;
    mkChart("c-ef", { type: "line", data: { labels: ef.points.map((x) => fmtShort(x.date)), datasets: [lineDs("Эффективность", ef.points.map((x) => x.ef), css("--" + sport),
      { pointRadius: 4, tension: 0, pointBackgroundColor: css("--" + sport), pointBorderColor: css("--surface"), pointBorderWidth: 2 })] },
      options: { ...timeOpts({ legend: false }), plugins: { legend: { display: false }, tooltip: { callbacks: { label: (c) => {
        const x = ef.points[c.dataIndex]; return [`${x.ef} м/мин на удар`, `${fmtPaceS(sport, x.pace)} при пульсе ${n0(x.hr)}`, km(x.distance_m, sport)]; } } } } } });
  });
  const val = (x) => (sport === "bike" ? +(3600 / x.pace).toFixed(1) : x.pace);
  const goalV = sport === "bike" ? +(3600 / d.goal.pace).toFixed(1) : d.goal.pace;
  mkChart("c-pace", { type: "line", data: { labels: ss.map((x) => fmtShort(x.date)), datasets: [
    { label: "Цель", data: ss.map(() => goalV), borderColor: css("--good"), borderDash: [6, 4], borderWidth: 1.5, pointRadius: 0 },
    lineDs(sport === "bike" ? "Скорость" : "Темп", ss.map(val), sportColor(sport) === "var(--other)" ? css("--s1") : css("--" + sport),
      { pointRadius: 4, pointHoverRadius: 6, tension: 0, pointBackgroundColor: css("--" + sport), pointBorderColor: css("--surface"), pointBorderWidth: 2 }),
  ] }, options: { ...timeOpts(),
    scales: { x: { grid: { display: false }, ticks: { maxTicksLimit: 8, maxRotation: 0 } },
      y: { reverse: sport !== "bike", grid: { color: css("--grid") }, border: { display: false },
        ticks: { callback: (v) => (sport === "bike" ? v : mmss(v)) } } },
    plugins: { legend: { display: true }, tooltip: { callbacks: { label: (ctx) => {
      if (ctx.datasetIndex === 0) return `Цель: ${fmtPaceS(sport, d.goal.pace)}`;
      const x = ss[ctx.dataIndex]; return [`${fmtPaceS(sport, x.pace)} · ${km(x.distance_m, sport)}`, x.avg_hr ? `пульс ${n0(x.avg_hr)}` : ""]; } } } } } });
  mkChart("c-dvol", { type: "bar", data: { labels: d.weeks.map((w) => fmtShort(w.week)), datasets: [{ label: "Объём",
    data: d.weeks.map((w) => (sport === "swim" ? w.distance_m : +(w.distance_m / 1000).toFixed(1))), backgroundColor: css("--" + sport), borderRadius: 4, maxBarThickness: 30 }] },
    options: timeOpts({ legend: false }) });
}

async function discMaps(sport, gps) {
  await loadLeaflet();
  const el = $("#disc-map"); if (!el) return;
  const m = baseMap(el), color = css("--" + sport);
  let layer = null;
  const info = $("#disc-map-info");
  const show = async (btn) => {
    document.querySelectorAll(".route").forEach((b) => b.classList.toggle("on", b === btn));
    if (layer) m.removeLayer(layer);
    if (btn.dataset.id === "__all") {
      info.innerHTML = `<div class="muted" style="font-size:12.5px;margin-top:8px">Загружаю ${gps.length} маршрутов…</div>`;
      const tr = await Promise.all(gps.map((x) => getTrack(x.source, x.source_id).catch(() => null)));
      layer = L.featureGroup(tr.filter((t) => t?.points?.length).map((t) => L.polyline(t.points.map((p) => [p[0], p[1]]), { color, weight: 3, opacity: .55 }))).addTo(m);
      info.innerHTML = `<div class="muted" style="font-size:12.5px;margin-top:8px">Все маршруты за год — где вы тренируетесь чаще всего</div>`;
    } else {
      const x = gps.find((g) => g.source_id === btn.dataset.id);
      const t = await getTrack(btn.dataset.src, btn.dataset.id);
      layer = drawRoute(m, t.points, color);
      const elev = t.points.map((p) => p[4]).filter((v) => v != null);
      const gain = elev.reduce((a, v, i) => a + (i && v > elev[i - 1] ? v - elev[i - 1] : 0), 0);
      info.innerHTML = `${zoneLegend()}<div class="route-stats num">
        <span><b>${km(x.distance_m, sport)}</b> дистанция</span><span><b>${hms(x.moving_s)}</b> в движении</span>
        <span><b>${fmtPaceS(sport, x.pace)}</b> ${sport === "bike" ? "скорость" : "темп"}</span>
        ${x.avg_hr ? `<span><b>${n0(x.avg_hr)}</b> ср. пульс</span>` : ""}${elev.length ? `<span><b>${n0(gain)} м</b> набор</span>` : ""}</div>`;
    }
    if (layer.getLayers().length) m.fitBounds(layer.getBounds(), { padding: [20, 20] });
  };
  document.querySelectorAll(".route").forEach((b) => (b.onclick = () => show(b)));
  show(document.querySelector(".route.on"));
}

// ---------- Путь к старту ----------
async function renderPath(el, tabs) {
  const p = await api("path");
  const rd = parseD(p.race.date), t0 = parseD(p.phases[0].start), span = rd - t0, now = new Date();
  const pos = Math.max(0, Math.min(100, ((now - t0) / span) * 100));
  const lag = p.ctl_target_today != null ? Math.round(p.ctl - p.ctl_target_today) : null;
  el.innerHTML = `
    <div class="page-head"><div><h1>Путь к старту</h1><div class="sub">${esc(p.race.name)} · ${fmtShort(p.race.date)} ${p.race.date.slice(0, 4)} · осталось ${p.weeks_left} недель</div></div>${tabs}</div>
    <div class="card section"><div class="card-h"><h3>${icon("calendar")}Фазы подготовки</h3><span class="meta">ориентир — точный план за тренером</span></div>
      <div class="phases">${p.phases.map((ph, i) => { const w = ((parseD(ph.end) - parseD(ph.start)) / span) * 100;
        return `<div class="phase ph${i} ${ph.current ? "cur" : ""}" style="flex:${w}" title="${esc(ph.name)}: ${fmtShort(ph.start)} – ${fmtShort(ph.end)}"><span>${esc(ph.name)}</span></div>`; }).join("")}
        <i class="now" style="left:${pos}%"><b>сейчас</b></i></div>
      <div class="phase-dates muted num"><span>${fmtShort(p.phases[0].start)} ${p.phases[0].start.slice(0, 4)}</span><span>старт ${fmtShort(p.race.date)} ${p.race.date.slice(0, 4)}</span></div>
    </div>
    <div class="today-grid">
      <div class="card chart-card"><h3>Фитнес (CTL): план и факт</h3><div class="sub">пунктир — ориентир по фазам, линия — ваш фактический CTL</div>
        <div class="chart-box"><canvas id="c-path"></canvas></div></div>
      <div class="stack">
        <div class="card"><div class="card-h"><h3>${icon("target")}Сейчас: ${esc(p.current.name)}</h3><span class="meta">${fmtShort(p.current.start)} – ${fmtShort(p.current.end)}</span></div>
          <div class="mini-stats">
            <div class="stat"><div class="label">CTL сейчас</div><div class="value num">${Math.round(p.ctl)}</div></div>
            <div class="stat"><div class="label">Ориентир на сегодня</div><div class="value num">${p.ctl_target_today != null ? Math.round(p.ctl_target_today) : "—"}</div>
              <div class="delta ${lag >= 0 ? "t-good" : lag > -10 ? "t-warn" : "t-bad"}">${lag == null ? "" : lag >= 0 ? `опережаете на ${lag}` : `отстаёте на ${-lag}`}</div></div>
            <div class="stat"><div class="label">Объём фазы</div><div class="value" style="font-size:17px">${esc(p.current.hours)}</div></div>
            <div class="stat"><div class="label">CTL к концу фазы</div><div class="value num">${p.current.ctl_end}</div></div>
          </div>
          <div class="desc-plain">${esc(p.current.focus)}</div></div>
        <div class="card"><div class="card-h"><h3>${icon("flag")}Вехи</h3></div>
          ${p.milestones.map((m) => `<div class="milestone ${m.done ? "done" : ""}" style="--c:${sportColor(m.sport)}">${icon(m.done ? "check" : m.sport)}<span>${esc(m.label)}</span>
            <em class="num muted">${m.done ? "✓" : `лучшее ${km(m.best, m.sport)}`}</em></div>`).join("")}</div>
      </div>
    </div>
    <div class="card section"><div class="card-h"><h3>${icon("calendar")}Все фазы</h3></div>
      <div class="table-wrap"><table class="data"><thead><tr><th>Фаза</th><th>Даты</th><th>CTL</th><th>Часы в неделю</th><th style="text-align:left">Фокус</th></tr></thead><tbody>
      ${p.phases.map((ph) => `<tr class="${ph.current ? "cur-row" : ""}"><td><b>${esc(ph.name)}</b></td><td class="num">${fmtShort(ph.start)} ${ph.start.slice(2, 4)} – ${fmtShort(ph.end)} ${ph.end.slice(2, 4)}</td>
        <td class="num">${Math.round(ph.ctl_start)} → ${ph.ctl_end}</td><td>${esc(ph.hours)}</td><td style="text-align:left;white-space:normal">${esc(ph.focus)}</td></tr>`).join("")}
      </tbody></table></div></div>`;
  const all = [...new Set([...p.target.map((x) => x.date), ...p.actual.map((x) => x.date)])].sort();
  const tg = Object.fromEntries(p.target.map((x) => [x.date, x.ctl])), ac = Object.fromEntries(p.actual.map((x) => [x.date, x.ctl]));
  mkChart("c-path", { type: "line", data: { labels: all.map((d) => `${fmtShort(d)} ${d.slice(2, 4)}`), datasets: [
    { label: "Ориентир", data: all.map((d) => tg[d] ?? null), borderColor: css("--muted"), borderDash: [6, 4], borderWidth: 1.5, pointRadius: 0, spanGaps: true },
    lineDs("Факт", all.map((d) => ac[d] ?? null), css("--s1")),
  ] }, options: timeOpts({ y: { min: 0 } }) });
}

// ---------- Рекорды ----------
async function renderRecords(el, tabs) {
  const r = await api("records");
  const label = (s, d) => (s === "swim" ? `${n0(d)} м` : `${d / 1000 === 21.097 ? "21,1" : n0(d / 1000)} км`);
  el.innerHTML = `
    <div class="page-head"><div><h1>Личные рекорды</h1><div class="sub">лучший средний темп на тренировке не короче дистанции · по чистому времени движения</div></div>${tabs}</div>
    <div class="grid g3 section">${["swim", "bike", "run"].map((s) => `<div class="card" style="--c:${sportColor(s)}">
      <div class="card-h"><h3><span class="sport-badge sm">${icon(s)}</span>${DISC[s].name}</h3><span class="meta">${r[s].sessions} трен.</span></div>
      ${r[s].rows.map((x) => `<div class="pr-row"><div><b>${label(s, x.distance)}</b>${x.best ? `<span class="muted num">${fmtShort(x.best.date)} ${x.best.date.slice(2, 4)}</span>` : ""}</div>
        ${x.best ? `<div class="num" style="text-align:right"><b>${hms(x.best.time)}</b><span class="muted">${fmtPaceS(s, x.best.pace)}</span></div>${sparkline(x.progress.map((q) => -q.pace), css("--" + s))}`
          : `<div class="muted" style="text-align:right">ещё нет<br><span style="font-size:11.5px">нужна тренировка от ${label(s, x.distance)}</span></div><div></div>`}</div>`).join("")}
      <div class="divider"></div>
      <div class="muted" style="font-size:12.5px">Самая длинная: ${r[s].longest ? `<b style="color:var(--ink)">${km(r[s].longest.distance, s)}</b> · ${fmtShort(r[s].longest.date)} ${r[s].longest.date.slice(2, 4)}` : "—"}</div>
    </div>`).join("")}</div>
    <div class="muted" style="font-size:12.5px">Если рекорд держит сбойная тренировка (например, в часах была неверная длина бассейна), откройте её в «План/факт» и нажмите
      «Не учитывать в статистике» — она пропадёт из рекордов, темпа и прогноза.</div>`;
}

// ---------- Гонка: выбор старта и питание ----------
const RACES = [
  { id: "emilia", name: "IRONMAN Italy Emilia-Romagna", place: "Червия, Италия", month: 9, profile: "плоская", fast: true, water: "море, ~23°C", air: "22–26°C", note: "одна из самых быстрых трасс Европы" },
  { id: "barcelona", name: "IRONMAN Barcelona", place: "Калелья, Испания", month: 10, profile: "плоская", fast: true, water: "море, ~21°C", air: "20–25°C", note: "быстрая, но бывает ветер и волна" },
  { id: "roth", name: "Challenge Roth", place: "Рот, Германия", month: 7, profile: "холмистая умеренно", fast: true, water: "канал, ~21°C", air: "20–30°C", note: "не бренд Ironman, легендарная атмосфера, быстрые времена" },
  { id: "hamburg", name: "IRONMAN Hamburg", place: "Гамбург, Германия", month: 6, profile: "плоская", fast: true, water: "озеро Альстер, ~20°C", air: "18–24°C", note: "город, плоский велоэтап" },
  { id: "copenhagen", name: "IRONMAN Copenhagen", place: "Копенгаген, Дания", month: 8, profile: "плоская", fast: true, water: "море, ~18°C", air: "18–22°C", note: "ветер на велоэтапе" },
  { id: "kalmar", name: "IRONMAN Kalmar", place: "Кальмар, Швеция", month: 8, profile: "плоская", fast: true, water: "море, ~18°C", air: "17–22°C", note: "прохладно, бывает ветер" },
  { id: "tallinn", name: "IRONMAN Tallinn", place: "Таллин, Эстония", month: 8, profile: "плоская", fast: true, water: "озеро, ~19°C", air: "17–22°C", note: "ближе всего к Москве по логистике" },
  { id: "frankfurt", name: "IRONMAN Frankfurt", place: "Франкфурт, Германия", month: 7, profile: "холмистая умеренно", fast: false, water: "озеро, ~22°C", air: "22–32°C", note: "часто жара" },
  { id: "vitoria", name: "IRONMAN Vitoria-Gasteiz", place: "Витория, Испания", month: 7, profile: "холмистая умеренно", fast: false, water: "водохранилище, ~21°C", air: "18–28°C", note: "" },
  { id: "cascais", name: "IRONMAN Portugal Cascais", place: "Кашкайш, Португалия", month: 10, profile: "холмистая умеренно", fast: false, water: "океан, ~18°C", air: "18–24°C", note: "океанская волна" },
  { id: "wales", name: "IRONMAN Wales", place: "Тенби, Уэльс", month: 9, profile: "очень холмистая", fast: false, water: "море, ~16°C", air: "14–18°C", note: "одна из самых тяжёлых трасс" },
  { id: "lanzarote", name: "IRONMAN Lanzarote", place: "Лансароте, Испания", month: 5, profile: "очень холмистая", fast: false, water: "океан, ~19°C", air: "22–28°C", note: "ветер и жара, очень тяжёлая" },
  { id: "cozumel", name: "IRONMAN Cozumel", place: "Косумель, Мексика", month: 11, profile: "плоская", fast: false, water: "море, ~28°C (без гидрокостюма)", air: "28–32°C", note: "жара и влажность" },
];
const MONTHS_FULL = ["январь", "февраль", "март", "апрель", "май", "июнь", "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь"];

async function renderRace(el, tabs) {
  const [race, gsum, st] = await Promise.all([api("race"), api("goals"), api("status")]);
  const weight = st.thresholds?.weight || 70;
  el.innerHTML = `
    <div class="page-head"><div><h1>Гонка</h1><div class="sub">выбор старта и план питания</div></div>${tabs}</div>
    <div class="today-grid">
      <div class="card"><div class="card-h"><h3>${icon("flag")}Выбор старта</h3><span class="meta">даты на 2028 год уточняйте на ironman.com</span></div>
        <div class="race-list-pick">${RACES.map((r) => `<button class="race-pick ${race.id === r.id ? "on" : ""}" data-id="${r.id}">
          <div><b>${esc(r.name)}</b>${r.fast ? `<span class="pill fast">быстрая</span>` : ""}</div>
          <span class="muted">${esc(r.place)} · ${MONTHS_FULL[r.month - 1]} · ${esc(r.profile)}</span>
          <span class="muted" style="font-size:12px">вода: ${esc(r.water)} · воздух ${esc(r.air)}${r.note ? " · " + esc(r.note) : ""}</span></button>`).join("")}</div></div>
      <div class="stack">
        <div class="card athlete-only"><div class="card-h"><h3>${icon("target")}Мой старт</h3></div>
          <form id="race-form" class="goal-form">
            <label><span>Название</span><input name="name" value="${esc(race.name)}" style="grid-column:span 2"></label>
            <label><span>Дата</span><input name="date" type="date" value="${race.date}"></label>
            <label><span>Место</span><input name="location" value="${esc(race.location || "")}" style="grid-column:span 2"></label>
            <input type="hidden" name="id" value="${esc(race.id || "")}">
            <button class="btn primary" type="submit">Сохранить старт</button>
          </form>
          <div class="muted" style="font-size:12.5px;margin-top:10px">Выберите старт слева — подставятся название и примерная дата. Дата влияет на отсчёт, фазы подготовки и ориентиры CTL.</div></div>
        <div class="card"><div class="card-h"><h3>${icon("bolt")}Для цели 10:00</h3></div>
          <div class="muted" style="font-size:13px">Быстрее всего — плоские трассы с прохладной погодой: Emilia-Romagna, Barcelona, Roth, Hamburg, Копенгаген, Кальмар, Таллин.
            Холмистые и жаркие (Lanzarote, Wales, Cozumel) добавляют 30–90 минут к тому же уровню подготовки.</div></div>
      </div>
    </div>

    <div class="card section"><div class="card-h"><h3>${icon("bolt")}Калькулятор питания на гонке</h3><span class="meta">ориентир, отрабатывается на длинных тренировках</span></div>
      <form id="fuel" class="fuel-form">
        <label>Вес, кг<input name="w" type="number" step="0.5" value="${weight}"></label>
        <label>Велоэтап, ч:мм<input name="bike" value="${hm(gsum.goals.bike)}"></label>
        <label>Бег, ч:мм<input name="run" value="${hm(gsum.goals.run)}"></label>
        <label>Углеводы на вело, г/ч<input name="cb" type="number" value="80"></label>
        <label>Углеводы на беге, г/ч<input name="cr" type="number" value="60"></label>
        <label>Потоотделение, л/ч<input name="sw" type="number" step="0.1" value="0.8"></label>
        <label>Натрий, мг на литр пота<input name="na" type="number" step="50" value="800"></label>
        <label>Углеводов в геле, г<input name="gel" type="number" value="25"></label>
      </form>
      <div id="fuel-out"></div>
    </div>`;
  document.querySelectorAll(".race-pick").forEach((b) => (b.onclick = () => {
    const r = RACES.find((x) => x.id === b.dataset.id), f = $("#race-form"); if (!f) return;
    document.querySelectorAll(".race-pick").forEach((x) => x.classList.toggle("on", x === b));
    f.name.value = r.name; f.location.value = r.place; f.id.value = r.id;
    const y = (f.date.value || "2028").slice(0, 4);
    f.date.value = `${y}-${String(r.month).padStart(2, "0")}-${r.month === 9 ? "20" : "15"}`;
  }));
  const rf = $("#race-form");
  if (rf) rf.onsubmit = async (e) => { e.preventDefault();
    await api("race", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(Object.fromEntries(new FormData(rf))) });
    toast("Старт сохранён"); syncInfo(); renderGoal(); };
  const ff = $("#fuel");
  const calc = () => {
    const v = Object.fromEntries([...new FormData(ff)].map(([k, x]) => [k, k === "bike" || k === "run" ? (parseHMS(x) || 0) / 3600 : +x]));
    const leg = (h, carbs) => ({ h, carbs: Math.round(carbs * h), fluid: +(v.sw * h).toFixed(1), na: Math.round(v.sw * h * v.na), gels: Math.ceil((carbs * h) / v.gel) });
    const b = leg(v.bike, v.cb), r = leg(v.run, v.cr);
    $("#fuel-out").innerHTML = `
      <div class="grid g3" style="margin-top:6px">
        <div class="fuel-card"><div class="src-tag">Накануне и утром</div>
          <div>Загрузка углеводами за 2 дня: <b>${Math.round(v.w * 8)}–${Math.round(v.w * 10)} г/день</b> (8–10 г/кг)</div>
          <div>Завтрак за 3 часа до старта: <b>${Math.round(v.w * 2)}–${Math.round(v.w * 3)} г углеводов</b>, 500 мл воды</div>
          <div>За 15 мин до старта: 1 гель</div></div>
        <div class="fuel-card" style="--c:var(--bike)"><div class="src-tag">Велоэтап · ${hm(v.bike * 3600)}</div>
          <div>Углеводы: <b>${b.carbs} г</b> (${v.cb} г/ч) ≈ ${b.gels} гелей или гели + батончики + изотоник</div>
          <div>Жидкость: <b>${b.fluid} л</b> ≈ ${Math.ceil(b.fluid / 0.75)} фляг по 750 мл</div>
          <div>Натрий: <b>${b.na} мг</b> (${Math.round(v.sw * v.na)} мг/ч)</div>
          <div class="muted">Каждые 20 мин: ${Math.round(v.cb / 3)} г углеводов и ${Math.round((v.sw * 1000) / 3)} мл</div></div>
        <div class="fuel-card" style="--c:var(--run)"><div class="src-tag">Бег · ${hm(v.run * 3600)}</div>
          <div>Углеводы: <b>${r.carbs} г</b> (${v.cr} г/ч) ≈ ${r.gels} гелей или гели + кола на пунктах</div>
          <div>Жидкость: <b>${r.fluid} л</b> — по 150–250 мл на каждом пункте</div>
          <div>Натрий: <b>${r.na} мг</b></div>
          <div class="muted">Каждые 20–25 мин: гель и вода на пункте питания</div></div>
      </div>
      <div class="muted" style="font-size:12.5px;margin-top:12px">Больше 60 г/ч усваивается только при смеси глюкозы и фруктозы и после тренировки кишечника:
        начинайте с 60 г/ч на длинных тренировках и поднимайте на 10 г/ч каждые 2–3 недели. Потоотделение измерьте: вес до и после часа тренировки + выпитое.</div>`;
  };
  ff.oninput = calc; calc();
}

// ---------- Снаряжение ----------
async function renderGear(el, tabs) {
  const g = await api("gear");
  el.innerHTML = `
    <div class="page-head"><div><h1>Снаряжение</h1><div class="sub">из Garmin Connect${g.updated ? ` · обновлено ${g.updated}` : ""}</div></div>${tabs}</div>
    <div class="grid g3 section">${(g.items || []).map((it) => { const sport = it.type === "Shoes" ? "run" : it.type === "Bike" ? "bike" : "other";
      const pct = it.max_m ? Math.min(100, (it.distance_m / it.max_m) * 100) : null;
      return `<div class="card" style="--c:${sportColor(sport)}"><div class="card-h"><h3><span class="sport-badge sm">${icon(sport)}</span>${esc(it.name || "Без названия")}</h3>
          <span class="meta">${it.type === "Shoes" ? "кроссовки" : it.type === "Bike" ? "велосипед" : esc(it.type || "")}</span></div>
        <div class="mini-stats"><div class="stat"><div class="label">Пробег</div><div class="value num">${n0((it.distance_m || 0) / 1000)}<small>км</small></div>
          <div class="delta">${it.activities || 0} трен.${it.estimated ? " · оценка" : ""}</div></div>
          <div class="stat"><div class="label">С даты</div><div class="value" style="font-size:16px">${it.since ? fmtShort(it.since) + " " + it.since.slice(0, 4) : "—"}</div></div></div>
        ${pct != null ? `<div class="divider"></div>${progressRow(it.type === "Shoes" ? "Ресурс кроссовок" : "До обслуживания", it.distance_m || 0, it.max_m, (m) => n0(m / 1000) + " км")}
          ${pct >= 90 ? `<div class="t-bad" style="font-size:12.5px">Пора менять или обслуживать</div>` : ""}` : ""}
      </div>`; }).join("") || `<div class="card muted">В Garmin Connect нет снаряжения</div>`}</div>
    <div class="muted" style="font-size:12.5px">«Оценка» — Garmin не знает, в каких тренировках использовалось снаряжение, поэтому пробег посчитан по всем пробежкам (кроссовки) и заездам
      (велосипед) с даты добавления. Точнее будет, если назначать снаряжение тренировкам в Garmin Connect; новые кроссовки добавляйте там же.</div>`;
}

// ---------- недельный отчёт (печать / PDF) ----------
async function renderReport() {
  const wk = location.hash.split("/")[1] || iso(mondayOf(new Date()));
  const r = await api(`report?week=${wk}`);
  const el = $("#view-report");
  const sports = ["swim", "bike", "run", "strength", "hockey", "football", "other"].filter((k) => r.by_sport[k]);
  const pct = (a, b) => (b ? Math.round((a / b) * 100) + "%" : "—");
  el.innerHTML = `
    <div class="report">
      <div class="report-head"><div><div class="muted">Недельный отчёт · ${esc(r.race.name)}</div>
        <h1>${fmtShort(r.week)} – ${fmtShort(r.end)} ${r.end.slice(0, 4)}</h1></div>
        <div class="no-print" style="display:flex;gap:8px"><a class="btn" href="#report/${iso(addDays(parseD(r.week), -7))}">←</a>
          <a class="btn" href="#report/${iso(addDays(parseD(r.week), 7))}">→</a>
          <button class="btn primary" onclick="window.print()">${icon("print")}Печать / PDF</button></div></div>
      <div class="kpis">
        <div class="card stat"><div class="label">Выполнено тренировок</div><div class="value num">${r.done}<small>из ${r.planned}</small></div></div>
        <div class="card stat"><div class="label">Фитнес CTL</div><div class="value num">${r.ctl.end != null ? Math.round(r.ctl.end) : "—"}</div>
          <div class="delta">${r.ctl.start != null && r.ctl.end != null ? `${r.ctl.end - r.ctl.start >= 0 ? "+" : ""}${(r.ctl.end - r.ctl.start).toFixed(1)} за неделю` : ""}</div></div>
        <div class="card stat"><div class="label">Сон в среднем</div><div class="value num">${r.health.sleep_h ?? "—"}<small>ч</small></div>
          <div class="delta">HRV ${r.health.hrv ?? "—"} · пульс покоя ${r.health.rhr ?? "—"}</div></div>
        <div class="card stat"><div class="label">Отбой до 23:00</div><div class="value num">${r.regime.on_time}<small>из ${r.regime.nights}</small></div>
          <div class="delta">средний отбой ${r.regime.avg_bed || "—"}</div></div>
      </div>
      <div class="card section"><div class="card-h"><h3>По видам спорта</h3></div><div class="table-wrap"><table class="data num">
        <thead><tr><th>Вид</th><th>План, ч</th><th>Факт, ч</th><th>%</th><th>План, км</th><th>Факт, км</th><th>TSS план</th><th>TSS факт</th></tr></thead><tbody>
        ${sports.map((k) => { const b = r.by_sport[k]; return `<tr><td><span class="sport-cell" style="--c:${sportColor(k)}">${SPORT[k]?.ico || ""}${SPORT[k]?.name || k}</span></td>
          <td>${hrs(b.plan_s)}</td><td>${hrs(b.fact_s)}</td><td>${pct(b.fact_s, b.plan_s)}</td><td>${b.plan_m ? km(b.plan_m, k) : "—"}</td><td>${b.fact_m ? km(b.fact_m, k) : "—"}</td>
          <td>${n0(b.plan_tss)}</td><td>${n0(b.fact_tss)}</td></tr>`; }).join("")}</tbody></table></div></div>
      <div class="card section">${weekLanes(keyRows(r.days))}<div style="margin-top:12px">${lanesLegend()}</div></div>
      <div class="grid g2 section">
        <div class="card"><div class="card-h"><h3>Пропущено</h3></div>${r.missed.length ? r.missed.map((m) => `<div class="milestone">${icon(m.sport)}<span>${fmtShort(m.date)} · ${esc(m.title || "")}</span></div>`).join("") : `<div class="muted">Нет</div>`}</div>
        <div class="card"><div class="card-h"><h3>Вне плана</h3></div>${r.unplanned.length ? r.unplanned.map((m) => `<div class="milestone">${icon(m.sport)}<span>${fmtShort(m.date)} · ${esc(m.title || "")}</span></div>`).join("") : `<div class="muted">Нет</div>`}</div>
      </div>
      ${r.comments.length ? `<div class="card section"><div class="card-h"><h3>Комментарии за неделю</h3></div>${r.comments.map((c) => `<div class="cmt ${c.role}"><div class="cmt-h"><b>${esc(c.author_name)}</b><span class="muted">${fmtShort(c.date)}</span></div><div>${esc(c.text)}</div></div>`).join("")}</div>` : ""}
    </div>`;
  requestAnimationFrame(drawArrows);
}

// ---------- Старты: календарь соревнований ----------
const RSPORT = { run: ["Бег", "var(--run)", "run"], trail: ["Трейл", "var(--strength)", "trail"], bike: ["Вело", "var(--bike)", "bike"],
  swim: ["Открытая вода", "var(--swim)", "swim"], tri: ["Триатлон", "var(--hockey)", "tri"] };
const RREGION = [["ru", "Россия"], ["moscow", "Москва и МО"], ["abroad", "За рубежом"], ["online", "Онлайн"], ["all", "Все"]];
const RPERIOD = [[1, "месяц"], [3, "3 мес"], [6, "полгода"], [12, "год"], [0, "всё"]];
const RDIST = [["any", "любая"], ["short", "до 10 км"], ["half", "10–21 км"], ["mar", "марафон 42"], ["ultra", "ультра 50+"]];
const DOWS = ["вс", "пн", "вт", "ср", "чт", "пт", "сб"];
let RC = null;
const rcState = (() => { const def = { view: "list", sports: Object.keys(RSPORT), region: "ru", period: 6, dist: "any", q: "", mine: false, month: null };
  try { return { ...def, ...JSON.parse(localStorage.getItem("rc_state") || "{}") }; } catch { return def; } })();
const rcSave = () => { try { localStorage.setItem("rc_state", JSON.stringify(rcState)); } catch {} };

function rcFilter(evs) {
  const today = iso(new Date());
  const lim = rcState.period ? iso(addDays(new Date(), rcState.period * 30.5)) : "9999";
  const q = rcState.q.trim().toLowerCase();
  return evs.filter((e) => {
    if (!rcState.sports.includes(e.sport)) return false;
    if (rcState.region === "ru" && !(e.region === "russia" || e.region === "moscow")) return false;
    if (!["ru", "all"].includes(rcState.region) && e.region !== rcState.region) return false;
    if (rcState.region !== "online" && rcState.region !== "all" && e.online) return false;
    if ((e.end || e.start) < today || e.start > lim) return false;
    if (rcState.mine && !e.marked) return false;
    const km = e.km || [], mx = Math.max(0, ...km);
    if (rcState.dist === "short" && !km.some((k) => k <= 10)) return false;
    if (rcState.dist === "half" && !km.some((k) => k > 10 && k <= 21.2)) return false;
    if (rcState.dist === "mar" && !km.some((k) => k >= 42 && k <= 43)) return false;
    if (rcState.dist === "ultra" && mx < 50) return false;
    if (q && !`${e.name} ${e.city}`.toLowerCase().includes(q)) return false;
    return true;
  });
}
const fmtKm = (k, sport) => (k < 1 ? `${Math.round(k * 1000)} м` : k === 21.1 || k === 21.097 ? "21,1" : k === 42.2 || k === 42.195 ? "42,2" : String(+k.toFixed(1)).replace(".", ","));
function rcLinks(e, small) {
  const L = [];
  if (e.reg) L.push(`<a class="rc-link primary" href="${esc(e.reg)}" target="_blank" rel="noopener">Регистрация</a>`);
  if (e.site) L.push(`<a class="rc-link" href="${esc(e.site)}" target="_blank" rel="noopener">Сайт</a>`);
  for (const [s, u] of Object.entries(e.links || {})) if (u && u !== e.reg) L.push(`<a class="rc-link src" href="${esc(u)}" target="_blank" rel="noopener">${esc(RC.source_names[s] || s)}</a>`);
  return `<div class="rc-links">${L.join("")}</div>`;
}
function rcCard(e) {
  const d = parseD(e.start), [nm, col, ic] = RSPORT[e.sport] || RSPORT.run;
  const range = e.end && e.end !== e.start ? `–${parseD(e.end).getDate()}${parseD(e.end).getMonth() !== d.getMonth() ? " " + MONTHS[parseD(e.end).getMonth()] : ""}` : "";
  return `<div class="rc-card" style="--c:${col}">
    <div class="rc-date"><b>${d.getDate()}${range}</b><span>${MONTHS[d.getMonth()]} · ${DOWS[d.getDay()]}</span></div>
    <div class="rc-main"><div class="rc-title"><span class="rc-ico">${icon(ic)}</span>${esc(e.name)}</div>
      <div class="rc-meta">${esc(e.city || "место уточняется")}${e.online ? " · онлайн" : ""} · ${nm}</div>
      ${e.km?.length ? `<div class="rc-km">${e.km.slice(0, 8).map((k) => `<span>${fmtKm(k, e.sport)}${k >= 1 ? " км" : ""}</span>`).join("")}</div>` : ""}
      ${rcLinks(e)}</div>
    <button class="rc-star ${e.marked ? "on" : ""} athlete-only" title="${e.marked ? "Убрать из моих" : "Хочу участвовать"}" onclick="rcMark('${e.id}', this)">${icon("star")}</button>
  </div>`;
}
async function rcMark(id, btn) {
  const r = await api(`race-calendar/mark/${id}`, { method: "POST" });
  const e = RC.events.find((x) => x.id === id); if (e) e.marked = r.marked;
  btn.classList.toggle("on", r.marked); toast(r.marked ? "Добавлено в мои старты" : "Убрано из моих стартов");
}

async function renderRaces() {
  RC = await api("race-calendar");
  const el = $("#view-races");
  const draw = () => {
    const list = rcFilter(RC.events);
    const cnt = (sp) => rcFilter(RC.events.map((e) => e)).filter((e) => e.sport === sp).length;
    const srcOk = RC.sources.filter((s) => s.ok).length;
    el.innerHTML = `
      <div class="page-head"><div><h1>Старты</h1>
        <div class="sub">${RC.events.length} событий из ${srcOk} источников${RC.updated ? ` · обновлено ${esc(RC.updated)}` : ""}${RC.refreshing ? " · идёт обновление…" : ""}</div></div>
        <div style="display:flex;gap:8px;flex-wrap:wrap">
          <div class="seg">${[["list", "Список"], ["cal", "Календарь"], ["map", "Карта"]].map(([k, l]) => `<button data-v="${k}" class="${rcState.view === k ? "on" : ""}">${l}</button>`).join("")}</div>
          <button class="btn athlete-only" id="rc-refresh" ${RC.refreshing ? "disabled" : ""}>${icon("refresh")}Обновить</button></div></div>
      <div class="card rc-filters">
        <div class="rc-sports">${Object.entries(RSPORT).map(([k, [nm, col, ic]]) => `<button class="rc-chip ${rcState.sports.includes(k) ? "on" : ""}" data-s="${k}" style="--c:${col}">${icon(ic)}${nm}</button>`).join("")}</div>
        <div class="rc-row">
          <select id="rc-region">${RREGION.map(([k, l]) => `<option value="${k}" ${rcState.region === k ? "selected" : ""}>${l}</option>`).join("")}</select>
          <select id="rc-period">${RPERIOD.map(([k, l]) => `<option value="${k}" ${rcState.period == k ? "selected" : ""}>${l}</option>`).join("")}</select>
          <select id="rc-dist">${RDIST.map(([k, l]) => `<option value="${k}" ${rcState.dist === k ? "selected" : ""}>Дистанция: ${l}</option>`).join("")}</select>
          <input id="rc-q" placeholder="Поиск: название или город" value="${esc(rcState.q)}">
          <label class="rc-mine athlete-only"><input type="checkbox" id="rc-mine" ${rcState.mine ? "checked" : ""}> ${icon("star")}мои</label>
          <span class="muted num">${list.length} найдено</span>
        </div>
      </div>
      <div id="rc-body"></div>
      <div class="muted rc-src">Источники: ${RC.sources.map((s) => `<span class="${s.ok ? "" : "t-bad"}" title="${esc(s.message)} · ${esc(s.updated)}">${esc(RC.source_names[s.source] || s.source)} ${s.ok ? s.count : "✗"}</span>`).join(" · ")}.
        Дубли с разных сайтов объединены; даты и регистрацию проверяйте на сайте старта.</div>`;
    el.querySelectorAll(".seg button[data-v]").forEach((b) => (b.onclick = () => { rcState.view = b.dataset.v; rcSave(); draw(); }));
    el.querySelectorAll(".rc-chip").forEach((b) => (b.onclick = () => { const s = b.dataset.s;
      rcState.sports = rcState.sports.includes(s) ? rcState.sports.filter((x) => x !== s) : [...rcState.sports, s]; rcSave(); draw(); }));
    $("#rc-region").onchange = (e) => { rcState.region = e.target.value; rcSave(); draw(); };
    $("#rc-period").onchange = (e) => { rcState.period = +e.target.value; rcSave(); draw(); };
    $("#rc-dist").onchange = (e) => { rcState.dist = e.target.value; rcSave(); draw(); };
    const mine = $("#rc-mine"); if (mine) mine.onchange = (e) => { rcState.mine = e.target.checked; rcSave(); draw(); };
    let qt; $("#rc-q").oninput = (e) => { clearTimeout(qt); qt = setTimeout(() => { rcState.q = e.target.value; rcSave(); const p = e.target.selectionStart; draw(); const q = $("#rc-q"); q.focus(); q.setSelectionRange(p, p); }, 250); };
    const rb = $("#rc-refresh"); if (rb) rb.onclick = async () => { await api("race-calendar/refresh", { method: "POST" });
      toast("Обновление запущено — занимает 10–15 минут, можно закрыть страницу"); rb.disabled = true; };
    const body = $("#rc-body");
    if (rcState.view === "list") rcList(body, list);
    else if (rcState.view === "cal") rcCalendar(body, list, draw);
    else rcMap(body, list);
  };
  draw();
}

function rcList(body, list) {
  if (!list.length) { body.innerHTML = `<div class="card empty">Ничего не нашлось — ослабьте фильтры</div>`; return; }
  const byM = {};
  list.forEach((e) => (byM[e.start.slice(0, 7)] ||= []).push(e));
  body.innerHTML = Object.entries(byM).map(([m, evs]) => `<div class="rc-month"><h2>${MONTHS_FULL[+m.slice(5) - 1]} ${m.slice(0, 4)} <span class="muted">· ${evs.length}</span></h2>
    <div class="card rc-list">${evs.slice(0, 300).map(rcCard).join("")}</div></div>`).join("");
}

function rcCalendar(body, list, redraw) {
  const now = new Date();
  const m0 = rcState.month ? parseD(rcState.month + "-01") : new Date(now.getFullYear(), now.getMonth(), 1);
  const y = m0.getFullYear(), mo = m0.getMonth();
  const first = new Date(y, mo, 1), startOff = (first.getDay() + 6) % 7, days = new Date(y, mo + 1, 0).getDate();
  const byD = {};
  list.forEach((e) => { const a = parseD(e.start), b = parseD(e.end || e.start);
    for (let d = new Date(a); d <= b && d - a < 7 * 864e5; d = addDays(d, 1)) (byD[iso(d)] ||= []).push(e); });
  const cells = [];
  for (let i = 0; i < startOff; i++) cells.push(`<div class="rc-day empty"></div>`);
  for (let d = 1; d <= days; d++) {
    const k = iso(new Date(y, mo, d)), evs = byD[k] || [];
    cells.push(`<div class="rc-day ${k === iso(now) ? "today" : ""} ${evs.length ? "has" : ""}" data-d="${k}"><div class="rc-dn">${d}</div>
      ${evs.slice(0, 3).map((e) => `<div class="rc-ev" style="--c:${RSPORT[e.sport]?.[1]}">${esc(e.name)}</div>`).join("")}
      ${evs.length > 3 ? `<div class="rc-more">+${evs.length - 3}</div>` : ""}</div>`);
  }
  const prev = iso(new Date(y, mo - 1, 1)).slice(0, 7), next = iso(new Date(y, mo + 1, 1)).slice(0, 7);
  body.innerHTML = `<div class="card"><div class="cal-nav" style="margin-bottom:12px">
      <button class="btn" data-m="${prev}">←</button><span class="range">${MONTHS_FULL[mo]} ${y}</span><button class="btn" data-m="${next}">→</button>
      <span class="muted" style="margin-left:auto">${Object.keys(byD).filter((k) => k.startsWith(`${y}-${String(mo + 1).padStart(2, "0")}`)).length} дней со стартами</span></div>
    <div class="rc-grid">${["пн", "вт", "ср", "чт", "пт", "сб", "вс"].map((d) => `<div class="rc-wd">${d}</div>`).join("")}${cells.join("")}</div></div>
    <div id="rc-daylist"></div>`;
  body.querySelectorAll("[data-m]").forEach((b) => (b.onclick = () => { rcState.month = b.dataset.m; rcSave(); redraw(); }));
  body.querySelectorAll(".rc-day.has").forEach((c) => (c.onclick = () => {
    body.querySelectorAll(".rc-day.sel").forEach((x) => x.classList.remove("sel")); c.classList.add("sel");
    const evs = byD[c.dataset.d] || [];
    $("#rc-daylist").innerHTML = `<h2>${fmtDay(c.dataset.d)} · ${evs.length}</h2><div class="card rc-list">${evs.map(rcCard).join("")}</div>`;
    $("#rc-daylist").scrollIntoView({ behavior: "smooth", block: "start" });
  }));
}

let _cluster;
function loadCluster() {
  if (window.L?.markerClusterGroup) return Promise.resolve();
  return (_cluster ||= loadLeaflet().then(() => new Promise((ok, fail) => {
    for (const f of ["MarkerCluster.min.css", "MarkerCluster.Default.min.css"]) { const l = document.createElement("link"); l.rel = "stylesheet";
      l.href = `https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.3/${f}`; document.head.append(l); }
    const sc = document.createElement("script"); sc.src = "https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.3/leaflet.markercluster.min.js";
    sc.onload = ok; sc.onerror = fail; document.head.append(sc);
  })));
}
async function rcMap(body, list) {
  const pts = list.filter((e) => e.lat && e.lon);
  body.innerHTML = `<div class="card"><div class="map rc-map" id="rc-map"></div>
    <div class="legend" style="margin-top:10px">${Object.values(RSPORT).map(([nm, col]) => `<span><i class="sw" style="background:${col};border-radius:50%"></i>${nm}</span>`).join("")}
      <span class="muted">· на карте ${pts.length} из ${list.length}${pts.length < list.length ? " (у остальных не удалось определить место)" : ""}</span></div></div>`;
  await loadCluster();
  const m = baseMap($("#rc-map"));
  m.scrollWheelZoom.enable();
  const cl = L.markerClusterGroup({ showCoverageOnHover: false, maxClusterRadius: 45 });
  pts.forEach((e) => {
    const col = css(RSPORT[e.sport]?.[1].slice(4, -1) || "--run");
    const mk = L.circleMarker([e.lat, e.lon], { radius: 7, color: "#fff", weight: 2, fillColor: col, fillOpacity: 0.95 });
    mk.bindPopup(`<div class="rc-pop"><b>${esc(e.name)}</b><div>${fmtShort(e.start)} ${e.start.slice(0, 4)} · ${esc(e.city || "")}</div>
      ${e.km?.length ? `<div>${e.km.slice(0, 6).map((k) => fmtKm(k) + (k >= 1 ? " км" : "")).join(" · ")}</div>` : ""}${rcLinks(e)}</div>`, { maxWidth: 280 });
    cl.addLayer(mk);
  });
  m.addLayer(cl);
  const ru = pts.filter((e) => e.region !== "abroad");
  if (ru.length) m.fitBounds(L.latLngBounds((ru.length > 3 ? ru : pts).map((e) => [e.lat, e.lon])), { padding: [24, 24], maxZoom: 9 });
  else m.setView([55.75, 37.6], 5);
}

// ---------- Нагрузка ----------
let loadDays = 180;
async function renderLoad() {
  const [fit, vol] = await Promise.all([api(`fitness?days=${loadDays}&forward=21`), api("volume?weeks=16")]);
  const el = $("#view-load");
  el.innerHTML = `
    <div class="page-head"><div><h1>Нагрузка</h1><div class="sub">форма, усталость и объёмы по неделям</div></div>
      <div class="seg">${[[42, "6 нед"], [90, "3 мес"], [180, "6 мес"], [365, "год"]].map(([d, l]) => `<button data-d="${d}" class="${d === loadDays ? "on" : ""}">${l}</button>`).join("")}</div></div>
    <div class="card chart-card"><h3>Фитнес (CTL) и усталость (ATL)</h3>
      <div class="sub">Пунктир — прогноз по плану тренера на 3 недели вперёд</div>
      <div class="chart-box"><canvas id="c-fit"></canvas></div></div>
    <div class="card chart-card" style="margin-top:12px"><h3>Свежесть (TSB)</h3>
      <div class="sub">Ниже −30 — риск перетренированности, +5…+25 — свежесть перед стартом</div>
      <div class="chart-box sm"><canvas id="c-tsb"></canvas></div></div>
    <h2>Объём по неделям</h2>
    <div class="card chart-card"><h3>Часы: факт по видам спорта и план</h3>
      <div class="sub">Столбцы — выполнено, линия — сколько поставил тренер</div>
      <div class="chart-box"><canvas id="c-vol"></canvas></div></div>
    <div class="card chart-card" style="margin-top:12px"><h3>Выполнение плана по TSS</h3>
      <div class="sub">Факт / план за неделю, %. Зелёная зона 80–120 %</div>
      <div class="chart-box sm"><canvas id="c-comp"></canvas></div></div>`;
  el.querySelectorAll(".seg button").forEach((b) => (b.onclick = () => { loadDays = +b.dataset.d; renderLoad(); }));

  const labels = fit.map((d) => fmtShort(d.date));
  const todayIdx = fit.findIndex((d) => d.future) - 1;
  const seg = { borderDash: (c) => (c.p0DataIndex >= todayIdx && todayIdx >= 0 ? [5, 4] : undefined) };
  mkChart("c-fit", {
    type: "line",
    data: { labels, datasets: [
      lineDs("Фитнес (CTL)", fit.map((d) => d.ctl), css("--s1"), { segment: seg }),
      lineDs("Усталость (ATL)", fit.map((d) => d.atl), css("--s2"), { segment: seg }),
    ] },
    options: timeOpts(),
  });
  mkChart("c-tsb", {
    type: "bar",
    data: { labels, datasets: [{ label: "TSB", data: fit.map((d) => d.tsb), borderRadius: 2, borderSkipped: false,
      backgroundColor: fit.map((d) => (d.future ? css("--axis") : d.tsb < -30 ? css("--critical") : css("--s3"))) }] },
    options: timeOpts({ legend: false }),
  });

  const wl = vol.map((w) => fmtShort(w.week));
  const sports = ["swim", "bike", "run", "strength"];
  mkChart("c-vol", {
    data: { labels: wl, datasets: [
      ...sports.map((s) => ({ type: "bar", label: SPORT[s].name, data: vol.map((w) => +(w.actual[s] || 0).toFixed(1)),
        backgroundColor: css("--" + s), stack: "a", borderRadius: 3, borderColor: css("--surface"), borderWidth: { top: 2 }, maxBarThickness: 34 })),
      { type: "line", label: "План, всего", data: vol.map((w) => +Object.values(w.plan).reduce((a, b) => a + b, 0).toFixed(1)),
        borderColor: css("--ink-2"), backgroundColor: css("--ink-2"), borderWidth: 2, borderDash: [4, 3], pointRadius: 3, pointStyle: "line" },
    ] },
    options: { ...timeOpts({ y: { title: { display: true, text: "часы" } } }),
      scales: { x: { stacked: true, grid: { display: false } }, y: { stacked: true, grid: { color: css("--grid") }, border: { display: false }, title: { display: true, text: "часы" } } } },
  });
  mkChart("c-comp", {
    type: "bar",
    data: { labels: wl, datasets: [{ label: "Выполнение, %", borderRadius: 3, maxBarThickness: 34,
      data: vol.map((w) => (w.plan_tss ? Math.round((w.actual_tss / w.plan_tss) * 100) : null)),
      backgroundColor: vol.map((w) => { const p = w.plan_tss ? (w.actual_tss / w.plan_tss) * 100 : 0;
        return p >= 80 && p <= 120 ? css("--good") : p >= 50 ? css("--warning") : css("--serious"); }) }] },
    options: timeOpts({ legend: false, y: { suggestedMax: 120 } }),
  });
}

// ---------- Здоровье ----------
let healthDays = 60, healthTable = false;
async function renderHealth() {
  const [h, reg, si, wt, rdy, rh] = await Promise.all([api(`health?days=${healthDays}`), api(`regime?days=${healthDays}`), api("sleep-impact"), api("weight"),
    api("readiness").catch(() => null), api("readiness/history?days=30").catch(() => [])]);
  const el = $("#view-health");
  const labels = h.map((d) => fmtShort(d.date));
  const get = (src, k, f = (v) => v) => h.map((d) => (d[src]?.[k] != null ? f(d[src][k]) : null));
  const rs = (await api("status")).recovery_source || "fitbit";
  const both = (k, f) => [lineDs(SRC[rs], get(rs, k, f), css("--s1"))];
  el.innerHTML = `
    <div class="page-head"><div><h1>Здоровье</h1><div class="sub">сон, режим, HRV и пульс покоя</div></div>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <div class="seg">${[[30, "30 дн"], [60, "60 дн"], [180, "6 мес"]].map(([d, l]) => `<button data-d="${d}" class="${d === healthDays ? "on" : ""}">${l}</button>`).join("")}</div>
        <div class="seg"><button id="h-chart" class="${healthTable ? "" : "on"}">График</button><button id="h-table" class="${healthTable ? "on" : ""}">Таблица</button></div>
      </div></div>
    ${healthTable ? `<div class="card table-wrap"><table class="data num"><thead><tr><th>Дата</th>
        <th>Сон, ч</th><th>Глубокий</th><th>REM</th><th>HRV</th><th>Пульс покоя</th><th>Body Battery</th><th>Готовность</th><th>Шаги</th></tr></thead><tbody>
        ${h.slice().reverse().map((d) => `<tr><td>${fmtShort(d.date)}</td><td>${hrs(d[rs]?.sleep_s)}</td><td>${hrs(d[rs]?.deep_s)}</td><td>${hrs(d[rs]?.rem_s)}</td>
          <td>${n0(d[rs]?.hrv)}</td><td>${n0(d[rs]?.resting_hr)}</td>
          <td>${n0(d.garmin?.body_battery)}</td><td>${n0(d.garmin?.readiness)}</td><td>${n0(d.garmin?.steps ?? d.fitbit?.steps)}</td></tr>`).join("")}
      </tbody></table></div>` : `
    ${rdy ? `<div class="grid g2 charts2 section">
      <div class="card chart-card"><h3>Сегодня: пульс и нагрузка</h3><div class="sub">поминутный пульс Fitbit, пропуски — с часов Garmin · пунктир — границы Z2 и Z4 ·
          ${rdy.hr_stale_min > 60 ? `<b class="t-bad">нет данных с ${rdy.hr_updated || "начала дня"} — устройства не синхронизировались</b>` : `пульс до ${rdy.hr_updated || "—"}`}</div>
        <div class="chart-box sm"><canvas id="c-dayhr"></canvas></div>
        <div class="sub" style="margin:10px 0 6px">накопленная нагрузка за день · зелёная полоса — оптимум ${rdy.target[0]}–${rdy.target[1]}</div>
        <div class="chart-box sm" style="height:120px"><canvas id="c-daystrain"></canvas></div></div>
      <div class="card chart-card"><h3>Восстановление и нагрузка · 30 дней</h3><div class="sub">восстановление, % (зелёная ≥67, жёлтая 34–66, красная &lt;34)</div>
        <div class="chart-box sm"><canvas id="c-rec"></canvas></div>
        <div class="sub" style="margin:10px 0 6px">нагрузка дня, 0–21</div>
        <div class="chart-box sm" style="height:120px"><canvas id="c-strain"></canvas></div></div>
    </div>` : ""}
    <div class="card chart-card" style="margin-bottom:12px"><h3>Режим: время отбоя</h3>
      <div class="sub">МСК · цель — не позже ${reg.target} (пунктир) · вовремя ${reg.nights.filter((n) => n.on_time).length} из ${reg.nights.length} ночей</div>
      <div class="chart-box sm"><canvas id="c-bed"></canvas></div></div>
    <div class="card section"><div class="card-h"><h3>${icon("moon")}Как отбой влияет на восстановление</h3><span class="meta">ваши данные за 4 месяца · утро после ночи</span></div>
      <div class="table-wrap"><table class="data num"><thead><tr><th>Отбой</th><th>Ночей</th><th>HRV утром</th><th>Пульс покоя</th><th>Сон</th></tr></thead><tbody>
      ${si.groups.map((g, i) => { const best = si.groups.filter((x) => x.hrv).reduce((a, x) => Math.max(a, x.hrv), 0);
        return `<tr><td><b>${esc(g.label)}</b></td><td>${g.nights || "—"}</td><td class="${g.hrv && g.hrv === best ? "t-good" : ""}">${g.hrv ?? "—"}${g.hrv ? " мс" : ""}</td>
        <td>${g.rhr ?? "—"}</td><td>${g.sleep != null ? g.sleep + " ч" : "—"}</td></tr>`; }).join("")}</tbody></table></div>
      <div class="muted" style="font-size:12.5px;margin-top:10px">${(() => { const g = si.groups.filter((x) => x.hrv && x.nights >= 2);
        if (g.length < 2) return "Пока мало ночей для выводов — данные копятся.";
        const a = g[0], z = g[g.length - 1];
        return `При отбое «${esc(a.label)}» HRV утром в среднем ${a.hrv} мс, при «${esc(z.label)}» — ${z.hrv} мс (${z.hrv >= a.hrv ? "+" : ""}${Math.round((z.hrv / a.hrv - 1) * 100)}%).
          Пульс покоя ${a.rhr} против ${z.rhr}. Ночей с отбоем до ${reg.target} пока ${si.groups[0].nights} — как только появятся, будет видно разницу.`; })()}</div>
    </div>

    <div class="card section"><div class="card-h"><h3>${icon("scale")}Вес</h3><span class="meta">${wt.rows.length ? `последний ${wt.rows[wt.rows.length - 1].kg} кг` : `в профиле Garmin ${wt.profile} кг`}</span></div>
      ${wt.rows.length >= 2 ? `<div class="chart-box sm"><canvas id="c-wt"></canvas></div>` : `<div class="muted" style="font-size:13px">Взвешиваний пока нет. Вносите вес раз в неделю утром натощак — будет график.</div>`}
      <form id="wt-form" class="cmt-form athlete-only" style="max-width:420px"><input name="date" type="date" value="${iso(new Date())}" style="flex:0 0 150px">
        <input name="kg" type="number" step="0.1" placeholder="кг" value="${wt.rows.length ? wt.rows[wt.rows.length - 1].kg : wt.profile}" style="flex:0 0 90px">
        <button class="btn primary" type="submit">Добавить</button></form>
    </div>

    <div class="grid g2 charts2">
      <div class="card chart-card"><h3>HRV (ночной RMSSD)</h3><div class="sub">мс · выше — лучше восстановление</div><div class="chart-box sm"><canvas id="c-hrv"></canvas></div></div>
      <div class="card chart-card"><h3>Пульс покоя</h3><div class="sub">уд/мин · рост на 5+ — признак усталости или болезни</div><div class="chart-box sm"><canvas id="c-rhr"></canvas></div></div>
      <div class="card chart-card"><h3>Сон</h3><div class="sub">часы за ночь: всего, глубокий, REM</div><div class="chart-box sm"><canvas id="c-sleep"></canvas></div></div>
      <div class="card chart-card"><h3>Body Battery и готовность к тренировке</h3><div class="sub">Garmin, 0–100</div><div class="chart-box sm"><canvas id="c-bb"></canvas></div></div>
    </div>`}`;
  el.querySelectorAll(".seg button[data-d]").forEach((b) => (b.onclick = () => { healthDays = +b.dataset.d; renderHealth(); }));
  $("#h-chart").onclick = () => { healthTable = false; renderHealth(); };
  $("#h-table").onclick = () => { healthTable = true; renderHealth(); };
  const wf = $("#wt-form");
  if (wf) wf.onsubmit = async (e) => { e.preventDefault();
    await api("weight", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ date: wf.date.value, kg: +wf.kg.value }) });
    toast("Вес сохранён"); renderHealth(); };
  if (healthTable) return;
  if (wt.rows.length >= 2) mkChart("c-wt", { type: "line", data: { labels: wt.rows.map((r) => fmtShort(r.date)),
    datasets: [lineDs("Вес, кг", wt.rows.map((r) => r.kg), css("--s1"), { pointRadius: 3 })] }, options: timeOpts({ legend: false }) });
  if (rdy) {
    const lab = Array.from({ length: 1440 }, (_, i) => `${String(Math.floor(i / 60)).padStart(2, "0")}:${String(i % 60).padStart(2, "0")}`);
    const upto = Math.max(rdy.curve.hr.reduce((a, v, i) => (v ? i : a), 0) + 1, Math.min(1440, rdy.now_min + 1));
    const xopt = { grid: { display: false }, ticks: { maxTicksLimit: 9, maxRotation: 0, callback: (v, i) => lab[i]?.endsWith(":00") ? lab[i] : lab[i] } };
    mkChart("c-dayhr", { type: "line", data: { labels: lab.slice(0, upto), datasets: [
      lineDs("Пульс", rdy.curve.hr.slice(0, upto), css("--critical"), { borderWidth: 1.2, tension: 0, spanGaps: 5 }),
      { label: "Z2", data: Array(upto).fill(rdy.z2_floor), borderColor: css("--axis"), borderDash: [4, 4], borderWidth: 1, pointRadius: 0 },
      { label: "Z4", data: Array(upto).fill(rdy.z4_floor), borderColor: css("--axis"), borderDash: [4, 4], borderWidth: 1, pointRadius: 0 },
    ] }, options: { ...timeOpts({ legend: false }), scales: { x: xopt, y: { grid: { color: css("--grid") }, border: { display: false } } } } });
    mkChart("c-daystrain", { type: "line", data: { labels: lab.slice(0, upto), datasets: [
      { label: "Оптимум от", data: Array(upto).fill(rdy.target[0]), borderWidth: 0, pointRadius: 0, fill: false },
      { label: "Оптимум до", data: Array(upto).fill(rdy.target[1]), borderWidth: 0, pointRadius: 0, fill: "-1", backgroundColor: "color-mix(in srgb, " + css("--good") + " 18%, transparent)" },
      lineDs("Нагрузка", rdy.curve.strain.slice(0, upto).map((v, i) => (rdy.curve.hr[i] || i <= (rdy.now_min - rdy.hr_stale_min) ? v : null)), css("--accent"), { tension: 0, spanGaps: false }),
    ] }, options: { ...timeOpts({ legend: false }), scales: { x: xopt, y: { min: 0, max: 21, grid: { color: css("--grid") }, border: { display: false } } } } });
    const rl = rh.map((x) => fmtShort(x.date));
    mkChart("c-rec", { type: "bar", data: { labels: rl, datasets: [{ label: "Восстановление, %", data: rh.map((x) => x.recovery), borderRadius: 3, maxBarThickness: 18,
      backgroundColor: rh.map((x) => (x.zone === "green" ? css("--good") : x.zone === "yellow" ? css("--warning") : css("--critical"))) }] },
      options: timeOpts({ legend: false, y: { min: 0, max: 100 } }) });
    mkChart("c-strain", { type: "bar", data: { labels: rl, datasets: [{ label: "Нагрузка", data: rh.map((x) => x.strain), backgroundColor: css("--accent"), borderRadius: 3, maxBarThickness: 18 }] },
      options: timeOpts({ legend: false, y: { min: 0, max: 21 } }) });
  }
  const nl = reg.nights.map((n) => fmtShort(n.night_of));
  mkChart("c-bed", { type: "bar", data: { labels: nl, datasets: [
    { type: "line", label: `Цель ${reg.target}`, data: nl.map(() => reg.target_min), borderColor: css("--ink-2"), borderWidth: 1.5, borderDash: [5, 4], pointRadius: 0 },
    { label: "Отбой", data: reg.nights.map((n) => [reg.target_min - 120, n.bed_min]), borderRadius: 3, maxBarThickness: 22,
      backgroundColor: reg.nights.map((n) => (n.on_time ? css("--good") : n.late_min <= 30 ? css("--warning") : css("--critical"))) },
  ] }, options: { ...timeOpts({ legend: false }),
    scales: { x: { grid: { display: false } }, y: { min: reg.target_min - 120, suggestedMax: reg.target_min + 180, grid: { color: css("--grid") }, border: { display: false },
      ticks: { stepSize: 60, callback: (v) => fmtMin(v) } } },
    plugins: { legend: { display: false }, tooltip: { callbacks: { label: (c) => {
      if (c.datasetIndex === 0) return `Цель ${reg.target}`;
      const n = reg.nights[c.dataIndex]; return [`Лёг ${n.bed_time}${n.on_time ? " ✓" : ` (+${fmtLate(n.late_min)})`}`, `Встал ${n.wake_time} · сон ${n.sleep_h} ч`]; } } } } } });
  mkChart("c-hrv", { type: "line", data: { labels, datasets: both("hrv") }, options: timeOpts() });
  mkChart("c-rhr", { type: "line", data: { labels, datasets: both("resting_hr") }, options: timeOpts() });
  const h1 = (v) => +(v / 3600).toFixed(2);
  mkChart("c-sleep", { type: "line", data: { labels, datasets: [
    lineDs("Всего", get(rs, "sleep_s", h1), css("--s1")),
    lineDs("Глубокий", get(rs, "deep_s", h1), css("--s2")),
    lineDs("REM", get(rs, "rem_s", h1), css("--s3")),
  ] }, options: timeOpts({ y: { min: 0 } }) });
  mkChart("c-bb", { type: "line", data: { labels, datasets: [
    lineDs("Body Battery (макс.)", get("garmin", "body_battery"), css("--s1")),
    lineDs("Готовность", get("garmin", "readiness"), css("--s3")),
  ] }, options: timeOpts({ y: { min: 0, max: 100 } }) });
}

// ---------- Источники ----------
async function renderSettings() {
  const s = await api("status");
  const src = [
    ["tp", "TrainingPeaks · веб-API", "План, факт, комментарии тренера, CTL/ATL/TSB", "TP_AUTH_COOKIE"],
    ["tp_ical", "TrainingPeaks · iCal", "Только план тренера (резервный канал)", "TP_ICAL_URL"],
    ["garmin", "Garmin Connect", "Тренировки, Body Battery, готовность, стресс", "GARMIN_EMAIL / GARMIN_PASSWORD"],
    ["fitbit", "Fitbit · Google Health API", "Сон, HRV, пульс покоя, пульс на тренировках", "GOOGLE_HEALTH_CLIENT_ID / SECRET"],
  ];
  const last = {};
  s.log.forEach((l) => { if (!last[l.source]) last[l.source] = l; });
  $("#view-settings").innerHTML = `
    ${s.demo ? `<div class="alert" style="margin-bottom:16px"><span>ℹ</span><span>Сейчас открыт <b>демо-режим</b> со сгенерированными данными. Реальные данные — запуск без <code>IRONMAN_DEMO=1</code>.</span></div>` : ""}
    <div class="page-head"><div><h1>Источники</h1><div class="sub">подключения, пороги и журнал синхронизаций</div></div></div>
    <div class="card">${src.map(([k, name, desc, envName]) => {
      const l = last[k];
      return `<div class="src"><div><div class="name">${name}</div><div class="muted" style="font-size:13px">${desc}</div>
          ${l ? `<div style="font-size:12px;margin-top:4px" class="${l.ok ? "status-ok" : "status-bad"}">${l.ok ? "✓" : "✗"} ${esc(l.ts)} — ${esc(l.message)}</div>` : ""}</div>
        <div>${s.configured[k] ? `<span class="pill"><span class="dot done"></span>настроен</span>`
          : k === "fitbit" ? `<a class="btn primary" href="/api/fitbit/login" style="text-decoration:none">Подключить</a>`
          : `<span class="pill" title="${envName}"><span class="dot upcoming"></span>не настроен</span>`}</div></div>`;
    }).join("")}</div>
    <h2>Пороги и зоны</h2>
    <div class="card" id="thr-card"><div class="muted">Загрузка…</div></div>
    <h2>Установка на Android</h2>
    <div class="card"><ol class="steps">
      <li>В Chrome на телефоне откройте <code>${location.origin}</code> и войдите.</li>
      <li>Меню ⋮ → «Добавить на главный экран» / «Установить приложение».</li>
    </ol></div>
    <h2>Журнал синхронизаций</h2>
    <div class="card table-wrap"><table class="data"><thead><tr><th>Время</th><th>Источник</th><th>Результат</th></tr></thead><tbody>
      ${s.log.map((l) => `<tr><td class="num">${esc(l.ts)}</td><td style="text-align:left">${esc(l.source)}</td><td style="text-align:left" class="${l.ok ? "" : "status-bad"}">${esc(l.message)}</td></tr>`).join("") || `<tr><td colspan="3" class="muted">Пока пусто</td></tr>`}
    </tbody></table></div>`;
  renderThresholds();
}

// ---------- пояснения терминов при наведении ----------
const GLOSSARY = {
  "TSS": ["Training Stress Score — балл нагрузки тренировки",
    "Учитывает длительность и интенсивность. Час на пороге (ПАНО) = 100 TSS. Час спокойно — 40–60, жёсткие интервалы — 80–100. Позволяет сравнивать разные виды спорта."],
  "CTL": ["Фитнес (Chronic Training Load)",
    "Средний TSS за ~6 недель — ваша тренированность. Растёт медленно. К старту Ironman обычно нужно 90–130."],
  "ATL": ["Усталость (Acute Training Load)",
    "Средний TSS за последнюю неделю — насколько вы нагружены прямо сейчас. Растёт и падает быстро."],
  "TSB": ["Свежесть (Training Stress Balance)",
    "Фитнес − усталость. Ниже −30 — перегруз, −10…−30 — рабочая усталость, около 0 — баланс, +5…+25 — свежесть перед стартом."],
  "HRV": ["Вариабельность пульса",
    "Насколько различаются интервалы между ударами сердца ночью. Выше вашей нормы — хорошо восстановились, заметно ниже (−10…−15%) — усталость, стресс или начинающаяся болезнь."],
  "RMSSD": ["Метод расчёта HRV", "Среднеквадратичная разница соседних интервалов между ударами, в миллисекундах."],
  "VO2 max": ["Максимальное потребление кислорода",
    "Сколько кислорода организм может использовать на пике, мл/кг/мин. Главный показатель «мотора» выносливости. Оценка Garmin по бегу с пульсом."],
  "Body Battery": ["Запас энергии (Garmin)", "0–100: заряжается во сне и отдыхе, тратится на нагрузку и стресс. Ниже 25 утром — день лучше сделать лёгким."],
  "Endurance Score": ["Оценка выносливости (Garmin)", "Сводная оценка способности выдерживать долгую нагрузку по всем тренировкам. Уровни: начальный → средний → тренированный → хорошо тренированный → эксперт → элита."],
  "Готовность": ["Готовность к тренировке (Garmin)", "0–100 по сну, HRV, недавней нагрузке и восстановлению. Выше 75 — можно нагружать, ниже 25 — нужен отдых."],
  "ПАНО": ["Порог анаэробного обмена",
    "Интенсивность, выше которой лактат копится быстрее, чем утилизируется. Примерно то, что вы держите около часа. От пульса ПАНО считаются зоны и TSS."],
  "LTHR": ["Пульс ПАНО (Lactate Threshold Heart Rate)", "От него считаются пульсовые зоны и TSS по пульсу."],
  "FTP": ["Функциональная пороговая мощность", "Мощность на велосипеде, которую вы держите около часа, в ваттах. От неё считается TSS по мощности."],
  "NP": ["Нормализованная мощность", "Мощность с поправкой на рывки: показывает, во что тренировка обошлась организму, честнее средней мощности."],
  "SWOLF": ["Эффективность плавания (swim + golf)",
    "Время отрезка в секундах + число гребков на нём. Чем меньше, тем эффективнее: быстрее и меньшим числом гребков. Сравнивайте только в одном бассейне и одним стилем."],
  "REM": ["Быстрый сон", "Фаза сна, важная для восстановления нервной системы и памяти. Норма — около 20–25% сна."],
  "T1": ["Первый переход", "Из воды на велосипед: снять гидрокостюм, шлем, обувь. На Ironman обычно 4–8 минут."],
  "T2": ["Второй переход", "С велосипеда на бег: поставить велосипед, сменить обувь. Обычно 2–5 минут."],
  "Z1": ["Зона 1 — восстановление", "Ниже 85% пульса ПАНО. Очень легко, можно разговаривать."],
  "Z2": ["Зона 2 — аэробная база", "85–89% пульса ПАНО. Основа подготовки к Ironman, большая часть объёма."],
  "Z3": ["Зона 3 — темп", "90–94% пульса ПАНО. Около темпа гонки на длинных дистанциях."],
  "Z4": ["Зона 4 — порог", "95–99% пульса ПАНО. Тяжело, держится 20–60 минут."],
  "Z5": ["Зона 5 — выше порога", "От 100% пульса ПАНО. Интервалы, VO2 max, короткие усилия."],
  "Аэробный эффект": ["Training Effect (Garmin), 0–5",
    "Как тренировка развила аэробную выносливость: 1–2 — незначительно, 2–3 — поддерживает, 3–4 — улучшает, 4–5 — сильно улучшает, 5 — перегрузка."],
  "Анаэробный эффект": ["Training Effect (Garmin), 0–5", "Как тренировка развила способность к коротким мощным усилиям выше порога."],
  "Эффективность": ["Эффективность сна", "Доля времени в кровати, когда вы действительно спали. Хорошо — выше 85%."],
  "Ригеля": ["Формула Ригеля", "Прогноз времени на длинную дистанцию по результату на короткой: время растёт чуть быстрее дистанции из-за усталости."],
};
const TERM_RE = new RegExp("(" + Object.keys(GLOSSARY).sort((a, b) => b.length - a.length)
  .map((t) => (/^[A-Z0-9 ]+$/.test(t) ? `\\b${t}\\b` : t)).join("|") + ")", "g");
const TERM_TEST = new RegExp(TERM_RE.source);  // без флага g — для проверки без побочного lastIndex
let _annotating = false;
function annotate(root) {
  _annotating = true;
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, { acceptNode: (n) =>
    n.parentElement.closest(".term, script, style, input, textarea, select, option, svg, .leaflet-container, .toast, #tip")
      ? NodeFilter.FILTER_REJECT : TERM_TEST.test(n.data) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_SKIP });
  const nodes = [];
  while (walker.nextNode()) nodes.push(walker.currentNode);
  for (const n of nodes) {
    TERM_RE.lastIndex = 0;
    const frag = document.createDocumentFragment();
    let last = 0, m;
    while ((m = TERM_RE.exec(n.data))) {
      frag.append(n.data.slice(last, m.index));
      const sp = document.createElement("span"); sp.className = "term"; sp.dataset.term = m[1]; sp.textContent = m[1];
      frag.append(sp); last = m.index + m[1].length;
    }
    frag.append(n.data.slice(last));
    n.replaceWith(frag);
  }
  TERM_RE.lastIndex = 0;
  _annotating = false;
}
const tip = Object.assign(document.createElement("div"), { id: "tip", hidden: true });
document.body.append(tip);
function showTip(el) {
  const [t, d] = GLOSSARY[el.dataset.term] || [];
  if (!t) return;
  tip.innerHTML = `<b>${esc(el.dataset.term)}</b> — ${esc(t)}<div>${esc(d)}</div>`;
  tip.hidden = false;
  const r = el.getBoundingClientRect(), w = Math.min(320, innerWidth - 24);
  tip.style.width = w + "px";
  tip.style.left = Math.max(12, Math.min(innerWidth - w - 12, r.left + r.width / 2 - w / 2)) + "px";
  const below = r.bottom + 8 + tip.offsetHeight < innerHeight;
  tip.style.top = (below ? r.bottom + 8 : r.top - tip.offsetHeight - 8) + "px";
}
document.addEventListener("mouseover", (e) => { const t = e.target.closest?.(".term"); if (t) showTip(t); });
document.addEventListener("mouseout", (e) => { if (e.target.closest?.(".term")) tip.hidden = true; });
document.addEventListener("click", (e) => {   // телефон: по нажатию
  const t = e.target.closest(".term");
  if (t) { e.stopPropagation(); showTip(t); } else tip.hidden = true;
}, true);
addEventListener("scroll", () => (tip.hidden = true), { passive: true });
let _annT;
new MutationObserver(() => { if (_annotating) return; clearTimeout(_annT); _annT = setTimeout(() => annotate($("#app")), 60); })
  .observe(document.getElementById("app"), { childList: true, subtree: true });

async function renderThresholds() {
  const t = await api("thresholds"), el = $("#thr-card"); if (!el) return;
  const fmtV = (k, v) => (k === "run_pace" ? mmss(v) + " /км" : k === "swim_css" ? mmss(v) + " /100 м" : `${n0(v)}`);
  const toInput = (k, v) => (k === "run_pace" || k === "swim_css" ? mmss(v) : v);
  el.innerHTML = `<form id="thr-form" class="thr-grid">${Object.entries(t.values).map(([k, x]) => `<label><span>${esc(x.label)}</span>
      <input name="${k}" value="${toInput(k, x.value)}" ${k === "run_pace" || k === "swim_css" ? 'placeholder="м:сс"' : 'type="number" step="any"'}>
      <em class="muted">${x.source}${x.garmin != null && x.source === "вручную" ? ` · Garmin: ${fmtV(k, x.garmin)}` : ""}${k === "weight" || k === "ftp" ? "" : ""}</em></label>`).join("")}
    <div class="thr-actions"><button class="btn primary" type="submit">Сохранить</button>
      <button class="btn" type="button" id="thr-reset">Вернуть значения Garmin</button></div></form>
    <div class="zones-row"><span class="src-tag">Пульсовые зоны · бег</span>${t.zones_run.map((f, i) => `<span class="zchip"><i class="z${i + 1}"></i>Z${i + 1} от ${f || "—"}</span>`).join("")}</div>
    <div class="zones-row"><span class="src-tag">Пульсовые зоны · велосипед</span>${t.zones_bike.map((f, i) => `<span class="zchip"><i class="z${i + 1}"></i>Z${i + 1} от ${f || "—"}</span>`).join("")}</div>
    <div class="muted" style="font-size:12.5px;margin-top:8px">Значения из Garmin обновляются при каждой синхронизации${t.garmin_updated ? ` (последний раз ${esc(t.garmin_updated)})` : ""}.
      Ручное значение важнее. По порогам считаются TSS, зоны и форма.</div>`;
  const f = $("#thr-form");
  const parse = (k, v) => (k === "run_pace" || k === "swim_css" ? parseHMS(v) : v === "" ? null : +v);
  f.onsubmit = async (e) => { e.preventDefault();
    const body = {}; for (const [k, x] of Object.entries(t.values)) { const v = parse(k, f[k].value); if (v !== x.value) body[k] = v; }
    await api("thresholds", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    toast("Пороги сохранены"); syncInfo(); renderThresholds(); };
  $("#thr-reset").onclick = async () => {
    await api("thresholds", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(Object.fromEntries(Object.keys(t.values).map((k) => [k, null]))) });
    toast("Возвращены значения Garmin"); renderThresholds(); };
}

// ---------- роутинг ----------
const VIEWS = { today: renderToday, calendar: renderCalendar, goal: renderGoal, races: renderRaces, load: renderLoad, health: renderHealth, settings: renderSettings, report: renderReport };
async function route() {
  const v = (location.hash.slice(1) || "today").split(/[?/]/)[0];
  const name = VIEWS[v] ? v : "today";
  document.querySelectorAll(".view").forEach((s) => s.classList.toggle("active", s.id === "view-" + name));
  document.querySelectorAll("#tabs a").forEach((a) => a.classList.toggle("active", a.dataset.view === (name === "report" ? "calendar" : name)));
  try { await VIEWS[name](); } catch (e) { $("#view-" + name).innerHTML = `<div class="card status-bad">Ошибка загрузки: ${esc(e.message)}</div>`; }
}
window.addEventListener("hashchange", route);
matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => { chartDefaults(); route(); });

async function doSync(e) {
  const b = e.currentTarget; b.disabled = true; toast("Синхронизация…", 120000);
  try {
    const res = await api("sync", { method: "POST" });
    toast(res.length ? res.map((r) => `${r.ok ? "✓" : "✗"} ${r.message}`).join("\n") : "Нет настроенных источников — см. «Источники»", 7000);
    route(); syncInfo();
  } catch (err) { toast("Ошибка: " + err.message); }
  b.disabled = false;
}
$("#sync-btn").onclick = doSync;
$("#sync-btn-m").onclick = doSync;
async function syncInfo() {
  try {
    const s = await api("status");
    $("#demo-badge").hidden = !s.demo;
    const ts = s.log.find((l) => l.ok)?.ts;
    $("#sync-info").textContent = ts ? `обновлено ${ts.slice(8, 10)}.${ts.slice(5, 7)} в ${ts.slice(11, 16)}` : "";
    _race = s.race; _lthr = s.thresholds?.lthr || LTHR_DEFAULT; _zones = s.thresholds?.zones_run || null;
    const days = Math.round((parseD(s.race.date) - parseD(iso(new Date()))) / 864e5);
    $("#race-mini").textContent = `до старта ${days} дн.`;
  } catch {}
}

async function whoami() {
  const me = await api("me"); _me = me;
  document.body.classList.toggle("role-coach", me.role === "coach");
  $("#user-box").innerHTML = `<div class="avatar">${esc((me.name || me.login)[0].toUpperCase())}</div>
    <div><b>${esc(me.name || me.login)}</b><span class="muted">${esc(me.role_name)}</span></div>
    <button class="icon-btn" id="logout" title="Выйти" aria-label="Выйти">${icon("logout")}</button>`;
  $("#logout").onclick = logout;
  const lm = $("#logout-m"); if (lm) lm.onclick = logout;
  if (me.role === "coach" && location.hash.startsWith("#settings")) location.hash = "#today";
}
async function logout() {
  await fetch("/api/logout", { method: "POST" });
  try { for (const k of await caches.keys()) await caches.delete(k); } catch {}
  location.replace("/login");
}

(async function init() {
  chartDefaults();
  document.querySelectorAll("[data-icon]").forEach((el) => (el.outerHTML = icon(el.dataset.icon)));
  try { await whoami(); } catch { return; }
  syncInfo();
  route();
  if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js").catch(() => {});
})();
