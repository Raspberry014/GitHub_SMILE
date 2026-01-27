import os
import time
import argparse
import importlib
import shutil

# импортируем модуль целиком (важно! будем заменять его render)
import arena

# ---- настройки анимации (по умолчанию можно менять флагами) ----
DEFAULT_SPEED = 0.15   # секунд паузы между ходами
USE_BOLD = True        # слегка выделять ботов жирным (ANSI), если терминал поддерживает

# ---- утилиты ----
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def term_supports_ansi() -> bool:
    # простая эвристика: если stdout — tty и не "dumb"
    return os.isatty(1) and os.environ.get("TERM", "") not in ("", "dumb")

def style_bold(s: str) -> str:
    if USE_BOLD and term_supports_ansi():
        return f"\x1b[1m{s}\x1b[0m"
    return s

def box_width():
    # ширина окна с учётом сетки 10x10 и пробелов
    return 2 * arena.W - 1

def hr():
    return "+" + "-" * box_width() + "+"

# ---- наш анимированный рендер ----
def animated_render(grid, posA, posB, scoreA, scoreB, turn, *, speed=DEFAULT_SPEED):
    rA, cA = posA
    rB, cB = posB

    # копия сетки и расставляем ботов
    g = [row[:] for row in grid]
    g[rA][cA] = "A"
    g[rB][cB] = "B"

    # попытка сделать «без мерцания» — сначала построим строку, потом одним принтом
    out_lines = []
    out_lines.append(f"Turn {turn:>2}  |  A:{scoreA}  B:{scoreB}")
    out_lines.append(hr())
    for r in range(arena.H):
        row_chars = []
        for c in range(arena.W):
            ch = g[r][c]
            if ch == "A":
                row_chars.append(style_bold("A"))
            elif ch == "B":
                row_chars.append(style_bold("B"))
            elif ch == arena.CellWall:
                row_chars.append("#")
            elif ch == arena.CellFood:
                row_chars.append("*")
            else:
                row_chars.append(".")
        out_lines.append("|" + " ".join(row_chars) + "|")
    out_lines.append(hr())

    clear_screen()
    print("\n".join(out_lines))
    time.sleep(speed)

# ---- запуск матча с подменой рендера ----
def run_game(speed: float, seed: int | None, botA: str, botB: str):
    """
    speed — пауза между кадрами
    seed  — фиксированный сид карты; если None, используется сид из arena.SEED
    botA/botB — 'my' | 'greedy' | 'random'
    """
    # подменяем render внутри модуля arena
    def _patched_render(grid, posA, posB, scoreA, scoreB, turn):
        animated_render(grid, posA, posB, scoreA, scoreB, turn, speed=speed)

    arena.render = _patched_render

    # выбираем ботов
    bot_map = {
        "my": arena.my_bot_decide,
        "greedy": arena.greedy_bot_decide,
        "random": arena.random_bot_decide,
    }
    botA_fn = bot_map.get(botA, arena.my_bot_decide)
    botB_fn = bot_map.get(botB, arena.greedy_bot_decide)

    # запускаем
    print("Старт анимации. Нажми Ctrl+C для выхода.\n")
    try:
        if seed is None:
            arena.play(botA_fn, botB_fn, verbose=True)
        else:
            arena.play(botA_fn, botB_fn, seed=seed, verbose=True)
    except KeyboardInterrupt:
        print("\nОстановлено пользователем.")

# ---- CLI ----
def main():
    parser = argparse.ArgumentParser(description="Псевдо-анимация для Бот-Арены (консоль).")
    parser.add_argument("--speed", type=float, default=DEFAULT_SPEED, help="Пауза между ходами, сек (0.05..0.5)")
    parser.add_argument("--seed", type=int, default=None, help="Сид карты (число). Если не указан — из arena.SEED")
    parser.add_argument("--botA", type=str, default="my", choices=["my", "greedy", "random"], help="Какой бот будет A")
    parser.add_argument("--botB", type=str, default="greedy", choices=["my", "greedy", "random"], help="Какой бот будет B")

    args = parser.parse_args()

    # на всякий случай проверим размер терминала (совет)
    cols = shutil.get_terminal_size().columns
    min_cols = box_width() + 4  # рамка + поля
    if cols < min_cols:
        print(f"⚠️  Ширина терминала мала ({cols}). Рекомендуется ≥ {min_cols} символов, иначе может «ломать» строки.")

    run_game(speed=max(0.01, args.speed), seed=args.seed, botA=args.botA, botB=args.botB)

if __name__ == "__main__":
    main()
