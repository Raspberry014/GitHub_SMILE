from fastapi import (
    FastAPI, WebSocket, WebSocketDisconnect,
    HTTPException, status, Form, Request, Cookie
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional
from enum import Enum
from pydantic import BaseModel
import secrets
from datetime import datetime
import sqlite3


app = FastAPI(title="VideoConference MVP")

# Разрешаем CORS (на всякий случай, если будешь открывать из другого origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ====== enum UserStatus (из UML) ======

class UserStatus(str, Enum):
    OFFLINE = "offline"
    IN_LOBBY = "in_lobby"
    IN_CONFERENCE = "in_conference"


# ====== User / Host (из UML) ======

class User(BaseModel):
    id: int
    username: str
    password: str        # для MVP можно в открытом виде
    is_host: bool = False
    status: UserStatus = UserStatus.OFFLINE


# ====== Conference / Lobby (из UML) ======

class Conference(BaseModel):
    id: int
    title: str
    host_id: int
    waiting_room: List[int] = []
    participants: List[int] = []


# ====== In-memory хранилище (вместо БД) ======

users_by_name: Dict[str, User] = {}
users_by_id: Dict[int, User] = {}
sessions: Dict[str, int] = {}   # session_id -> user_id
next_user_id: int = 1

conference = Conference(
    id=1,
    title="Demo conference",
    host_id=-1,   # назначим первого зарегистрированного host'а
    waiting_room=[],
    participants=[]
)

# ====== простой журнал событий в SQLite ======
DB_PATH = "events_log.db"


def init_db() -> None:
    """Создаёт таблицу журнала событий, если её ещё нет."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS conference_events (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            ts         TEXT NOT NULL,   -- время события (UTC)
            event_type TEXT NOT NULL,   -- тип события (login, admit, reject, join и т.п.)
            username   TEXT,
            details    TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def save_event(event_type: str,
               username: str | None = None,
               details: str | None = None) -> None:
    """Записывает одно событие в журнал."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    ts = datetime.utcnow().isoformat(timespec="seconds")
    cur.execute(
        "INSERT INTO conference_events (ts, event_type, username, details) "
        "VALUES (?, ?, ?, ?)",
        (ts, event_type, username, details),
    )
    conn.commit()
    conn.close()


def log_event(event_type: str, actor_id: int | None = None, details: str | None = None) -> None:
    """
    Удобная обёртка: по id берём пользователя и пишем событие в лог.
    """
    user = users_by_id.get(actor_id) if actor_id is not None else None
    username = user.username if user else None
    save_event(event_type, username, details)


def get_last_events(limit: int = 50):
    """
    Возвращает список последних событий (ts, event_type, username, details).
    Можно будет использовать в админ-странице.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT ts, event_type, username, details
        FROM conference_events
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


# инициализируем БД при старте приложения
@app.on_event("startup")
async def on_startup():
  init_db()


# ====== AuthService (из UML) ======

def get_current_user(request: Request) -> User:
    session_id = request.cookies.get("session_id")
    if not session_id or session_id not in sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    user_id = sessions[session_id]
    user = users_by_id.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user


@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
      <meta charset="UTF-8">
      <title>VideoConference MVP</title>
      <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          background: radial-gradient(circle at top, #1d4ed8, #020617 55%);
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          color: #e5e7eb;
        }
        .card {
          background: rgba(15, 23, 42, 0.92);
          padding: 32px 40px;
          border-radius: 20px;
          box-shadow: 0 24px 80px rgba(15, 23, 42, 0.9);
          max-width: 520px;
          width: 100%;
        }
        h1 {
          font-size: 28px;
          margin-bottom: 8px;
        }
        .subtitle {
          font-size: 14px;
          color: #9ca3af;
          margin-bottom: 20px;
        }
        ul { list-style: none; margin-top: 16px; }
        li + li { margin-top: 10px; }
        a.btn {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          padding: 10px 18px;
          border-radius: 999px;
          background: #2563eb;
          color: white;
          text-decoration: none;
          font-size: 14px;
          font-weight: 500;
          transition: background 0.15s, transform 0.1s, box-shadow 0.1s;
          box-shadow: 0 12px 30px rgba(37, 99, 235, 0.35);
        }
        a.btn:hover {
          background: #1d4ed8;
          transform: translateY(-1px);
          box-shadow: 0 16px 40px rgba(37, 99, 235, 0.45);
        }
        a.btn-outline {
          background: transparent;
          border: 1px solid #4b5563;
          box-shadow: none;
        }
        a.btn-outline:hover {
          background: rgba(55, 65, 81, 0.5);
        }
        .btn-row {
          display: flex;
          gap: 10px;
          margin-top: 18px;
        }
        .uml {
          margin-top: 14px;
          font-size: 13px;
          color: #9ca3af;
        }
        .uml span {
          display: inline-block;
          margin-top: 4px;
          padding: 4px 10px;
          border-radius: 999px;
          background: rgba(15, 23, 42, 0.9);
          border: 1px solid rgba(75, 85, 99, 0.7);
          font-size: 12px;
        }

        /* добавили стиль для ссылки "Выйти" */
        .top-logout {
          position: absolute;
          right: 32px;
          top: 24px;
          font-size: 14px;
          color: #9ca3af;
          text-decoration: none;
          transition: color .2s;
        }
        .top-logout:hover {
          color: #ffffff;
        }
      </style>
    </head>
    <body>
      <!-- добавили ссылку выхода сразу после <body> -->
      <a href="/logout" class="top-logout">Выйти</a>

      <div class="card">
        <h1>VideoConference MVP</h1>
        <p class="subtitle">
          Прототип системы видеоконференций: регистрация, проверка устройств, лобби и вход в конференцию.
        </p>

        <div class="btn-row">
          <a href="/register" class="btn">Регистрация</a>
          <a href="/login" class="btn btn-outline">Вход</a>
        </div>

        <div class="uml">
          UML-состав:&nbsp;
          <span>User, Host, ClientApp, AuthService, DeviceCheck, Lobby, Conference, UserStatus</span>
        </div>
      </div>
    </body>
    </html>
    """



@app.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    error = request.query_params.get("error")

    error_block = ""
    if error == "1":
        error_block = """
        <div class="error-banner">
          Пользователь с таким именем уже существует
        </div>
        """

    return """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
      <meta charset="UTF-8">
      <title>Регистрация — VideoConference MVP</title>
      <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          background: radial-gradient(circle at top, #2563eb, #020617 55%);
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          color: #e5e7eb;
        }
        .card {
          background: rgba(15, 23, 42, 0.95);
          padding: 32px 36px;
          border-radius: 24px;
          box-shadow: 0 28px 90px rgba(15, 23, 42, 0.95);
          max-width: 460px;
          width: 100%;
        }
        h2 { font-size: 26px; margin-bottom: 6px; }
        .subtitle {
          font-size: 13px;
          color: #9ca3af;
          margin-bottom: 20px;
        }
        label {
          display: block;
          font-size: 13px;
          margin-bottom: 6px;
        }
        input, select {
          width: 100%;
          padding: 9px 11px;
          border-radius: 12px;
          border: 1px solid #1f2937;
          background: #020617;
          color: #e5e7eb;
          font-size: 14px;
          margin-bottom: 14px;
        }
        input:focus, select:focus {
          outline: none;
          border-color: #3b82f6;
          box-shadow: 0 0 0 1px #3b82f6;
        }
        button {
          width: 100%;
          padding: 11px 0;
          border-radius: 999px;
          border: none;
          background: #3b82f6;
          color: #e5f2ff;
          font-weight: 600;
          font-size: 14px;
          cursor: pointer;
          transition: background 0.15s, transform 0.1s, box-shadow 0.1s;
          box-shadow: 0 16px 40px rgba(59, 130, 246, 0.45);
          margin-top: 4px;
        }
        button:hover {
          background: #2563eb;
          transform: translateY(-1px);
          box-shadow: 0 20px 52px rgba(37, 99, 235, 0.6);
        }
        .link {
          margin-top: 16px;
          font-size: 13px;
          text-align: center;
          color: #9ca3af;
        }
        .link a {
          color: #60a5fa;
          text-decoration: none;
        }
        .link a:hover { text-decoration: underline; }
      </style>
    </head>
    <body>
      <div class="card">
        <h2>Регистрация</h2>
        <p class="subtitle">
          Создайте учётную запись участника или ведущего, чтобы подключаться к видеоконференциям.
        </p>

        <form action="/register" method="post">
          <label>Имя пользователя</label>
          <input type="text" name="username" required>

          <label>Пароль</label>
          <input type="password" name="password" required>

          <label>Роль</label>
          <select name="role">
            <option value="user">Участник</option>
            <option value="host">Ведущий (Host)</option>
          </select>

          <button type="submit">Зарегистрироваться</button>
        </form>

        <p class="link">
          Уже есть аккаунт?
          <a href="/login">Войти</a>
        </p>
      </div>
    </body>
    </html>
    """


@app.post("/register")
async def register(
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form("user"),
):
    global next_user_id, conference

    if username in users_by_name:
            return RedirectResponse(
                url="/register?error=1",
                status_code=303
            )

    is_host = (role == "host")
    user = User(
        id=next_user_id,
        username=username,
        password=password,
        is_host=is_host,
    )
    next_user_id += 1

    users_by_name[username] = user
    users_by_id[user.id] = user

     # Назначаем первого host'а ведущим конференции
    if is_host and conference.host_id == -1:
        conference.host_id = user.id

    # Логируем факт регистрации
    log_event(
        "register",
        actor_id=user.id,
        details=f"role={'host' if is_host else 'user'}",
    )

    return RedirectResponse(url="/login", status_code=303)


def render_login_page(error: Optional[str] = None) -> str:
    error_block = ""
    if error:
        error_block = f"""
        <div class="alert">
          <span>{error}</span>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8" />
        <title>Вход — VideoConference MVP</title>
        <style>
          * {{ box-sizing: border-box; margin: 0; padding: 0; }}
          body {{
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: radial-gradient(circle at top, #0ea5e9, #020617 55%);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            color: #e5e7eb;
          }}
          .card {{
            background: rgba(15, 23, 42, 0.96);
            padding: 32px 40px;
            border-radius: 24px;
            box-shadow: 0 28px 80px rgba(15, 23, 42, 0.9);
            width: 420px;
          }}
          h2 {{
            font-size: 26px;
            margin-bottom: 6px;
          }}
          .subtitle {{
            font-size: 14px;
            color: #9ca3af;
            margin-bottom: 20px;
          }}
          label {{
            display: block;
            font-size: 14px;
            margin-bottom: 6px;
          }}
          input[type="text"],
          input[type="password"] {{
            width: 100%;
            padding: 10px 12px;
            border-radius: 999px;
            border: 1px solid rgba(148, 163, 184, 0.7);
            background: rgba(15, 23, 42, 0.9);
            color: #e5e7eb;
            font-size: 14px;
            outline: none;
            margin-bottom: 14px;
          }}
          input[type="text"]:focus,
          input[type="password"]:focus {{
            border-color: #38bdf8;
          }}
          button {{
            width: 100%;
            padding: 11px 0;
            border-radius: 999px;
            border: none;
            background: #38bdf8;
            color: #0f172a;
            font-weight: 600;
            font-size: 15px;
            cursor: pointer;
            box-shadow: 0 16px 40px rgba(56, 189, 248, 0.45);
            transition: background 0.15s, transform 0.1s, box-shadow 0.1s;
            margin-top: 4px;
          }}
          button:hover {{
            background: #0ea5e9;
            transform: translateY(-1px);
            box-shadow: 0 20px 55px rgba(56, 189, 248, 0.55);
          }}
          .footer-text {{
            margin-top: 14px;
            font-size: 13px;
            color: #9ca3af;
            text-align: center;
          }}
          .footer-text a {{
            color: #38bdf8;
            text-decoration: none;
          }}
          .footer-text a:hover {{
            text-decoration: underline;
          }}
          .alert {{
            margin-bottom: 14px;
            padding: 9px 12px;
            border-radius: 10px;
            background: rgba(239, 68, 68, 0.16);
            border: 1px solid rgba(248, 113, 113, 0.7);
            color: #fecaca;
            font-size: 13px;
          }}
        </style>
    </head>
    <body>
      <div class="card">
        <h2>Вход</h2>
        <p class="subtitle">Введите имя пользователя и пароль, указанные при регистрации.</p>

        {error_block}

        <form action="/login" method="post">
          <label>Имя пользователя</label>
          <input type="text" name="username" required />

          <label>Пароль</label>
          <input type="password" name="password" required />

          <button type="submit">Войти</button>
        </form>

        <div class="footer-text">
          Нет аккаунта? <a href="/register">Зарегистрироваться</a>
        </div>
      </div>
    </body>
    </html>
    """


@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    # читаем параметр ?error=1 из URL
    error_code = request.query_params.get("error")
    error_msg = None
    if error_code == "1":
        error_msg = "Неверное имя пользователя или пароль"

    return HTMLResponse(render_login_page(error_msg))


@app.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
):
    user = users_by_name.get(username)

    if not user or user.password != password:
        # пишем в журнал неудачную попытку
        save_event(
            "login_failed",
            username=username,
            details="Неверное имя пользователя или пароль",
        )
        # возвращаемся на форму с ошибкой
        return RedirectResponse(
            url="/login?error=1",
            status_code=303
        )

    # успешный вход
    session_id = secrets.token_hex(16)
    sessions[session_id] = user.id
    user.status = UserStatus.OFFLINE

    save_event(
        "login_success",
        username=user.username,
        details="Успешная авторизация",
    )

    response = RedirectResponse(url="/device-check", status_code=303)
    response.set_cookie("session_id", session_id, httponly=True)
    return response


