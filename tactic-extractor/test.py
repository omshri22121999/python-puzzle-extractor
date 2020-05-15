import chess
import chess.pgn
import chess.engine
from tactic_classifier import TacticClassifier

eng = chess.engine.SimpleEngine.popen_uci("./stockfish-x86_64-bmi2")
list = [
    "r2q1k1r/ppp1n1Np/1bnpB2B/8/1P1pb1P1/2P4P/P4P2/R2Q1RK1 w - - 0 1",
]
for i in list:
    board = chess.Board(i)
    for depth in range(1, 22):
        info = eng.analyse(board, limit=chess.engine.Limit(depth=depth))
        print("Depth : " + str(depth) + " | Move : " + str(board.san(info.pv[0])))
        if info.score.is_mate():
            print("Found As Mate!")
eng.quit()
