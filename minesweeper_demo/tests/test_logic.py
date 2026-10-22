import unittest
from minesweeper import DemoSession, Minesweeper, MinesweeperAI, Sentence


class LogicTests(unittest.TestCase):
    def test_sentence_updates(self):
        a, b = (0, 0), (0, 1)
        sentence = Sentence({a, b}, 1)
        self.assertEqual(sentence.known_safes(), set())
        sentence.mark_mine(a)
        self.assertEqual(sentence.known_safes(), {b})
        sentence.mark_safe(b)
        self.assertEqual(sentence.cells, set())
        self.assertEqual(Sentence({a}, 1).known_mines(), {a})

    def test_subset_reaches_fixed_point(self):
        a, b, c, d = [(0, i) for i in range(4)]
        ai = MinesweeperAI(2, 4)
        ai.knowledge = [Sentence({a, b}, 1), Sentence({a, b, c}, 1), Sentence({c, d}, 1)]
        ai.infer()
        self.assertIn(c, ai.safes)
        self.assertIn(d, ai.mines)
        self.assertEqual(ai.subset_inferences, 1)
        before = (set(ai.safes), set(ai.mines), len(ai.knowledge))
        ai.infer()
        self.assertEqual(before, (ai.safes, ai.mines, len(ai.knowledge)))

    def test_clue_subtracts_known_mines(self):
        ai = MinesweeperAI(2, 2)
        ai.mark_mine((0, 0))
        ai.add_knowledge((1, 1), 1)
        self.assertTrue({(0, 1), (1, 0)} <= ai.safes)
        self.assertIn(ai.make_safe_move(), {(0, 1), (1, 0)})

    def test_contradictions(self):
        with self.assertRaises(ValueError):
            Sentence({(0, 0)}, 2)
        ai = MinesweeperAI()
        ai.knowledge = [Sentence({(0, 0)}, 0), Sentence({(0, 0)}, 1)]
        with self.assertRaises(ValueError):
            ai.infer()

    def test_zero_board_and_first_click(self):
        game = Minesweeper(3, 3, 0)
        self.assertEqual(len(game.reveal((0, 0))), 9)
        self.assertTrue(game.won)
        dense = Minesweeper(2, 2, 3)
        dense.reveal((1, 1))
        self.assertNotIn((1, 1), dense.mines)
        self.assertTrue(dense.won)

    def test_random_move_excludes_mines_and_opened(self):
        ai = MinesweeperAI(1, 3)
        ai.mark_mine((0, 0))
        ai.moves_made.add((0, 1))
        self.assertEqual(ai.make_random_move(), (0, 2))
        ai.moves_made.add((0, 2))
        self.assertIsNone(ai.make_random_move())

    def test_agent_facts_match_hidden_truth_across_games(self):
        # Oracle belongs only to the test, never to the agent.
        for seed in range(100):
            session = DemoSession(6, 6, 6, seed)
            for _ in range(37):
                if session.game.finished:
                    break
                session.step()
                self.assertFalse(session.ai.safes & session.game.mines, f"seed={seed}")
                self.assertTrue(session.ai.mines <= session.game.mines, f"seed={seed}")
            self.assertTrue(session.game.finished, f"Agent stalled: {seed}")

    def test_reproducible_board(self):
        first, second = DemoSession(seed=42), DemoSession(seed=42)
        first.step()
        second.step()
        self.assertEqual(first.game.mines, second.game.mines)
        self.assertEqual(first.game.revealed, second.game.revealed)


if __name__ == "__main__":
    unittest.main()
