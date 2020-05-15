from position_test import PositionTest
from log_colors import LogColors
import chess
import chess.pgn
import logging

log_colors = LogColors()


class PuzzleExtract:
    def __init__(self, last_pos, last_move, game_id, engine, game, depth):
        self.last_pos = last_pos.copy()
        self.last_move = last_move
        self.game_id = game_id
        last_pos.push(last_move)
        self.positions = PositionTest(last_pos, engine, depth=depth)
        self.game = game

    def to_dict(self):
        return {
            "game_id": self.game_id,
            "category": self.positions.category(),
            "last_pos": self.last_pos.fen(),
            "last_move": self.last_move.uci(),
            "move_list": self.positions.move_list(),
        }

    def to_pgn(self):
        fen = self.last_pos.fen()
        board = chess.Board(fen)
        game = chess.pgn.Game().from_board(board)

        result = "1-0"
        if board.turn:
            result = "0-1"

        node = game.add_variation(self.last_move)
        for m in self.positions.move_list():
            node = node.add_variation(chess.Move.from_uci(m))

        for h in self.game.headers:
            game.headers[h] = self.game.headers[h]
        game.headers["Result"] = result
        return game

    def color(self):
        return self.positions.position.turn

    def is_complete(self):
        return (
            self.positions.is_complete(
                self.positions.category(),
                self.color(),
                True,
                self.positions.material_difference(),
            )
            and not self.positions.ambiguous()
            and len(self.positions.move_list()) > 2
        )

    def generate(self):
        self.positions.generate()
        if self.is_complete():
            logging.debug(log_colors.print_green("Puzzle is complete"))
        else:
            logging.debug(log_colors.print_fail("Puzzle incomplete"))

    def category(self):
        return self.positions.category()
