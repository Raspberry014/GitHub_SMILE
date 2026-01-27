import os, sqlite3, random
from datetime import datetime
from flask import Flask, render_template, request, redirect
import numpy as np
import pandas as pd

# Важно для рисования графиков без GUI-окна:
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(__file__)
DB_PATH   = os.path.join(BASE_DIR, "cruise_ps.sqlite")
PLOTS_DIR = os.path.join(BASE_DIR, "static", "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

app = Flask(__name__)

# -------------------- ИНИЦИАЛИЗАЦИЯ БД И ДАННЫХ --------------------
def create_db_and_seed_if_needed():
    if os.path.exists(DB_PATH):
        return
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.executescript("""
    PRAGMA foreign_keys = ON;

    CREATE TABLE education (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT UNIQUE NOT NULL
    );
    CREATE TABLE social_status (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT UNIQUE NOT NULL
    );
    CREATE TABLE place (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT UNIQUE NOT NULL
    );

    CREATE TABLE client (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      last_name   TEXT NOT NULL,
      first_name  TEXT NOT NULL,
      patronymic  TEXT NOT NULL,
      age INTEGER CHECK (age BETWEEN 0 AND 120),
      education_id INTEGER REFERENCES education(id),
      social_status_id INTEGER REFERENCES social_status(id),
      income REAL CHECK (income >= 0)
    );

    CREATE TABLE booking (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      client_id INTEGER REFERENCES client(id),
      place_id  INTEGER REFERENCES place(id),
      start_date DATE NOT NULL,
      duration_days INTEGER CHECK (duration_days > 0),
      spend_amount REAL CHECK (spend_amount >= 0)
    );
    """)

    educations = ["Среднее", "Среднее профессиональное", "Неоконченное высшее", "Высшее"]
    for name in educations:
        cur.execute("INSERT INTO education(name) VALUES(?)", (name,))

    statuses = ["Студент", "Рабочий", "Служащий", "Руководитель", "Предприниматель", "Пенсионер"]
    for name in statuses:
        cur.execute("INSERT INTO social_status(name) VALUES(?)", (name,))

    places = ["Санаторий", "База отдыха", "Дом отдыха", "Дача", "Курортный отель", "Турпансионат"]
    for name in places:
        cur.execute("INSERT INTO place(name) VALUES(?)", (name,))

    # Карты id для справочников
    edu_map    = {row[1]: row[0] for row in cur.execute("SELECT id, name FROM education").fetchall()}
    status_map = {row[1]: row[0] for row in cur.execute("SELECT id, name FROM social_status").fetchall()}
    place_map  = {row[1]: row[0] for row in cur.execute("SELECT id, name FROM place").fetchall()}

    # Демоданные: 600 записей
    random.seed(42); np.random.seed(42)

    last_names = ["Иванов","Петров","Сидоров","Кузнецов","Смирнов","Волков","Морозов","Зайцев","Егоров","Соколов",
                  "Поляков","Алексеев","Фёдоров","Орлов","Макаров","Соловьёв","Беляев","Комаров","Киселёв","Гаврилов"]
    first_names = ["Иван","Пётр","Алексей","Сергей","Дмитрий","Михаил","Андрей","Никита","Егор","Тимур",
                   "Алина","Анна","Елена","Мария","Ольга","Татьяна","Ксения","Дарья","Наталья","Виктория"]
    patr_names = ["Иванович","Петрович","Алексеевич","Сергеевич","Дмитриевич","Михайлович","Андреевич","Никитич","Егорович","Тимурович",
                  "Ивановна","Петровна","Алексеевна","Сергеевна","Дмитриевна","Михайловна","Андреевна","Никитична","Егоровна","Тимуровна"]

    pref_weights = {
        "Студент":           [0.05, 0.35, 0.25, 0.25, 0.05, 0.05],
        "Рабочий":           [0.15, 0.30, 0.25, 0.15, 0.10, 0.05],
        "Служащий":          [0.20, 0.25, 0.25, 0.10, 0.15, 0.05],
        "Руководитель":      [0.35, 0.10, 0.10, 0.05, 0.30, 0.10],
        "Предприниматель":   [0.30, 0.10, 0.10, 0.05, 0.35, 0.10],
        "Пенсионер":         [0.45, 0.15, 0.20, 0.10, 0.05, 0.05],
    }
    income_ranges = {
        "Студент": (80000, 220000),
        "Рабочий": (200000, 450000),
        "Служащий": (250000, 600000),
        "Руководитель": (600000, 1500000),
        "Предприниматель": (700000, 2000000),
        "Пенсионер": (150000, 350000),
    }
    base_daily = {"Санаторий":28000,"База отдыха":12000,"Дом отдыха":15000,"Дача":5000,"Курортный отель":45000,"Турпансионат":20000}
    month_weights = {1:0.05,2:0.05,3:0.06,4:0.07,5:0.10,6:0.18,7:0.20,8:0.18,9:0.07,10:0.04,11:0.03,12:0.07}

    def wchoice(options, weights):
        return random.choices(options, weights=weights, k=1)[0]

    N = 600
    for _ in range(N):
        ln = random.choice(last_names); fn = random.choice(first_names); pn = random.choice(patr_names)
        age = int(np.clip(np.random.normal(38, 12), 18, 80))
        edu_name = random.choice(list(edu_map.keys()))
        status_name = random.choice(list(status_map.keys()))
        income = int(np.random.uniform(*income_ranges[status_name]))
        place_name = wchoice(list(place_map.keys()), pref_weights[status_name])

        duration = int(np.clip(int(np.random.normal(10, 4)), 3, 28))
        month = random.choices(list(month_weights.keys()), weights=list(month_weights.values()), k=1)[0]
        year  = random.choice([2024, 2025])
        day   = random.randint(1, 28)
        start_date = f"{year:04d}-{month:02d}-{day:02d}"

        base = base_daily[place_name] * duration * np.random.uniform(0.85, 1.15)
        alpha = np.random.uniform(0.07, 0.18)
        spend = int(base + alpha * income)

        # client
        cur.execute("""INSERT INTO client(last_name, first_name, patronymic, age, education_id, social_status_id, income)
                       VALUES(?,?,?,?,?,?,?)""",
                    (ln, fn, pn, age, edu_map[edu_name], status_map[status_name], float(income)))
        client_id = cur.lastrowid

        # booking
        cur.execute("""INSERT INTO booking(client_id, place_id, start_date, duration_days, spend_amount)
                       VALUES(?,?,?,?,?)""",
                    (client_id, place_map[place_name], start_date, duration, float(spend)))

    # полезные VIEW
    cur.executescript("""
    CREATE VIEW v_pref_by_status AS
    SELECT s.name AS соц_статус, p.name AS место, COUNT(*) AS кол
    FROM booking b
    JOIN client c ON c.id = b.client_id
    JOIN social_status s ON s.id = c.social_status_id
    JOIN place p ON p.id = b.place_id
    GROUP BY s.name, p.name;

    CREATE VIEW v_monthly AS
    SELECT substr(start_date,1,7) AS месяц, COUNT(*) AS кол
    FROM booking
    GROUP BY 1
    ORDER BY 1;

    CREATE VIEW v_season AS
    WITH t AS (
      SELECT CASE
        WHEN CAST(strftime('%m', start_date) AS INT) IN (12,1,2)  THEN 'Зима'
        WHEN CAST(strftime('%m', start_date) AS INT) IN (3,4,5)   THEN 'Весна'
        WHEN CAST(strftime('%m', start_date) AS INT) IN (6,7,8)   THEN 'Лето'
        ELSE 'Осень' END AS сезон
      FROM booking
    )
    SELECT сезон, COUNT(*) AS кол FROM t GROUP BY сезон;
    """)
    con.commit()
    con.close()

create_db_and_seed_if_needed()

# -------------------- УТИЛИТЫ --------------------
def q(sql, args=(), one=False):
    con = sqlite3.connect(DB_PATH); con.row_factory = sqlite3.Row
    cur = con.execute(sql, args)
    rows = cur.fetchall()
    con.close()
    return (rows[0] if rows else None) if one else rows

def ensure_plots():
    # строим графики из БД (и считаем корреляцию)
    con = sqlite3.connect(DB_PATH)
    df_c = pd.read_sql_query("SELECT * FROM client", con)
    df_b = pd.read_sql_query("SELECT * FROM booking", con)
    places = pd.read_sql_query("SELECT * FROM place", con)
    con.close()

    df = df_b.merge(df_c, left_on='client_id', right_on='id', suffixes=('_b','_c'))
    df = df.merge(places, left_on='place_id', right_on='id', suffixes=('','_p')).rename(columns={'name':'place_name'})

    # 1) Популярность мест
    plt.figure(figsize=(7.5,4.5))
    df['place_name'].value_counts().sort_values(ascending=False).plot(kind='bar')
    plt.title('Популярность мест отдыха (всего)')
    plt.xlabel('Место отдыха'); plt.ylabel('Количество отдыхающих')
    plt.tight_layout(); plt.savefig(os.path.join(PLOTS_DIR,'places_overall.png'), dpi=140); plt.close()

    # 2) Доход vs Затраты + регрессия
    plt.figure(figsize=(7,4.8))
    plt.scatter(df['income'], df['spend_amount'], alpha=0.5)
    coef = np.polyfit(df['income'], df['spend_amount'], 1)
    x = np.linspace(df['income'].min(), df['income'].max(), 100)
    y = coef[0]*x + coef[1]
    plt.plot(x, y, linewidth=2)
    corr = float(df[['income','spend_amount']].corr().iloc[0,1])
    plt.title(f'Доход vs Затраты (корреляция = {corr:.2f})')
    plt.xlabel('Доход в месяц'); plt.ylabel('Сумма затрат на отдых')
    plt.tight_layout(); plt.savefig(os.path.join(PLOTS_DIR,'income_spend_corr.png'), dpi=140); plt.close()

    # 3) Помесячная динамика
    d = df.copy(); d['start_date'] = pd.to_datetime(d['start_date'])
    monthly = d.groupby(d['start_date'].dt.to_period('M')).size().reset_index(name='cnt'); monthly['m'] = monthly['start_date'].astype(str)
    plt.figure(figsize=(9,4.5))
    plt.plot(range(len(monthly)), monthly['cnt'])
    plt.xticks(range(len(monthly)), monthly['m'], rotation=45, ha='right')
    plt.title('Динамика количества отдыхающих по месяцам')
    plt.xlabel('Месяц'); plt.ylabel('Количество')
    plt.tight_layout(); plt.savefig(os.path.join(PLOTS_DIR,'monthly_trend.png'), dpi=140); plt.close()

    # 4) Сезонность
    season_map = {12:'Зима',1:'Зима',2:'Зима',3:'Весна',4:'Весна',5:'Весна',6:'Лето',7:'Лето',8:'Лето',9:'Осень',10:'Осень',11:'Осень'}
    d['season'] = d['start_date'].dt.month.map(season_map)
    sc = d['season'].value_counts().reindex(['Зима','Весна','Лето','Осень']).fillna(0)
    plt.figure(figsize=(6.5,4))
    plt.bar(sc.index, sc.values)
    plt.title('Сезонность отдыхающих'); plt.xlabel('Сезон'); plt.ylabel('Количество')
    plt.tight_layout(); plt.savefig(os.path.join(PLOTS_DIR,'seasonal.png'), dpi=140); plt.close()
    return corr

# -------------------- РОУТЫ --------------------
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/data/clients")
def clients():
    rows = q("""
        SELECT c.id, c.last_name, c.first_name, c.patronymic, c.age,
               e.name AS education, s.name AS social_status, c.income
        FROM client c
        LEFT JOIN education e ON e.id=c.education_id
        LEFT JOIN social_status s ON s.id=c.social_status_id
        ORDER BY c.id DESC
        LIMIT 100
    """)
    return render_template("clients.html", rows=rows)

@app.route("/data/bookings")
def bookings():
    rows = q("""
        SELECT b.id,
               (c.last_name||' '||c.first_name||' '||c.patronymic) AS fio,
               p.name AS place, b.start_date, b.duration_days, b.spend_amount
        FROM booking b
        JOIN client c ON c.id=b.client_id
        JOIN place  p ON p.id=b.place_id
        ORDER BY b.id DESC
        LIMIT 100
    """)
    return render_template("bookings.html", rows=rows)

@app.route("/add", methods=["GET","POST"])
def add():
    con = sqlite3.connect(DB_PATH); con.row_factory = sqlite3.Row
    if request.method == "POST":
        f = request.form; cur = con.cursor()
        cur.execute("""
            INSERT INTO client(last_name,first_name,patronymic,age,education_id,social_status_id,income)
            VALUES(?,?,?,?,?,?,?)
        """, (f['last_name'], f['first_name'], f['patronymic'], int(f['age']),
              int(f['education_id']), int(f['social_status_id']), float(f['income'])))
        cid = cur.lastrowid
        cur.execute("""
            INSERT INTO booking(client_id,place_id,start_date,duration_days,spend_amount)
            VALUES(?,?,?,?,?)
        """, (cid, int(f['place_id']), f['start_date'], int(f['duration_days']), float(f['spend_amount'])))
        con.commit(); con.close()
        return redirect("/data/bookings")
    educations = con.execute("SELECT id,name FROM education ORDER BY name").fetchall()
    statuses   = con.execute("SELECT id,name FROM social_status ORDER BY name").fetchall()
    places     = con.execute("SELECT id,name FROM place ORDER BY name").fetchall()
    con.close()
    return render_template("add.html", educations=educations, statuses=statuses, places=places)

@app.route("/analytics")
def analytics():
    corr = ensure_plots()
    return render_template("analytics.html", corr=f"{corr:.2f}")

if __name__ == "__main__":
    print(f"DB: {DB_PATH}")
    app.run(debug=True)
