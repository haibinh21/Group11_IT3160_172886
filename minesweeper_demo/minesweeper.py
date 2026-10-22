"""Draft Minesweeper: game rules and a knowledge-based agent, no GUI dependency.

Coordinates are (row, column). Sentence(cells, count) means exactly count mines.
The agent receives only revealed clues; it never receives the hidden board.
"""
from collections import deque
from dataclasses import dataclass
import random

Cell = tuple[int, int]


@dataclass
class Sentence:
    """Nhiệm vụ 1: biểu diễn và cập nhật một ràng buộc đếm mìn."""
    cells: set[Cell]
    count: int

    def __post_init__(self):
        self.cells = set(self.cells)
        self.validate()

    def validate(self):
        if not 0 <= self.count <= len(self.cells):
            raise ValueError(f"Contradictory sentence: {self}")

    def known_mines(self):
        return set(self.cells) if self.count == len(self.cells) else set()

    def known_safes(self):
        return set(self.cells) if self.count == 0 else set()

    def mark_mine(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1
            self.validate()

    def mark_safe(self, cell):
        self.cells.discard(cell)
        self.validate()

    def __str__(self):
        return f"{sorted(self.cells)} = {self.count}"


class Minesweeper:
    """Board generated on first reveal; only the first clicked cell is protected."""
    def __init__(self, height=8, width=8, mines=10, seed=11):
        if height < 1 or width < 1 or not 0 <= mines < height * width:
            raise ValueError("Need positive dimensions and 0 <= mines < cell count")
        self.height, self.width, self.mine_count = height, width, mines
        self.seed = seed
        self.mines: set[Cell] = set()
        self.revealed: dict[Cell, int] = {}
        self.exploded: Cell | None = None
        self.started = False

    def neighbors(self, cell):
        row, col = cell
        return {(r, c) for r in range(max(0, row - 1), min(self.height, row + 2))
                for c in range(max(0, col - 1), min(self.width, col + 2))
                if (r, c) != cell}

    @property
    def won(self):
        # Winning means every non-mine cell is open; flags are only annotations.
        return self.started and len(self.revealed) == self.height * self.width - self.mine_count

    @property
    def finished(self):
        return self.exploded is not None or self.won

    def reveal(self, cell):
        """Return all new visible clues, including zero-region expansion."""
        r, c = cell
        if not (0 <= r < self.height and 0 <= c < self.width):
            raise ValueError("Cell is outside the board")
        if self.finished or cell in self.revealed:
            return {}
        if not self.started:
            choices = [(r, c) for r in range(self.height) for c in range(self.width)
                       if (r, c) != cell]
            self.mines = set(random.Random(self.seed).sample(choices, self.mine_count))
            self.started = True
        if cell in self.mines:
            self.exploded = cell
            return {}
        pending = deque([cell])
        new = {}
        while pending:
            current = pending.popleft()
            if current in self.revealed:
                continue
            nearby = self.neighbors(current)
            count = len(nearby & self.mines)
            self.revealed[current] = new[current] = count
            if count == 0:
                pending.extend(sorted(nearby - self.revealed.keys()))
        return new


class MinesweeperAI:
    """Nhiệm vụ 2–3: direct rules + subset inference until a fixed point."""
    def __init__(self, height=8, width=8, seed=11):
        self.height, self.width = height, width
        self.moves_made: set[Cell] = set()
        self.safes: set[Cell] = set()
        self.mines: set[Cell] = set()
        self.knowledge: list[Sentence] = []
        self.rng = random.Random(seed)
        self.events = deque(maxlen=80)
        self.subset_inferences = 0

    def neighbors(self, cell):
        row, col = cell
        return {(r, c) for r in range(max(0, row - 1), min(self.height, row + 2))
                for c in range(max(0, col - 1), min(self.width, col + 2))
                if (r, c) != cell}

    def mark_mine(self, cell):
        if cell in self.safes:
            raise ValueError(f"Cell is both safe and mine: {cell}")
        if cell not in self.mines:
            self.mines.add(cell)
            self.events.append(f"MINE {cell}")
            for sentence in self.knowledge:
                sentence.mark_mine(cell)

    def mark_safe(self, cell):
        if cell in self.mines:
            raise ValueError(f"Cell is both safe and mine: {cell}")
        if cell not in self.safes:
            self.safes.add(cell)
            self.events.append(f"SAFE {cell}")
            for sentence in self.knowledge:
                sentence.mark_safe(cell)

    def _clean(self):
        unique = {}
        for sentence in self.knowledge:
            sentence.validate()
            if not sentence.cells:
                continue
            key = frozenset(sentence.cells)
            if key in unique and unique[key].count != sentence.count:
                raise ValueError("Different mine counts for the same set of cells")
            unique[key] = sentence
        self.knowledge = list(unique.values())

    def infer(self):
        """Repeat inference because each new fact can simplify older sentences."""
        while True:
            self._clean()
            safe, mines = set(), set()
            for sentence in self.knowledge:
                safe |= sentence.known_safes()
                mines |= sentence.known_mines()
            if safe & mines:
                raise ValueError("Knowledge base contains incompatible conclusions")
            if safe or mines:
                for cell in sorted(safe):
                    self.mark_safe(cell)
                for cell in sorted(mines):
                    self.mark_mine(cell)
                continue

            existing = {frozenset(s.cells): s.count for s in self.knowledge}
            additions = {}
            for left in self.knowledge:
                for right in self.knowledge:
                    if left.cells < right.cells:
                        cells = frozenset(right.cells - left.cells)
                        count = right.count - left.count
                        Sentence(set(cells), count).validate()
                        previous = existing.get(cells, additions.get(cells))
                        if previous is not None and previous != count:
                            raise ValueError("Subset inference produced a contradiction")
                        if previous is None:
                            additions[cells] = count
            if not additions:
                return
            for cells, count in additions.items():
                sentence = Sentence(set(cells), count)
                self.knowledge.append(sentence)
                self.subset_inferences += 1
                self.events.append(f"SUBSET {sentence}")

    def add_knowledge(self, cell, count):
        """Receive a safe revealed cell and its adjacent-mine count."""
        if cell in self.moves_made:
            return
        if not (0 <= cell[0] < self.height and 0 <= cell[1] < self.width):
            raise ValueError("Cell is outside the board")
        nearby = self.neighbors(cell)
        if not 0 <= count <= len(nearby):
            raise ValueError("Invalid clue")
        self.moves_made.add(cell)
        self.mark_safe(cell)
        self.events.append(f"CLUE {cell}: {count}")
        unknown = nearby - self.safes - self.mines
        remaining = count - len(nearby & self.mines)
        self.knowledge.append(Sentence(unknown, remaining))
        self.infer()

    def make_safe_move(self):
        candidates = self.safes - self.moves_made
        return min(candidates) if candidates else None

    def make_random_move(self):
        # Uniform among legal unknown cells; this is not a minimum-risk solver.
        candidates = sorted({(r, c) for r in range(self.height) for c in range(self.width)}
                            - self.moves_made - self.mines)
        return self.rng.choice(candidates) if candidates else None


class DemoSession:
    """Shared controller for GUI and experiments; hidden board stays in the game."""
    def __init__(self, height=8, width=8, mines=10, seed=11):
        self.game = Minesweeper(height, width, mines, seed)
        self.ai = MinesweeperAI(height, width, seed + 100_000)
        self.safe_moves = self.guesses = 0
        self.last_move = None
        self.last_kind = "Ready"

    def open_cell(self, cell, kind="Manual"):
        if self.game.finished or cell in self.game.revealed:
            return
        self.last_move, self.last_kind = cell, kind
        new = self.game.reveal(cell)
        for opened, clue in new.items():
            self.ai.add_knowledge(opened, clue)
        if self.game.exploded is not None:
            self.ai.events.append(f"HIT MINE {cell}")

    def step(self, strategy="logic"):
        if self.game.finished:
            return
        if not self.game.started:
            cell = (self.game.height // 2, self.game.width // 2)
            kind = "First move (protected)"
        else:
            cell = self.ai.make_safe_move() if strategy == "logic" else None
            if cell is not None:
                kind = "Logic: proven safe"
                self.safe_moves += 1
            else:
                if strategy == "random":
                    # Baseline ignores inferred mines too, using only visible cells.
                    choices = sorted({(r, c) for r in range(self.game.height)
                                      for c in range(self.game.width)} - self.game.revealed.keys())
                    cell = self.ai.rng.choice(choices) if choices else None
                else:
                    cell = self.ai.make_random_move()
                kind = "Guess: uniform random"
                self.guesses += 1
        if cell is not None:
            self.open_cell(cell, kind)
