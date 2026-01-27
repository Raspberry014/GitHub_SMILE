# DemoQA UI автотесты (Playwright + Pytest + POM)

Проект выполнен в рамках практических работ №2–5 и содержит UI-автотесты для сайта https://demoqa.com/  
Стек: **Playwright (Python) + Pytest**, архитектура **Page Object Model (POM)**.

## Реализовано
- UI-тестирование сайта DemoQA
- Playwright + Python
- Page Object Model (POM)
- Параллельный запуск тестов (**pytest-xdist**)
- Конфигурация через `config/settings.json` + переопределение через переменные окружения:
  - `BASE_URL`, `TIMEOUT_MS`, `BROWSER`, `HEADLESS`, `RECORD_VIDEO`
- Тестовые данные:
  - JSON (`data/`)
  - генерация данных через **Faker**
- Ожидания через Playwright `expect` (**без `sleep`**)
- Артефакты:
  - **HTML-отчет**
  - скриншоты при падении тестов
  - логирование

## Требования
- Python **3.10+**
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
