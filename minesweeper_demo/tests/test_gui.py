"""Headless event-loop check; skipped when Pygame is not installed."""
import importlib.util
import os
import unittest
from unittest.mock import patch


@unittest.skipUnless(importlib.util.find_spec("pygame"), "Pygame is optional for core tests")
class GuiTests(unittest.TestCase):
    def test_step_difficulty_replay_and_new_controls(self):
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"
        os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
        import pygame
        import runner
        from minesweeper import DemoSession

        created = []

        def session_factory(*args, **kwargs):
            session = DemoSession(*args, **kwargs)
            created.append(session)
            return session

        def key(code):
            return [pygame.event.Event(pygame.KEYDOWN, key=code)]

        frames = [key(pygame.K_SPACE), key(pygame.K_2), key(pygame.K_SPACE),
                  key(pygame.K_r), key(pygame.K_n), [pygame.event.Event(pygame.QUIT)]]
        with patch("sys.argv", ["runner.py", "--seed", "11"]), \
                patch.object(runner, "DemoSession", side_effect=session_factory), \
                patch.object(pygame.event, "get", side_effect=frames), \
                patch.object(runner.random, "randrange", return_value=123):
            runner.main()
        self.assertEqual(len(created), 4)
        self.assertTrue(created[0].game.started)
        self.assertEqual(created[1].game.height, 9)
        self.assertEqual(created[1].game.mine_count, 15)
        self.assertTrue(created[1].game.started)
        self.assertEqual(created[2].game.seed, 11)
        self.assertFalse(created[2].game.started)
        self.assertEqual(created[3].game.seed, 123)


if __name__ == "__main__":
    unittest.main()
