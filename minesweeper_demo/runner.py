"""Nhiệm vụ 4: Pygame demo with single-step AI and an inspectable knowledge base."""
import argparse
import os
from pathlib import Path
import random
import sys

from minesweeper import DemoSession

BG = (15, 22, 36)
PANEL = (24, 35, 53)
TEXT = (231, 238, 246)
MUTED = (153, 173, 195)
TEAL = (62, 218, 180)
AMBER = (255, 192, 88)
RED = (255, 105, 118)
ORIGIN = (34, 148)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=11)
    parser.add_argument("--smoke-test", action="store_true", help="Render using SDL dummy display and exit")
    parser.add_argument("--screenshot", help="Save the rendered demo to a PNG file")
    args = parser.parse_args()
    if args.smoke_test:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
    try:
        import pygame
    except ImportError:
        sys.exit("Pygame is missing. Run: python3 -m pip install -r requirements.txt")

    pygame.display.init()
    pygame.font.init()
    screen = pygame.display.set_mode((1080, 720))
    pygame.display.set_caption("Minesweeper AI | Group 11 | DRAFT")
    clock = pygame.time.Clock()
    fonts = {size: pygame.font.SysFont("Arial", size) for size in (14, 16, 18, 22, 30)}
    session = DemoSession(seed=args.seed)
    flags = set()
    auto = False
    next_tick = 0
    side = 8
    mine_count = 10

    def text(value, pos, size=18, color=TEXT):
        screen.blit(fonts[size].render(str(value), True, color), pos)

    def short(value, max_width, size=14):
        while fonts[size].size(value)[0] > max_width:
            value = value[:-4] + "..."
        return value

    def reset(seed):
        nonlocal session, auto
        session = DemoSession(side, side, mine_count, seed)
        flags.clear()
        auto = False

    def step():
        nonlocal auto
        try:
            session.step()
            # User flags are annotations, not evidence. AI may open a flagged cell.
            flags.difference_update(session.game.revealed)
        except ValueError as error:
            auto = False
            session.ai.events.append(f"ERROR: {error}")

    buttons = {
        "step": pygame.Rect(34, 624, 135, 42),
        "auto": pygame.Rect(181, 624, 135, 42),
        "reset": pygame.Rect(328, 624, 135, 42),
        "new": pygame.Rect(475, 624, 135, 42),
    }

    def draw():
        game, ai = session.game, session.ai
        tile = 52 if game.height == 8 else 46
        screen.fill(BG)
        text("MINESWEEPER / AI LAB", (34, 24), 30)
        text("GROUP 11   /   KNOWLEDGE-BASED AGENT", (35, 66), 14, MUTED)
        pygame.draw.rect(screen, PANEL, (940, 26, 106, 32), border_radius=8)
        text("DRAFT 0.1", (953, 33), 16, AMBER)
        status = "WON" if game.won else "MINE HIT" if game.exploded else "RUNNING" if game.started else "READY"
        text(f"{status}   |   {game.mine_count} mines   |   Seed {game.seed}", (34, 107), 18,
             TEAL if game.won else RED if game.exploded else TEXT)
        for r in range(game.height):
            for c in range(game.width):
                cell = (r, c)
                rect = pygame.Rect(ORIGIN[0] + c * tile, ORIGIN[1] + r * tile, tile - 5, tile - 5)
                opened = cell in game.revealed
                color = (37, 51, 70) if not opened else (21, 31, 47)
                if not opened and cell in ai.safes:
                    color = (28, 79, 76)
                if not opened and cell in ai.mines:
                    color = (90, 48, 60)
                pygame.draw.rect(screen, color, rect, border_radius=6)
                if cell == session.last_move:
                    pygame.draw.rect(screen, AMBER, rect, width=2, border_radius=6)
                if game.finished and cell in game.mines:
                    pygame.draw.circle(screen, RED, rect.center, 9)
                elif opened:
                    clue = game.revealed[cell]
                    if clue:
                        colors = {1: (116, 183, 255), 2: TEAL, 3: RED}
                        label = fonts[22].render(str(clue), True, colors.get(clue, AMBER))
                        screen.blit(label, label.get_rect(center=rect.center))
                elif cell in ai.mines or cell in flags:
                    label = fonts[22].render("F", True, RED if cell in ai.mines else AMBER)
                    screen.blit(label, label.get_rect(center=rect.center))
                elif cell in ai.safes:
                    pygame.draw.circle(screen, TEAL, rect.center, 4)

        pygame.draw.rect(screen, PANEL, (638, 100, 408, 582), border_radius=14)
        text("AGENT STATE", (658, 117), 22)
        ready = len(ai.safes - ai.moves_made)
        text(f"Proven safe: {ready}    Known mines: {len(ai.mines)}", (658, 154), 16, TEAL)
        text(f"Safe choices: {session.safe_moves}    Guesses: {session.guesses}", (658, 180), 16)
        text(f"Open: {len(game.revealed)}    Subset rules: {ai.subset_inferences}", (658, 206), 16)
        text(short(session.last_kind, 365, 16), (658, 236), 16, AMBER)
        text(f"KNOWLEDGE BASE / {len(ai.knowledge)} constraints", (658, 278), 14, MUTED)
        for i, sentence in enumerate(ai.knowledge[:5]):
            text(short(str(sentence), 365), (658, 303 + i * 22), 14)
        text("RECENT REASONING   /   coordinates: row, col", (658, 430), 14, MUTED)
        for i, event in enumerate(list(ai.events)[-8:]):
            text(short(event, 365), (658, 456 + i * 24), 14,
                 TEAL if event.startswith("SAFE") else RED if event.startswith("MINE") else TEXT)

        text("Green dot: proven safe     Red F: AI mine     Yellow F: your flag", (34, 580), 14, MUTED)
        for key, rect in buttons.items():
            pygame.draw.rect(screen, TEAL if key == "step" else PANEL, rect, border_radius=9)
            title = {"step": "Step [Space]", "auto": "Pause [A]" if auto else "Auto [A]",
                     "reset": "Replay [R]", "new": "New [N]"}[key]
            label = fonts[16].render(title, True, BG if key == "step" else TEXT)
            screen.blit(label, label.get_rect(center=rect.center))
        text("Left click: open | Right click: flag | 1: 8x8 / 10 mines | 2: 9x9 / 15 mines", (34, 687), 14, MUTED)
        pygame.display.flip()

    if args.smoke_test:
        for _ in range(5):
            step()
        draw()
        if args.screenshot:
            destination = Path(args.screenshot)
            destination.parent.mkdir(parents=True, exist_ok=True)
            pygame.image.save(screen, str(destination))
        pygame.quit()
        print("GUI smoke test passed")
        return

    running = True
    while running:
        action = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                action = {pygame.K_SPACE: "step", pygame.K_a: "auto", pygame.K_r: "reset",
                          pygame.K_n: "new", pygame.K_1: "easy", pygame.K_2: "hard"}.get(event.key)
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for key, rect in buttons.items():
                        if rect.collidepoint(event.pos):
                            action = key
                x, y = event.pos
                tile = 52 if side == 8 else 46
                c, r = (x - ORIGIN[0]) // tile, (y - ORIGIN[1]) // tile
                inside_tile = (x - ORIGIN[0]) % tile < tile - 5 and (y - ORIGIN[1]) % tile < tile - 5
                if 0 <= r < side and 0 <= c < side and inside_tile and not session.game.finished:
                    cell = (r, c)
                    auto = False
                    if event.button == 1 and cell not in flags and cell not in session.ai.mines:
                        session.open_cell(cell)
                    elif event.button == 3 and cell not in session.game.revealed and cell not in session.ai.mines:
                        flags.symmetric_difference_update({cell})
        if action == "step":
            auto = False
            step()
        elif action == "auto":
            auto = not auto
        elif action == "reset":
            reset(session.game.seed)
        elif action == "new":
            reset(random.randrange(1_000_000))
        elif action in ("easy", "hard"):
            side, mine_count = (8, 10) if action == "easy" else (9, 15)
            reset(session.game.seed)
        if auto and not session.game.finished and pygame.time.get_ticks() >= next_tick:
            step()
            next_tick = pygame.time.get_ticks() + 450
        if session.game.finished:
            auto = False
        draw()
        clock.tick(30)
    pygame.quit()


if __name__ == "__main__":
    main()
