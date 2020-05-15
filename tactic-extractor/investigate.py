import chess


class Investigate:
    def __init__(self):
        pass

    def mate_sign(self, mate):
        if mate.is_mate():
            if mate.mate() > 0:
                return 1
            elif mate.mate() < 0:
                return -1
            else:
                return 0

    def material_value(self, board):
        return sum(
            v * (len(board.pieces(pt, True)) + len(board.pieces(pt, False)))
            for v, pt in zip([0, 3, 3, 5.5, 9], chess.PIECE_TYPES)
        )

    def piece_count(self, board):
        return chess.popcount(board.occupied)

    def investigate(self, prev_score, curr_score, board):
        if prev_score.is_mate() and curr_score.is_mate():
            if self.mate_sign(prev_score) == self.mate_sign(curr_score):
                return True
        elif (
            not (prev_score.is_mate())
            and (curr_score.is_mate())
            and (self.material_value(board) > 3)
        ):
            if (
                (prev_score.cp < 110)
                and (self.mate_sign(curr_score) == -1)
                or (prev_score.cp > -110)
                and (self.mate_sign(curr_score) == 1)
            ):
                return True
        elif (
            not (prev_score.is_mate())
            and not (curr_score.is_mate())
            and (self.material_value(board) > 3)
            and self.piece_count(board) > 6
        ):
            if (
                prev_score.cp > -110
                and prev_score.cp < 850
                and curr_score.cp > 200
                and curr_score.cp < 800
            ) or (
                prev_score.cp > -850
                and prev_score.cp < 110
                and curr_score.cp < -200
                and curr_score.cp > -850
            ):
                return True
        return False
