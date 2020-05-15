from tactics_checker import Tactic
import chess


class TacticClassifier:
    def __init__(self):
        self.value = {1: 1, 2: 3, 3: 3, 4: 5, 5: 9, 6: 100}

    def set_pgn(self, game_set):
        self.game = game_set

