# Ironman Dashboard

Личная панель подготовки к Ironman: план тренера из **TrainingPeaks**, тренировки с **Garmin**, сон и восстановление с **Fitbit** (Google Health API) — в одном окне, на компьютере и на Android (PWA). Спортсмен видит всё и управляет данными, тренер — смотрит и комментирует.

## Что умеет

| Раздел | Что внутри |
|---|---|
| **Сегодня** | Восстановление 0–100 % и нагрузка дня 0–21 в духе WHOOP, «сколько ещё можно сегодня», тренировка от тренера, неделя «план ↔ факт» со стрелками переносов, режим сна, сигналы, тренированность Garmin |
| **План/факт** | Календарь на 1–4 недели, разбор каждой тренировки (Training Effect, зоны, карта маршрута), комментарии спортсмена и тренера, ручное добавление тренировок по пульсу Fitbit (хоккей и т. п.), недельный отчёт для печати / PDF |
| **Дисциплины** | Цель на финиш (по умолчанию 10:00) против прогноза, витрины плавания / велосипеда / бега с темпом, картами и аэробной эффективностью, путь к старту по фазам с ориентиром CTL, личные рекорды, выбор старта и калькулятор питания, снаряжение |
| **Нагрузка** | CTL / ATL / TSB с прогнозом по плану, объёмы по неделям, выполнение плана по TSS |
| **Здоровье** | Пульс и нагрузка за день, 30 дней восстановления, отбой против цели, влияние отбоя на HRV, HRV, пульс покоя, сон, Body Battery, вес |
| **Источники** | Статус подключений, пороги и пульсовые зоны (из Garmin + ручная правка), журнал синхронизаций |

Подсказки к терминам (TSS, CTL, HRV, ПАНО…) — при наведении. Тёмная тема — автоматически.

## Как считается

- **TSS** — из TrainingPeaks / Garmin, иначе по мощности → пульсу → темпу от ваших порогов.
- **CTL / ATL / TSB** — модель Банистера (42 / 7 дней) по всем тренировкам, включая те, что не попали в TrainingPeaks.
- **Восстановление** — ночь против личной нормы за 30 дней: HRV (главный вес), пульс покоя, сон против потребности, поздний отбой.
- **Нагрузка дня** — TRIMP по поминутному пульсу Fitbit (пропуски — с часов Garmin), логарифмическая шкала 0–21.
- **Прогноз на гонку** — лучшая четверть тренировок с поправкой на дистанцию (Ригель); бег — прогноз Garmin на марафон × 1,12.

## Установка

```bash
python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env            # заполнить доступы, см. ниже
.venv/bin/python -m app.auth add <логин> --role athlete     # пользователь панели
.venv/bin/uvicorn app.server:app --port 8000
```

Демо без аккаунтов: `IRONMAN_DEMO=1 .venv/bin/python -m app.sync demo && IRONMAN_DEMO=1 .venv/bin/uvicorn app.server:app`.

### Источники данных

- **TrainingPeaks.** Официального API для частных лиц нет. Используется cookie `Production_tpAuth` из браузера (`TP_AUTH_COOKIE`) или iCal-ссылка календаря (`TP_ICAL_URL`, только план).
- **Garmin.** Библиотека `garminconnect`. Первый вход: `python -m app.sync garmin-login` (спросит код MFA), токены сохраняются в `data/garmin_tokens`, пароль после этого не нужен.
- **Fitbit.** Через Google Health API: проект в Google Cloud → включить Google Health API → OAuth-клиент типа Web application с redirect `PUBLIC_URL/api/fitbit/callback` → `GOOGLE_HEALTH_CLIENT_ID/SECRET` в `.env` → «Источники → Подключить».

### Пользователи

```bash
python -m app.auth add robert --role athlete     # полный доступ
python -m app.auth add coach --role coach        # тренер: просмотр и комментарии
python -m app.auth invite coach --role coach     # одноразовая ссылка, пароль задаёт сам человек
python -m app.auth list | remove <логин>
```

## Виджет на рабочий стол macOS

`widget/ironman.widget.jsx` — виджет для [Übersicht](https://tracesof.net/uebersicht/): восстановление, нагрузка дня, тренировка на сегодня, отбой, дни до старта. Обновляется раз в 15 минут, клик открывает панель.

```bash
brew install --cask ubersicht
mkdir -p ~/.config/ironman-widget && chmod 700 ~/.config/ironman-widget
echo "https://ваш-адрес" > ~/.config/ironman-widget/url
python -m app.auth widget-token > ~/.config/ironman-widget/token   # на сервере; ключ только для чтения сводки
ln -s "$PWD/widget/ironman.widget.jsx" ~/Library/Application\ Support/Übersicht/widgets/
```

Положение — константы `TOP` / `LEFT` в начале файла.

## Развёртывание на сервере

Проверено на Ubuntu 24.04: пользователь `ironman`, код в `/opt/ironman/app`, systemd-служба `ironman` (uvicorn на 127.0.0.1:8000), Caddy с автоматическим HTTPS перед ней, файрвол ufw (22, 80, 443). Данные синхронизируются раз в час (`SYNC_INTERVAL_MIN`).

```bash
./deploy.sh        # rsync кода на DEPLOY_HOST (по умолчанию ssh-хост «ironman»), перезапуск службы
```

`deploy.sh` не трогает `data/` и `.env` на сервере.

## Устройство

```
app/
  connectors/   trainingpeaks.py · garmin.py · fitbit.py (Google Health API)
  service.py    сведение источников: план↔факт, дедупликация, форма, режим
  recovery.py   восстановление и нагрузка дня
  goals.py      цель на гонку, витрины дисциплин, прогнозы
  extras.py     путь к старту, рекорды, эффективность, комментарии, отчёт, вес, снаряжение
  thresholds.py пороги и зоны (Garmin → ручная правка → по умолчанию)
  auth.py       пользователи, сессии, приглашения
  server.py     FastAPI: /api/*, вход, роли, статика
web/            PWA без сборки: index.html · app.js · styles.css · login · setup
data/           SQLite и токены — только локально, в git не попадает
```

Личный проект: Garmin Connect и веб-API TrainingPeaks — неофициальные интерфейсы и могут меняться.
