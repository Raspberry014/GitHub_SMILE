# DemoQA UI автотесты (Playwright + Pytest + POM)

Проект покрывает требования практических работ **№2–6** по дисциплине РТПО на сайте https://demoqa.com/.

**Использовано:**
- **Python + Playwright (sync)**
- **Pytest**
- **Page Object Model (POM)**
- **Параллельный запуск**: `pytest-xdist`
- **Конфигурация** через `config/settings.json` + переопределение через переменные окружения
- **Тестовые данные**: JSON + Faker (где нужно)
- **Ожидания**: Playwright `expect` (без `sleep`)
- **Артефакты**: HTML-отчёт, скриншоты при падении, логи

## Разделы DemoQA, которые тестируются
- **Elements** (Text Box / Check Box / Radio Button / Web Tables / Buttons / Links / Upload and Download)
- **Forms** (Practice Form)
- **Alerts, Frame & Windows** (Browser Windows / Frames)
- **Widgets** (Tabs / Tool Tips / Menu / Select Menu)
- **Interactions** (Sortable / Selectable / Resizable / Droppable)

## Требования
- Python 3.10+
- Windows / Linux / macOS

## Установка
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

python -m pip install -r requirements.txt
python -m playwright install
```

## Запуск тестов

### Все тесты + HTML-отчёт
```bash
pytest
```

### Параллельный запуск
DemoQA иногда начинает «тормозить», если воркеров слишком много.  
Для стабильности рекомендуется 2–4 воркера:

```bash
pytest -n 2
# или
pytest -n 4
```

Если хотите попробовать авто-количество:
```bash
pytest -n auto
```

### Запуск только одного раздела
```bash
pytest tests/elements -n 2
pytest tests/widgets -n 2
pytest tests/interactions -n 2
```

### Headed-режим (видимый браузер)
**Windows (PowerShell):**
```powershell
$env:HEADLESS="0"; pytest -n 2
```

**Linux/macOS:**
```bash
HEADLESS=0 pytest -n 2
```

### Сменить браузер
```bash
BROWSER=firefox pytest -n 2
# BROWSER=chromium / firefox / webkit
```

### Сменить base url и таймаут
```bash
BASE_URL=https://demoqa.com TIMEOUT_MS=15000 pytest -n 2
```

### Включить запись видео (опционально)
```bash
RECORD_VIDEO=1 pytest -n 2
```

## Артефакты
- HTML-отчёт: `artifacts/reports/report.html`
- Скриншоты при падении: `artifacts/screenshots/`
- Логи: `artifacts/logs/run_<worker>.log`
- Видео (если включено): `artifacts/videos/`
- Downloads: `artifacts/downloads/`
- Uploads: `artifacts/uploads/`

## Структура проекта
- `pages/` — Page Object Model по разделам сайта
- `tests/` — тесты по разделам
- `data/` — тестовые данные JSON
- `utils/` — логирование, загрузка данных, фиксы UI (баннеры/реклама DemoQA)
