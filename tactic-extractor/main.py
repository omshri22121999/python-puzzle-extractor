import chess
import chess.pgn
import chess.engine
import logging
import sys
import argparse
from log_colors import LogColors
from investigate import Investigate
from puzzle_extract import PuzzleExtract
import platform

log_colors = LogColors()
investigate = Investigate()
format = "%(message)s"

logging.basicConfig(level=logging.DEBUG, format=format)

logging.getLogger("chess.engine").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)

parser = argparse.ArgumentParser(description="Extract tactics from chess games")

parser.add_argument(
    "-p", "--pgn", help="Location of PGN file to read.", default="./games.pgn"
)
parser.add_argument(
    "-s",
    "--stockfish",
    help="Location of StockFish engine.",
    default="./stockfish/sf_" + platform.system(),
)
parser.add_argument("-q", "--quiet", help="Whether to print logs.", action="store_true")


args = parser.parse_args()
pgn_file = args.pgn

if args.quiet:
    logger = logging.getLogger()
    logger.disabled = True

try:
    chess_engine = chess.engine.SimpleEngine.popen_uci(args.stockfish)
except Exception as e:
    logging.exception(log_colors.print_fail("ERROR : " + e.args[1]), exc_info=False)
    sys.exit()
    exit()

try:
    all_games = open(pgn_file, "r")
except Exception as e:
    logging.exception(
        log_colors.print_fail("ERROR : " + str(e.args[1])), exc_info=False
    )
    chess_engine.quit()
    sys.exit()

tactics_file = open("tactics.pgn", "w")
game_id = 0
depth_var = 17

while True:
    game = chess.pgn.read_game(all_games)
    if game == None:
        break
    game_id += 1
    game_board = game.board()
    logging.debug(log_colors.print_blue("Game ID: " + str(game_id)))
    logging.debug(log_colors.print_header(str(game)))
    logging.debug(log_colors.print_underline("Starting Position:\n"))
    logging.debug(game_board.unicode(invert_color=True) + "\n")
    prev_score = chess.engine.Cp(0)
    puzzles = []
    for move in game.mainline_moves():
        move_num_str = str(game_board.fullmove_number) + "."
        dummy_board = game_board.copy()
        if not (game_board.turn):
            move_num_str += " ... "
        logging.debug(log_colors.print_blue(move_num_str + game_board.san(move)))
        dummy_board.push(move)
        logging.debug(dummy_board.unicode(invert_color=True) + "\n")
        info = chess_engine.analyse(dummy_board, chess.engine.Limit(depth=depth_var))
        logging.debug(log_colors.print_green("   CP : " + str(info.score.relative)))
        logging.debug(
            log_colors.print_green("   Mate : " + str(info.score.relative.mate()))
        )
        cur_score = info.score.relative
        if investigate.investigate(prev_score, cur_score, game_board):
            print(log_colors.print_warning("Interesting Position!"))
            puzzles.append(
                PuzzleExtract(
                    last_pos=game_board.copy(),
                    last_move=move,
                    game_id=game_id,
                    engine=chess_engine,
                    game=game,
                    depth=depth_var,
                )
            )
        prev_score = cur_score
        game_board.push(move)

    logging.debug("\n\n")
    for puzzle in puzzles:
        logging.debug(log_colors.print_warning("Generating New Puzzle ...."))
        puzzle.generate()
        if puzzle.is_complete():
            logging.debug(log_colors.print_bold("Puzzle Generated!"))

            puzzle_pgn = puzzle.to_pgn()
            logging.debug(log_colors.print_header(str(puzzle_pgn)))
            logging.debug(
                log_colors.print_bold("Adding Puzzle to tactics.pgn ..... \n")
            )
            try:
                if puzzle.positions.category() == "Material":
                    moves = list(puzzle_pgn.mainline_moves())[0:-1]
                    puzzle_pgn.remove_variation(0)
                    puzzle_pgn.add_line(moves)
                tactics_file.write(str(puzzle_pgn))
                tactics_file.write("\n\n")
                logging.debug(log_colors.print_bold("Puzzle Added! \n"))

            except Exception as e:
                logging.error(log_colors.print_fail("ERROR:" + str(e)))

tactics_file.close()
all_games.close()
chess_engine.quit()
