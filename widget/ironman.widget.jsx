// Ironman Dashboard — виджет для рабочего стола macOS (Übersicht).
// Ставится в ~/Library/Application Support/Übersicht/widgets/
// Ключ читается из ~/.config/ironman-widget/token, адрес — из ~/.config/ironman-widget/url.
import { css, run } from "uebersicht";

// Положение на экране (в точках от левого верхнего угла) — поменяйте, чтобы подвинуть
const TOP = 186;
const LEFT = 376;

export const refreshFrequency = 15 * 60 * 1000; // раз в 15 минут

export const command = `
  DIR="$HOME/.config/ironman-widget"
  URL=$(cat "$DIR/url" 2>/dev/null)
  curl -s -m 20 "$URL/api/widget?token=$(cat "$DIR/token")"
`;

const ZONE = { green: "#3ecf5a", yellow: "#f5c03b", red: "#ff6159" };
const SPORT = { run: "🏃", bike: "🚴", swim: "🏊", strength: "💪", hockey: "🏒", football: "⚽", rest: "🌙", other: "•" };
const STATUS = { done: "✓", partial: "◐", off: "≠", missed: "✗", today: "", upcoming: "", unplanned: "+", rest: "" };

const ru = (v) => (v == null ? "—" : String(v).replace(".", ","));

const Ring = ({ value, max, color, label, sub, band, unit }) => {
  const R = 27, C = 2 * Math.PI * R;
  const frac = Math.max(0, Math.min(1, (value || 0) / max));
  const arc = (a0, a1, col, w) => (
    <circle cx="32" cy="32" r={R} fill="none" stroke={col} strokeWidth={w} strokeLinecap="round"
      strokeDasharray={`${Math.max(0.01, (a1 - a0) * C)} ${C}`} strokeDashoffset={-a0 * C} transform="rotate(-90 32 32)" />
  );
  return (
    <div className={ringBox}>
      <svg width="64" height="64" viewBox="0 0 64 64">
        <circle cx="32" cy="32" r={R} fill="none" stroke="rgba(255,255,255,.16)" strokeWidth="6" />
        {band && arc(band[0] / max, band[1] / max, "rgba(62,207,90,.38)", 6)}
        {value != null && frac > 0.01 && arc(0, frac, color, 6)}
        <text x="32" y="37" textAnchor="middle" className={ringVal}>{ru(value)}{unit && <tspan className={ringUnit}>{unit}</tspan>}</text>
      </svg>
      <div className={ringLabel}>{label}</div>
      {sub && <div className={ringSub}>{sub}</div>}
    </div>
  );
};

export const render = ({ output, error }) => {
  let d;
  try { d = JSON.parse(output); } catch (e) { d = null; }
  if (error || !d || d.detail) {
    return <div className={card}><div className={muted}>Ironman: нет связи с панелью{d && d.detail ? ` — ${d.detail}` : ""}</div></div>;
  }
  const w = (d.workouts || [])[0];
  const short = (m) => (m >= 90 ? `${ru(Math.round(m / 6) / 10)} ч` : `${m} мин`);
  // спокойная работа, если влезает в 2,5 ч; иначе — сколько нужно в Z4
  const useZ2 = d.remaining_z2_min <= 150;
  const left = d.remaining > 0.3
    ? `До оптимума ≈ ${short(useZ2 ? d.remaining_z2_min : d.remaining_z4_min)} в ${useZ2 ? "Z2" : "Z4"}`
    : d.strain > d.target[1] ? "Выше оптимума — на сегодня хватит" : "Оптимум набран";
  return (
    <div className={card} onClick={() => run(`open "$(cat "$HOME/.config/ironman-widget/url")"`)}>
      <div className={rings}>
        <Ring value={d.recovery} max={100} color={ZONE[d.zone] || "#999"} label="Восстановл." unit={d.recovery != null ? "%" : ""} />
        <Ring value={d.strain} max={21} color="#5aa0ff" label="Нагрузка" sub={`цель ${ru(d.target[0])}–${ru(d.target[1])}`} band={d.target} />
      </div>
      <div className={info}>
        {w ? (
          <div>
            <div className={title}>{SPORT[w.sport] || "•"} {w.title}{STATUS[w.status] ? ` ${STATUS[w.status]}` : ""}</div>
            <div className={muted}>{[w.minutes && `≈${w.minutes} мин`, d.planned_strain && `нагрузка ≈${ru(d.planned_strain)}`].filter(Boolean).join(" · ")}{d.over_plan ? " · много" : ""}</div>
          </div>
        ) : <div className={title}>Сегодня без тренировки</div>}
        <div className={line}>{left}</div>
        <div className={foot}>{d.hr_stale ? `⚠ пульс до ${d.hr_updated}` : `HRV ${Math.round(d.hrv || 0)} · сон ${ru(d.sleep_h)} ч`} · отбой {d.bed_time || "—"}</div>
        <div className={foot}>До старта {d.days_left} дн · CTL {d.ctl ?? "—"}</div>
      </div>
    </div>
  );
};

// Положение корневого блока
export const className = `
  top: ${TOP}px;
  left: ${LEFT}px;
  font-family: -apple-system, "SF Pro Text", system-ui, sans-serif;
`;

const card = css`
  width: 345px; height: 165px; box-sizing: border-box; padding: 14px 16px;
  display: flex; gap: 12px; align-items: center; cursor: pointer;
  border-radius: 24px; color: #fff;
  background: rgba(255, 255, 255, 0.16);
  backdrop-filter: blur(28px) saturate(1.6); -webkit-backdrop-filter: blur(28px) saturate(1.6);
  border: 1px solid rgba(255, 255, 255, 0.22);
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.12);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.12);
`;
const rings = css`display: flex; gap: 6px; flex: none;`;
const ringBox = css`display: flex; flex-direction: column; align-items: center; width: 66px;`;
const ringVal = css`font: 700 17px -apple-system, system-ui; fill: #fff;`;
const ringUnit = css`font-size: 10px; font-weight: 600;`;
const ringLabel = css`font-size: 10.5px; font-weight: 600; margin-top: 2px; opacity: .95; white-space: nowrap;`;
const ringSub = css`font-size: 9.5px; opacity: .7; white-space: nowrap;`;
const info = css`display: flex; flex-direction: column; gap: 5px; min-width: 0; flex: 1;`;
const title = css`font-size: 14px; font-weight: 650; line-height: 1.2; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;`;
const line = css`font-size: 12px; font-weight: 600; opacity: .95; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;`;
const muted = css`font-size: 11.5px; opacity: .78; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;`;
const foot = css`font-size: 10.5px; opacity: .68; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;`;
