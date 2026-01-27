import random
import sys
from typing import Tuple, List, Dict

H, W = 10, 10
TURNS = 20
WALL_DENSITY = 0.08
SEED = 40 

CellEmpty, CellWall, CellFood = ".", "#", "*"

Action = {"UP": (-1, 0), "DOWN": (1, 0), "LEFT": (0, -1), "RIGHT": (0, 1), "STAY": (0, 0)}

def in_bounds(r, c):
    return 0 <= r < H and 0 <= c < W

def render(grid, posA, posB, scoreA, scoreB, turn):
    g = [row[:] for row in grid]
    rA, cA = posA
    rB, cB = posB
    g[rA][cA] = "A"
    g[rB][cB] = "B"
    print(f"Turn {turn}  |  A:{scoreA}  B:{scoreB}")
    print("+" + "-" * (2*W-1) + "+")
    for r in range(H):
        line = []
        for c in range(W):
            line.append(g[r][c])
        print("|" + " ".join(line) + "|")
    print("+" + "-" * (2*W-1) + "+\n")

def random_map():
    grid = [[CellEmpty for _ in range(W)] for _ in range(H)]
    for r in range(H):
        for c in range(W):
            if random.random() < WALL_DENSITY:
                grid[r][c] = CellWall
    # гарантируем стартовые зоны без стен
    for rr in range(2):
        for cc in range(2):
            grid[rr][cc] = CellEmpty
            grid[H-1-rr][W-1-cc] = CellEmpty
    return grid

def place_bot(grid, occupied=None):
    if occupied is None:
        occupied = set()
    tries = 0
    while True:
        tries += 1
        r, c = random.randrange(H), random.randrange(W)
        if (r, c) in occupied: 
            continue
        if grid[r][c] == CellEmpty:
            return (r, c)
        if tries > 10_000:
            raise RuntimeError("Cannot place bot")

def neighbors4(r, c):
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        rr, cc = r+dr, c+dc
        if in_bounds(rr, cc):
            yield rr, cc

def closest_food(grid, start: Tuple[int,int]) -> Tuple[int,int] | None:
    from collections import deque
    q = deque([start])
    seen = {start}
    while q:
        r, c = q.popleft()
        if grid[r][c] == CellFood:
            return (r, c)
        for rr, cc in neighbors4(r, c):
            if (rr, cc) not in seen and grid[rr][cc] != CellWall:
                seen.add((rr, cc))
                q.append((rr, cc))
    return None

# ======= БОТЫ =======

