import chess
import chess.engine
import logging
from log_colors import LogColors

log_colors = LogColors()

class PositionTest:
    def __init__(self, position:chess.Board, engine:chess.engine.SimpleEngine,player_turn:bool=True, best_move:chess.Move=None, best_evaluation:chess.engine.Score=None, next_best_evaluvation:chess.engine.Score=None,depth:int=17):
        self.position = position
        self.engine = engine
        self.best_move = None
        self.player_turn = player_turn
        self.next_position = None
        self.best_move = best_move
        self.best_evaluvation = best_evaluation
        self.next_best_evaluvation = next_best_evaluvation
        self.depth = depth
    
    def move_list(self):
        if self.next_position is None or self.next_position.ambiguous() or self.next_position.position.is_game_over():
            if self.best_move is not None:
                return [self.best_move.uci()]
            else:
                return []
        else:
            return [self.best_move.uci()] + self.next_position.move_list()
    
    def ambiguous(self):
        if(self.best_evaluvation is not None and self.next_best_evaluvation is not None):
            if self.best_evaluvation.is_mate() and self.next_best_evaluvation.is_mate():
                if(self.best_evaluvation.mate() > -1 and self.next_best_evaluvation.mate() > -1):
                    return True
            elif self.best_evaluvation.is_mate() and not(self.next_best_evaluvation.is_mate()):
                if(self.next_best_evaluvation.cp > 200):
                    return True
            
            elif not(self.best_evaluvation.is_mate()) and not(self.next_best_evaluvation.is_mate()) :
                if(self.best_evaluvation.cp < 210
                    or self.next_best_evaluvation.cp > 90):
                    return True
        return False

    def category(self):
        if self.next_position is None:
            if self.position.is_game_over():
                return 'Mate'
            else:
                return 'Material'
        else:
            return self.next_position.category()
    
    def material_difference(self):
        return sum(v * (len(self.position.pieces(pt, True)) - len(self.position.pieces(pt, False))) for v, pt in zip([0,3,3,5.5,9], chess.PIECE_TYPES))

    def material_count(self):
        return chess.popcount(self.position.occupied)

    def generate(self):
        logging.debug(self.position.unicode()+'\n')
        logging.debug(log_colors.print_blue('Material Value: ' + str(self.material_difference())))
        
        self.evaluate_position()

        if self.best_move and not self.ambiguous() and not self.game_over():
            logging.debug(log_colors.print_green("Going Deeper:"))
            logging.debug(log_colors.print_green("   Ambiguous: " + str(self.ambiguous())))
            logging.debug(log_colors.print_green("   Game Over: " + str(self.game_over())))
            logging.debug(log_colors.print_green("   Has Best Move: " + str(self.best_move!=None)))
            self.next_position.generate()
        else:
            logging.debug(log_colors.print_warning("Not Going Deeper:"))
            logging.debug(log_colors.print_warning("   Ambiguous: " + str(self.ambiguous())))
            logging.debug(log_colors.print_warning("   Game Over: " + str(self.game_over())))
            logging.debug(log_colors.print_warning("   Has Best Move: " + str(self.best_move!=None)))

    def is_complete(self, category, color, first_node, first_val):
        if self.next_position is not None:
            if ((category == 'Mate' and not self.ambiguous())
                or (category == 'Material' and self.next_position.next_position is not None)):
                return self.next_position.is_complete(category, color, False, first_val)
        
        if category == 'Material':
            if color:
                if (self.material_difference() > 0.2 
                    and abs(self.material_difference() - first_val) > 0.1 
                    and first_val < 2
                    and self.best_evaluvation.is_mate() is False
                    and self.material_count() > 6):
                    return True
                else:
                    return False
            else:
                if (self.material_difference() < -0.2 
                    and abs(self.material_difference() - first_val) > 0.1
                    and first_val > -2
                    and self.best_evaluvation.is_mate() is False
                    and self.material_count() > 6):
                    return True
                else:
                    return False
        else:
            if self.position.is_game_over() and self.material_count() > 6:
                return True
            else:
                return False

    def evaluate_position(self):
        if(self.player_turn):
            info = self.engine.analyse(self.position,chess.engine.Limit(depth=self.depth),multipv=2)
            self.best_move = info[0].pv[0]
            self.best_evaluvation = info[0].score.relative
            if(len(info)>1):
                self.next_best_evaluvation = info[1].score.relative
            else:
                self.next_best_evaluvation = None
        else:
            info = self.engine.analyse(self.position,chess.engine.Limit(depth=self.depth))
            self.best_move = info.pv[0]
            self.best_evaluvation = info.score.relative
            self.next_best_evaluvation = None
        if(self.best_move is not None):
            self.next_position = PositionTest(position=self.position.copy(),
                engine = self.engine,
                player_turn = not(self.player_turn),)
            logging.debug(log_colors.print_green("Best Move: " + self.next_position.position.san(self.best_move)))
            self.next_position.position.push(self.best_move)
            logging.debug(log_colors.print_blue("   CP: " + (str(self.best_evaluvation.cp) if not(self.best_evaluvation.is_mate()) else "None")))
            logging.debug(log_colors.print_blue("   Mate: " + str(self.best_evaluvation.is_mate())))
            if(self.next_best_evaluvation!=None):
                logging.debug(log_colors.print_green("Next Best Evaluvation: "))
                logging.debug(log_colors.print_blue("   CP: " + (str(self.next_best_evaluvation.cp) if not(self.next_best_evaluvation.is_mate()) else "None")))
                logging.debug(log_colors.print_blue("   Mate: " + str(self.next_best_evaluvation.is_mate())))
            return True
        else:
            logging.debug(log_colors.print_fail("No best move!"))
            return False

    def game_over(self):
        return self.next_position.position.is_game_over()

# g = PositionTest(position = chess.Board("r2qk2r/p2p1ppp/1pbbp3/7n/2P1P3/P1N1B3/1PQ2PPP/R3KB1R w KQkq - 4 12"),engine = chess.engine.SimpleEngine.popen_uci('./stockfish-x86_64-bmi2'))
# g.generate()
# print(g.is_complete(g.category(),g.position.turn,True,g.material_difference()) and not g.ambiguous() and len(g.move_list())>2)