@app.get("/logout")
async def logout(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id and session_id in sessions:
        user_id = sessions.pop(session_id)
        user = users_by_id.get(user_id)
        if user:
            user.status = UserStatus.OFFLINE
            # логируем один раз
            log_event("logout", actor_id=user.id)
            # убираем из списков конференции
            if user.id in conference.waiting_room:
                conference.waiting_room.remove(user.id)
            if user.id in conference.participants:
                conference.participants.remove(user.id)

    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("session_id")
    return response

# ====== DeviceCheck (из UML) ======

@app.get("/device-check", response_class=HTMLResponse)
async def device_check(request: Request):
    user = get_current_user(request)

    return f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
      <meta charset="UTF-8">
      <title>Проверка устройств — VideoConference MVP</title>
      <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          background: radial-gradient(circle at top, #a855f7, #020617 55%);
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          color: #e5e7eb;
        }}
        .card {{
          background: rgba(15, 23, 42, 0.95);
          padding: 28px 32px;
          border-radius: 20px;
          box-shadow: 0 24px 80px rgba(15, 23, 42, 0.9);
          max-width: 460px;
          width: 100%;
        }}
        h2 {{ font-size: 24px; margin-bottom: 8px; }}
        .subtitle {{ font-size: 13px; color: #9ca3af; margin-bottom: 18px; }}
        .user {{
          font-size: 14px;
          margin-bottom: 18px;
        }}
        .status {{
          display: inline-flex;
          align-items: center;
          gap: 6px;
          padding: 6px 10px;
          border-radius: 999px;
          background: rgba(76, 29, 149, 0.8);
          font-size: 12px;
          margin-bottom: 16px;
        }}
        .status-dot {{
          width: 8px;
          height: 8px;
          border-radius: 999px;
          background: #fde68a;
          box-shadow: 0 0 8px rgba(253, 230, 138, 0.9);
        }}
        button {{
          width: 100%;
          padding: 10px 0;
          border-radius: 999px;
          border: none;
          background: #a855f7;
          color: #040016;
          font-weight: 600;
          font-size: 14px;
          cursor: pointer;
          transition: background 0.15s, transform 0.1s, box-shadow 0.1s;
          box-shadow: 0 12px 30px rgba(168, 85, 247, 0.35);
          margin-top: 8px;
        }}
        button:hover {{
          background: #9333ea;
          transform: translateY(-1px);
          box-shadow: 0 16px 40px rgba(168, 85, 247, 0.45);
        }}
        .hint {{
          font-size: 12px;
          color: #9ca3af;
          margin-top: 10px;
        }}

        /* КНОПКА ВЫХОДА */
        .top-logout {{
          position: absolute;
          right: 24px;
          top: 20px;
          font-size: 14px;
          color: #9ca3af;
          text-decoration: none;
          transition: color .2s;
        }}
        .top-logout:hover {{
          color: #ffffff;
        }}
      </style>
    </head>
    <body>
      <!-- ССЫЛКА ВЫХОДА СРАЗУ ПОСЛЕ <body> -->
      <a href="/logout" class="top-logout">Выйти</a>

      <div class="card">
        <h2>Проверка устройств</h2>
        <p class="subtitle">Этап перед входом в лобби и конференцию.</p>

        <p class="user">Пользователь: <b>{user.username}</b></p>

        <div class="status">
          <span class="status-dot"></span>
          <span>Камера и микрофон: псевдо-проверка (для прототипа)</span>
        </div>

        <button onclick="startCheck()">Запустить проверку</button>

        <p class="hint">
          В реальной системе здесь выполнялась бы фактическая проверка доступа к камере и микрофону (WebRTC).
        </p>

        <script>
          function startCheck() {{
            setTimeout(() => {{
              alert("Псевдо-проверка устройств прошла успешно. Переходим в лобби.");
              window.location.href = "/lobby";
            }}, 400);
          }}
        </script>
      </div>
    </body>
    </html>
    """


# ====== Lobby / Conference (UML: Conference, Lobby, Host, User) ======

class LobbyManager:
    def __init__(self):
        # user_id -> WebSocket
        self.active_connections: Dict[int, WebSocket] = {}
        self.host_ws: Optional[WebSocket] = None

    async def connect(self, user: User, websocket: WebSocket):
      await websocket.accept()
      self.active_connections[user.id] = websocket

      if user.is_host:
          self.host_ws = websocket
          # ведущий зашёл в лобби
          log_event("host_join_lobby", actor_id=user.id)
          await self.send_waiting_list()
      else:
          # обычный участник заходит в лобби → в ожидание
          user.status = UserStatus.IN_LOBBY
          if user.id not in conference.waiting_room:
              conference.waiting_room.append(user.id)
          log_event("user_join_lobby", actor_id=user.id)
          await self.send_waiting_list()

    async def disconnect(self, user: User):
        ws = self.active_connections.pop(user.id, None)
        if user.is_host and self.host_ws is ws:
            self.host_ws = None

        # Убираем из очереди и участников
        if user.id in conference.waiting_room:
            conference.waiting_room.remove(user.id)
        if user.id in conference.participants:
            conference.participants.remove(user.id)

        user.status = UserStatus.OFFLINE
        log_event("user_disconnect", actor_id=user.id)

        await self.send_waiting_list()

    async def send_waiting_list(self):
        """Отправить ведущему список ожидающих."""
        if not self.host_ws:
            return
        data = {
            "type": "waiting_list",
            "users": [
                {"id": uid, "username": users_by_id[uid].username}
                for uid in conference.waiting_room
            ]
        }
        await self.host_ws.send_json(data)

    async def admit(self, user_id: int):
      if user_id in conference.waiting_room:
        conference.waiting_room.remove(user_id)
      if user_id not in conference.participants:
        conference.participants.append(user_id)

      user = users_by_id[user_id]
      user.status = UserStatus.IN_CONFERENCE

      ws = self.active_connections.get(user_id)
      if ws:
        await ws.send_json({"type": "admitted"})

      log_event("user_admitted", actor_id=user_id)

      await self.send_waiting_list()

    async def reject(self, user_id: int):
      if user_id in conference.waiting_room:
          conference.waiting_room.remove(user_id)

      user = users_by_id[user_id]
      user.status = UserStatus.OFFLINE

      ws = self.active_connections.get(user_id)
      if ws:
          await ws.send_json({"type": "rejected"})

      log_event("user_rejected", actor_id=user_id)

      await self.send_waiting_list()


lobby_manager = LobbyManager()


@app.get("/lobby", response_class=HTMLResponse)
async def lobby_page(request: Request):
    user = get_current_user(request)
    is_host_js = "true" if user.is_host else "false"

    html = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
      <meta charset="UTF-8">
      <title>Лобби — VideoConference MVP</title>
      <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          background: radial-gradient(circle at top, #f97316, #020617 55%);
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          color: #e5e7eb;
        }
        .shell {
          max-width: 860px;
          width: 100%;
          padding: 24px;
        }
        .top {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 18px;
        }
        .tag {
          font-size: 12px;
          padding: 4px 10px;
          border-radius: 999px;
          border: 1px solid rgba(148, 163, 184, 0.6);
          color: #e5e7eb;
          background: rgba(15, 23, 42, 0.9);
        }
        .role {
          font-size: 13px;
          color: #9ca3af;
        }
        h2 { font-size: 24px; margin-bottom: 4px; }
        .wrapper {
          display: grid;
          grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr);
          gap: 18px;
        }
        .panel {
          background: rgba(15, 23, 42, 0.95);
          border-radius: 18px;
          padding: 18px 20px;
          box-shadow: 0 20px 60px rgba(15, 23, 42, 0.85);
        }
        .panel h3 {
          font-size: 16px;
          margin-bottom: 6px;
        }
        .panel p {
          font-size: 13px;
          color: #9ca3af;
          margin-bottom: 12px;
        }
        #waiting-list {
          margin-top: 6px;
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        .user-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 8px 10px;
          border-radius: 12px;
          background: rgba(30, 64, 175, 0.15);
        }
        .user-name {
          font-size: 14px;
        }
        .btns {
          display: flex;
          gap: 6px;
        }
        button.small {
          padding: 6px 10px;
          border-radius: 999px;
          border: none;
          font-size: 12px;
          cursor: pointer;
          transition: background 0.1s, transform 0.08s;
        }
        button.small:active {
          transform: translateY(1px);
        }
        .btn-admit {
          background: #22c55e;
          color: #02140b;
        }
        .btn-admit:hover {
          background: #16a34a;
        }
        .btn-reject {
          background: #ef4444;
          color: #fee2e2;
        }
        .btn-reject:hover {
          background: #dc2626;
        }
        .user-wait {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        .dot {
          width: 8px;
          height: 8px;
          border-radius: 999px;
          background: #f97316;
          box-shadow: 0 0 10px rgba(248, 171, 88, 0.9);
        }
        .wait-row {
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .wait-text {
          font-size: 13px;
          color: #9ca3af;
        }

        /* КНОПКА "ВЫЙТИ" */
        .top-logout {
          position: absolute;
          right: 24px;
          top: 20px;
          font-size: 14px;
          color: #9ca3af;
          text-decoration: none;
          transition: color .2s;
        }
        .top-logout:hover {
          color: #ffffff;
        }
      </style>
    </head>
    <body>
      <!-- ССЫЛКА ВЫХОДА -->
      <a href="/logout" class="top-logout">Выйти</a>

      <div class="shell">
        <div class="top">
          <div>
            <div class="tag">Лобби конференции</div>
            <h2>Подключение к встрече</h2>
            <div class="role">Вы вошли как: <b>{{USERNAME}}</b> ({{ROLE}})</div>
          </div>
        </div>

        <div class="wrapper">
          <div id="host-panel" class="panel" style="display:none;">
            <h3>Панель ведущего</h3>
            <p>Здесь отображаются пользователи, ожидающие входа в конференцию.</p>
            <div id="waiting-list"></div>
          </div>

          <div id="user-panel" class="panel" style="display:none;">
            <h3>Ожидание решения ведущего</h3>
            <div class="user-wait">
              <div class="wait-row">
                <div class="dot"></div>
                <div class="wait-text">
                  Вы находитесь в лобби. Пожалуйста, дождитесь, пока ведущий вас впустит или отклонит.
                </div>
              </div>
              <p class="wait-text">
                Окно можно оставить открытым: после решения ведущего произойдёт автоматический переход.
              </p>
            </div>
          </div>
        </div>
      </div>

      <script>
        const IS_HOST = {{IS_HOST}};

        if (IS_HOST) {
          document.getElementById("host-panel").style.display = "block";
        } else {
          document.getElementById("user-panel").style.display = "block";
        }

        const ws = new WebSocket(`ws://${location.host}/ws/lobby`);

        ws.onmessage = (event) => {
          const msg = JSON.parse(event.data);
          if (msg.type === "waiting_list" && IS_HOST) {
            const container = document.getElementById("waiting-list");
            container.innerHTML = "";
            msg.users.forEach(u => {
              const row = document.createElement("div");
              row.className = "user-row";

              const span = document.createElement("span");
              span.className = "user-name";
              span.textContent = u.username + " (id=" + u.id + ")";

              const btns = document.createElement("div");
              btns.className = "btns";

              const admitBtn = document.createElement("button");
              admitBtn.className = "small btn-admit";
              admitBtn.textContent = "Впустить";
              admitBtn.onclick = () => {
                ws.send(JSON.stringify({action: "admit", user_id: u.id}));
              };

              const rejectBtn = document.createElement("button");
              rejectBtn.className = "small btn-reject";
              rejectBtn.textContent = "Отклонить";
              rejectBtn.onclick = () => {
                ws.send(JSON.stringify({action: "reject", user_id: u.id}));
              };

              btns.appendChild(admitBtn);
              btns.appendChild(rejectBtn);

              row.appendChild(span);
              row.appendChild(btns);

              container.appendChild(row);
            });
          } else if (msg.type === "admitted" && !IS_HOST) {
            alert("Вас впустили в конференцию");
            window.location.href = "/conference";
          } else if (msg.type === "rejected" && !IS_HOST) {
            alert("Вход в конференцию отклонён ведущим");
          }
        };

        ws.onclose = () => {
          console.log("WebSocket закрыт");
        };
      </script>
    </body>
    </html>
    """

    html = (
        html.replace("{{USERNAME}}", user.username)
            .replace("{{ROLE}}", "Host" if user.is_host else "User")
            .replace("{{IS_HOST}}", is_host_js)
    )

    return HTMLResponse(html)


@app.websocket("/ws/lobby")
async def lobby_ws(websocket: WebSocket, session_id: Optional[str] = Cookie(None)):
    if not session_id or session_id not in sessions:
        await websocket.close(code=4401)
        return

    user_id = sessions[session_id]
    user = users_by_id[user_id]

    await lobby_manager.connect(user, websocket)

    try:
        while True:
            data = await websocket.receive_json()
            if user.is_host:
                action = data.get("action")
                target_id = data.get("user_id")
                if not isinstance(target_id, int):
                    continue
                if action == "admit":
                    await lobby_manager.admit(target_id)
                elif action == "reject":
                    await lobby_manager.reject(target_id)
            else:
                # участник в этом MVP не отправляет сообщений
                pass
    except WebSocketDisconnect:
        await lobby_manager.disconnect(user)

# ====== Простой текстовый чат в конференции ======

conference_chat_connections: Dict[int, WebSocket] = {}

@app.websocket("/ws/conference-chat")
async def conference_chat_ws(websocket: WebSocket, session_id: Optional[str] = Cookie(None)):
    if not session_id or session_id not in sessions:
        await websocket.close(code=4401)
        return

    user_id = sessions[session_id]
    user = users_by_id[user_id]

    # разрешаем чат только тем, кто уже в конференции
    if user.status != UserStatus.IN_CONFERENCE:
        await websocket.close(code=4403)
        return

    await websocket.accept()
    conference_chat_connections[user_id] = websocket

    try:
        while True:
            text = await websocket.receive_text()
            msg = text.strip()
            if not msg:
                continue

            payload = {
                "type": "chat",
                "from": user.username,
                "message": msg,
            }

            # логируем сообщение в БД (если уже добавил save_event/log_event – тут вызываешь)
            # save_event("chat", username=user.username, details=msg)

            # рассылаем всем подключённым участникам
            dead_ids = []
            for uid, ws in conference_chat_connections.items():
                try:
                    await ws.send_json(payload)
                except Exception:
                    dead_ids.append(uid)
            for uid in dead_ids:
                conference_chat_connections.pop(uid, None)
    except WebSocketDisconnect:
        conference_chat_connections.pop(user_id, None)


@app.get("/conference", response_class=HTMLResponse)
async def conference_page(request: Request):
    user = get_current_user(request)

    if user.status != UserStatus.IN_CONFERENCE:
        return HTMLResponse(
            "Вы ещё не были допущены в конференцию ведущим.",
            status_code=403
        )

    # список участников по идентификаторам
    participant_names = [
        users_by_id[uid].username
        for uid in conference.participants
        if uid in users_by_id
    ]
    participants_html = "".join(
        f"<li>{name}</li>" for name in participant_names
    ) or "<li>Список пока пуст</li>"

    role_label = "Host" if user.is_host else "User"

    # блок с событиями для ведущего
    host_events_block = ""
    if user.is_host:
        events = []
        for ts, event_type, username, details in get_last_events(15):
            base = f"{ts}: "

            if event_type == "login_success":
                text = base + f"успешный вход пользователя {username}"
            elif event_type == "login_failed":
                text = base + f"неудачная попытка входа (имя: {username})"
            elif event_type == "register":
                text = base + f"регистрация пользователя {username} ({details or ''})"
            elif event_type == "user_join_lobby":
                text = base + f"{username} вошёл в лобби"
            elif event_type == "host_join_lobby":
                text = base + "ведущий вошёл в лобби"
            elif event_type == "user_admitted":
                text = base + f"пользователь {username} допущен в конференцию"
            elif event_type == "user_rejected":
                text = base + f"пользователю {username} отказано во входе"
            elif event_type == "logout":
                text = base + f"{username} вышел из системы"
            else:
                text = base + f"{event_type} ({username or '-'}) — {details or ''}"

            events.append(f"<li>{text}</li>")

        rows_html = "".join(events) if events else "<li>Пока нет событий</li>"

        host_events_block = f"""
          <div class="section">
            <div class="section-title">Последние события конференции</div>
            <ul class="events-list">
              {rows_html}
            </ul>
          </div>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="ru">
      <head>
        <meta charset="utf-8" />
        <title>Конференция — VideoConference MVP</title>
        <style>
          * {{ box-sizing: border-box; margin: 0; padding: 0; }}
          body {{
              margin: 0;
              min-height: 100vh;
              font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
              color: #e5e7eb;
              background: radial-gradient(circle at top, #16a34a 0, #020617 55%);
              display: flex;
              align-items: center;
              justify-content: center;
          }}
          .card {{
              background: rgba(15,23,42,0.96);
              border-radius: 32px;
              padding: 32px 40px;
              box-shadow: 0 30px 80px rgba(0,0,0,0.6);
              max-width: 960px;
              width: 92%;
          }}
          .title {{
              font-size: 32px;
              font-weight: 700;
              margin-bottom: 8px;
          }}
          .subtitle {{
              font-size: 16px;
              color: #9ca3af;
              margin-bottom: 20px;
          }}
          .badge {{
              display: inline-block;
              padding: 4px 12px;
              border-radius: 999px;
              font-size: 12px;
              background: rgba(34,197,94,0.15);
              color: #4ade80;
              border: 1px solid rgba(34,197,94,0.4);
              margin-left: 8px;
          }}
          .sections {{
              display: grid;
              grid-template-columns: minmax(0, 1.1fr) minmax(0, 1.1fr);
              gap: 24px;
          }}
          .section-title {{
              font-weight: 600;
              margin-bottom: 8px;
          }}
          ul {{
              margin: 0;
              padding-left: 20px;
              font-size: 14px;
          }}
          .events-list {{
              max-height: 220px;
              overflow-y: auto;
              padding-right: 8px;
          }}
          .bottom-text {{
              margin-top: 20px;
              color:#9ca3af;
              font-size: 13px;
          }}
          .back-btn {{
              margin-top: 24px;
              display: inline-flex;
              align-items: center;
              justify-content: center;
              padding: 10px 24px;
              border-radius: 999px;
              border: none;
              background: #22c55e;
              color: #0f172a;
              font-size: 15px;
              font-weight: 600;
              cursor: pointer;
              text-decoration: none;
          }}
          .back-btn:hover {{
              filter: brightness(1.05);
          }}
          .top-logout {{
              position: absolute;
              right: 32px;
              top: 24px;
              font-size: 14px;
              color: #9ca3af;
              text-decoration: none;
              transition: color .2s;
          }}
          .top-logout:hover {{
              color: #ffffff;
          }}
          /* чат */
          .chat-box {{
              border-radius: 16px;
              background: rgba(15,23,42,0.9);
              border: 1px solid rgba(148,163,184,0.35);
              padding: 10px 12px;
              height: 200px;
              overflow-y: auto;
              font-size: 13px;
          }}
          .chat-msg {{
              margin-bottom: 6px;
          }}
          .chat-msg-own .chat-author {{
              color: #4ade80;
          }}
          .chat-author {{
              font-weight: 600;
              margin-right: 4px;
          }}
          .chat-form {{
              display: flex;
              gap: 8px;
              margin-top: 8px;
          }}
          .chat-input {{
              flex: 1;
              padding: 8px 10px;
              border-radius: 999px;
              border: 1px solid rgba(148,163,184,0.6);
              background: rgba(15,23,42,0.9);
              color: #e5e7eb;
              font-size: 13px;
          }}
          .chat-send {{
              padding: 8px 16px;
              border-radius: 999px;
              border: none;
              background: #22c55e;
              color: #022c16;
              font-weight: 600;
              font-size: 13px;
              cursor: pointer;
          }}
          /* локальный предпросмотр видео */
          .video-block {{
              margin-top: 10px;
              border-radius: 18px;
              background: rgba(15,23,42,0.9);
              border: 1px solid rgba(148,163,184,0.35);
              padding: 10px 12px;
          }}
          .video-row {{
              display: flex;
              flex-direction: column;
              gap: 8px;
          }}
          #localVideo {{
              width: 100%;
              border-radius: 12px;
              background: #020617;
          }}
          .video-btn {{
              align-self: flex-start;
              padding: 6px 16px;
              border-radius: 999px;
              border: none;
              background: #10b981;
              color: #022c22;
              font-size: 13px;
              font-weight: 600;
              cursor: pointer;
          }}
          .subtle {{
              font-size: 12px;
              color: #9ca3af;
              margin-top: 4px;
          }}
          @media (max-width: 900px) {{
              .sections {{
                  grid-template-columns: minmax(0, 1fr);
              }}
          }}
        </style>
      </head>
      <body>
        <a href="/logout" class="top-logout">Выйти</a>
        <div class="card">
          <div class="title">Конференция</div>
          <div class="subtitle">
            Пользователь: <b>{user.username}</b>
            <span class="badge">{role_label}</span>
          </div>

          <div class="sections">
            <div class="section">
              <div class="section-title">Текущие участники конференции:</div>
              <ul>
                {participants_html}
              </ul>

              <div class="video-block">
                <div class="section-title">Локальный предпросмотр камеры</div>
                <div class="video-row">
                  <video id="localVideo" autoplay playsinline muted></video>
                  <button id="startVideo" class="video-btn">Включить камеру</button>
                </div>
                <p class="subtle">
                  Поток не отправляется другим участникам и используется только как демонстрация работы с WebRTC (getUserMedia).
                </p>
              </div>
            </div>

            <div class="section">
              <div class="section-title">Чат конференции</div>
              <div id="chat-messages" class="chat-box"></div>
              <form id="chat-form" class="chat-form">
                <input id="chat-input" class="chat-input"
                       type="text"
                       placeholder="Напишите сообщение и нажмите Enter..."
                       autocomplete="off" />
                <button type="submit" class="chat-send">Отправить</button>
              </form>

              {host_events_block}
            </div>
          </div>

          <p class="bottom-text">
            В данном прототипе реализована ключевая логика доступа: регистрация → проверка устройств → лобби → допуск ведущим → конференция.
            Дополнительно добавлены текстовый чат, журнал событий и локальный предпросмотр камеры как шаг к интеграции полной видеосвязи (WebRTC).
          </p>

          <a href="/lobby" class="back-btn">Назад в лобби</a>
        </div>

        <script>
          // подключение к WebSocket-чату
          const chatBox = document.getElementById("chat-messages");
          const chatForm = document.getElementById("chat-form");
          const chatInput = document.getElementById("chat-input");
          let chatSocket = null;

          function appendMessage(author, text, isOwn) {{
            const div = document.createElement("div");
            div.className = "chat-msg" + (isOwn ? " chat-msg-own" : "");
            const a = document.createElement("span");
            a.className = "chat-author";
            a.textContent = author + ":";
            const t = document.createElement("span");
            t.className = "chat-text";
            t.textContent = " " + text;
            div.appendChild(a);
            div.appendChild(t);
            chatBox.appendChild(div);
            chatBox.scrollTop = chatBox.scrollHeight;
          }}

          function initChat() {{
            chatSocket = new WebSocket(`ws://${{location.host}}/ws/conference-chat`);
            chatSocket.onmessage = (ev) => {{
              const msg = JSON.parse(ev.data);
              if (msg.type === "chat") {{
                const isOwn = msg.from === "{user.username}";
                appendMessage(msg.from, msg.message, isOwn);
              }}
            }};
          }}

          chatForm.addEventListener("submit", (e) => {{
            e.preventDefault();
            if (!chatSocket || chatSocket.readyState !== WebSocket.OPEN) return;
            const text = chatInput.value.trim();
            if (!text) return;
            chatSocket.send(text);
            chatInput.value = "";
          }});

          // локальный предпросмотр камеры
          const startVideoBtn = document.getElementById("startVideo");
          const localVideo = document.getElementById("localVideo");

          if (startVideoBtn && localVideo && navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {{
            startVideoBtn.addEventListener("click", async () => {{
              try {{
                const stream = await navigator.mediaDevices.getUserMedia({{ video: true, audio: true }});
                localVideo.srcObject = stream;
                startVideoBtn.textContent = "Камера включена";
                startVideoBtn.disabled = true;
              }} catch (err) {{
                alert("Не удалось получить доступ к камере/микрофону: " + err);
              }}
            }});
          }}

          window.addEventListener("load", initChat);
        </script>
      </body>
    </html>
    """

@app.get("/events", response_class=HTMLResponse)
async def events_page():
    rows = get_last_events(100)

    # собираем строки таблицы
    trs = ""
    for ts, event_type, username, details in rows:
        trs += f"""
        <tr>
          <td>{ts}</td>
          <td>{event_type}</td>
          <td>{username or "-"}</td>
          <td>{details or "-"}</td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
      <meta charset="UTF-8">
      <title>Журнал событий — VideoConference MVP</title>
      <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          background: radial-gradient(circle at top, #020617, #020617 55%);
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          color: #e5e7eb;
        }}
        .card {{
          background: rgba(15, 23, 42, 0.96);
          padding: 24px 28px;
          border-radius: 18px;
          box-shadow: 0 24px 80px rgba(0, 0, 0, 0.7);
          max-width: 900px;
          width: 95%;
        }}
        h2 {{ font-size: 22px; margin-bottom: 12px; }}
        table {{
          width: 100%;
          border-collapse: collapse;
          font-size: 13px;
        }}
        th, td {{
          padding: 6px 8px;
          border-bottom: 1px solid rgba(55, 65, 81, 0.7);
        }}
        th {{
          text-align: left;
          color: #9ca3af;
          font-weight: 500;
        }}
        tr:nth-child(even) td {{
          background: rgba(15, 23, 42, 0.8);
        }}
        .badge {{
          display: inline-block;
          padding: 2px 8px;
          border-radius: 999px;
          background: rgba(30, 64, 175, 0.3);
          border: 1px solid rgba(59,130,246,0.5);
          font-size: 11px;
          margin-left: 6px;
        }}
        .top-row {{
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 10px;
        }}
        a.back {{
          font-size: 13px;
          color: #60a5fa;
          text-decoration: none;
        }}
        a.back:hover {{ text-decoration: underline; }}
      </style>
    </head>
    <body>
      <div class="card">
        <div class="top-row">
          <h2>Журнал событий<span class="badge">debug / отчёт</span></h2>
          <a href="/" class="back">На главную</a>
        </div>
        <table>
          <thead>
            <tr>
              <th>Время (UTC)</th>
              <th>Событие</th>
              <th>Пользователь</th>
              <th>Детали</th>
            </tr>
          </thead>
          <tbody>
            {trs}
          </tbody>
        </table>
      </div>
    </body>
    </html>
    """
    return HTMLResponse(html)



# запуск: uvicorn vc_app:app --reload