def my_bot_decide(observation: Dict) -> str:
    """
    Пример "разумного" бота: идёт по кратчайшему пути к ближайшей еде,
    если стоит на еде — берёт, если еды нет — держится ближе к центру.
    """
    me = observation["you"]["pos"]
    grid = observation["grid"]
    r, c = me
    if grid[r][c] == CellFood:
        return "PICK"

    target = closest_food(grid, me)
    if target is None:
        # еды нет — идём к центру
        center = (H//2, W//2)
        tr, tc = center
    else:
        tr, tc = target

    best = "STAY"
    best_dist = 10**9
    for name, (dr, dc) in Action.items():
        rr, cc = r+dr, c+dc
        if not in_bounds(rr, cc): 
            continue
        if grid[rr][cc] == CellWall:
            continue
        d = abs(rr - tr) + abs(cc - tc)
        if d < best_dist:
            best_dist = d
            best = name
    return best

def random_bot_decide(observation: Dict) -> str:
    me = observation["you"]["pos"]
    grid = observation["grid"]
    r, c = me
    if grid[r][c] == CellFood and random.random() < 0.9:
        return "PICK"
    choices = []
    for name, (dr, dc) in Action.items():
        rr, cc = r+dr, c+dc
        if in_bounds(rr, cc) and grid[rr][cc] != CellWall:
            choices.append(name)
    return random.choice(choices) if choices else "STAY"

def greedy_bot_decide(observation: Dict) -> str:
    # Пример противника: всегда двигается в сторону клетки с едой, если рядом
    me = observation["you"]["pos"]
    grid = observation["grid"]
    r, c = me
    if grid[r][c] == CellFood:
        return "PICK"
    for name, (dr, dc) in Action.items():
        rr, cc = r+dr, c+dc
        if in_bounds(rr, cc) and grid[rr][cc] == CellFood:
            return name
    # иначе — как рандом
    return random_bot_decide(observation)

def smart_bot_decide(observation):
    me = observation["you"]["pos"]
    opp = observation["opponent"]["pos"]
    grid = observation["grid"]

    r, c = me
    if grid[r][c] == CellFood:
        return "PICK"

    # ищем все ресурсы
    foods = [(rr, cc) for rr in range(H) for cc in range(W) if grid[rr][cc] == CellFood]
    if foods:
        # считаем расстояния Манхэттена
        def dist(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])
        foods.sort(key=lambda f: (dist(me, f), -dist(opp, f)))  
        # берём такую еду, где мы явно выигрываем по дистанции
        for f in foods:
            if dist(me, f) < dist(opp, f):
                target = f
                break
        else:
            target = foods[0]
    else:
        target = (H//2, W//2)

    # идём к цели
    best, best_dist = "STAY", 999
    for name, (dr, dc) in Action.items():
        rr, cc = r+dr, c+dc
        if in_bounds(rr, cc) and grid[rr][cc] != CellWall:
            d = abs(rr - target[0]) + abs(cc - target[1])
            if d < best_dist:
                best_dist = d
                best = name
    return best

def tournament(botA, botB, games=50):
    winsA = winsB = draws = 0
    for seed in range(games):
        scoreA, scoreB = play(botA, botB, seed=seed, verbose=False)
        if scoreA > scoreB:
            winsA += 1
        elif scoreB > scoreA:
            winsB += 1
        else:
            draws += 1
    print(f"Results of {games} games:")
    print(f"A wins: {winsA}, B wins: {winsB}, Draws: {draws}")

# ======= ДВИЖОК =======

def step(pos, action, grid):
    r, c = pos
    if action == "PICK":
        if grid[r][c] == CellFood:
            grid[r][c] = CellEmpty
            return pos, 1
        return pos, 0
    if action not in Action:
        return pos, 0
    dr, dc = Action[action]
    rr, cc = r+dr, c+dc
    if in_bounds(rr, cc) and grid[rr][cc] != CellWall:
        return (rr, cc), 0
    return pos, 0

def spawn_food(grid, chance=0.35, max_spawn=3):
    # на каждом ходу потенциально появляется до 3 новых ресурсов
    spawns = 0
    if random.random() < chance:
        cells = [(r,c) for r in range(H) for c in range(W) if grid[r][c] == CellEmpty]
        random.shuffle(cells)
        for r, c in cells:
            grid[r][c] = CellFood
            spawns += 1
            if spawns >= max_spawn:
                break

def make_observation(grid, me, opp, my_score, opp_score, turn):
    obs_grid = [row[:] for row in grid]
    return {
        "you": {"pos": me, "score": my_score},
        "opponent": {"pos": opp, "score": opp_score},
        "grid": obs_grid,
        "turn": turn,
    }

def play(botA, botB, seed=SEED, verbose=True):
    random.seed(seed)
    grid = random_map()
    posA = place_bot(grid)
    posB = place_bot(grid, {posA})
    scoreA = scoreB = 0

    for turn in range(1, TURNS+1):
        spawn_food(grid)

        obsA = make_observation(grid, posA, posB, scoreA, scoreB, turn)
        obsB = make_observation(grid, posB, posA, scoreB, scoreA, turn)

        actA = botA(obsA)
        actB = botB(obsB)

        # сначала рассчитываем новые позиции (без подбора)
        newPosA, _ = step(posA, actA if actA != "PICK" else "STAY", grid)
        newPosB, _ = step(posB, actB if actB != "PICK" else "STAY", grid)

        # столкновение: оба остаются
        if newPosA == newPosB:
            newPosA = posA
            newPosB = posB

        posA, posB = newPosA, newPosB

        # затем обработка PICK
        _, gainA = step(posA, actA, grid)
        _, gainB = step(posB, actB, grid)
        scoreA += gainA
        scoreB += gainB

        if verbose:
            render(grid, posA, posB, scoreA, scoreB, turn)

    print(f"Итоговый счёт: A={scoreA}  B={scoreB}")
    if scoreA > scoreB:
        print("Победил бот A!")
    elif scoreB > scoreA:
        print("Победил бот B!")
    else:
        print("Ничья!")
    return scoreA, scoreB

if __name__ == "__main__":
    # СРАВНИ СВОЕГО БОТА С ЖАДНЫМ
    print("Матч: MyBot (A) vs GreedyBot (B)")
    tournament(smart_bot_decide, greedy_bot_decide, games=100)
