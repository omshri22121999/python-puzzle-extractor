# %%
import chess
import json

class Tactic:
    def __init__(self):
        self.value = {1: 1, 2: 3, 3: 3, 4: 5, 5: 9, 6: 100}

    def set_params(self, fen, move, checkmate_move):
        self.board = chess.Board(fen)
        self.old_board = chess.Board(fen)
        self.board.push(move)
        self.move = move
        self.capture_check = self.old_board.is_capture(move)
        if((str.isnumeric(move.uci()[-1]))):
            self.new_square_moved_piece = chess.SQUARES[chess.SQUARE_NAMES.index(
                move.uci()[-2:])]
        else:
            self.new_square_moved_piece = chess.SQUARES[chess.SQUARE_NAMES.index(
                move.uci()[-3:-1])]
        self.old_square_moved_piece = chess.SQUARES[chess.SQUARE_NAMES.index(
            move.uci()[0:2])]
        self.squares_moved_piece_attacks = list(
            self.board.attacks(self.new_square_moved_piece))
        self.moved_piece = self.board.piece_at(self.new_square_moved_piece)
        self.pieces_discovery = list(self.board.attackers(
            color=self.moved_piece.color, square=self.old_square_moved_piece))
        self.opp_color_attackers = list(self.board.attackers(
            square=self.new_square_moved_piece, color=not(self.moved_piece.color)))
        if(self.new_square_moved_piece in self.pieces_discovery):
            self.pieces_discovery.remove(self.new_square_moved_piece)
        if(checkmate_move != None):
            self.checkmate = True
            self.checkmate_piece_square = chess.SQUARES[chess.SQUARE_NAMES.index(
                checkmate_move.uci()[0:2])]
            self.checkmate_fin_square = chess.SQUARES[chess.SQUARE_NAMES.index(
                checkmate_move.uci()[-2:])]
        else:
            self.checkmate = False
            self.checkmate_piece_square = None
            self.checkmate_fin_square = None

    def print_board(self, tac="Tactic"):
        print('\n')
        print(tac+"\n\n")
        print(self.board)

    def cp_diff_percent(self, cp1, cp2):
        if(cp1 != 0):
            return abs(float((cp1-cp2)*100.0/cp1))
        elif(cp2 != 0):
            return abs(float((cp1-cp2)*100.0/cp2))
        else:
            return 0

    def useful_attacks(self, sq, piece, board):
        piece_check = board.piece_at(sq)
        if(piece_check != None):
            if(piece_check.color != piece.color):
                if(self.piece_value_check(piece_check, piece) > 0):
                    return 1
                elif(self.attack_strength(sq, piece.color, board) > 0):
                    return 1
        return 0

    def attack_strength(self, sq, color, board): 
        dummy_board = board.copy()
        attackers_final_list = []
        defenders_final_list = []
        type='real'
        attackers = list(dummy_board.attackers(square=sq, color=color))
        defenders = list(dummy_board.attackers(square=sq, color=not(color)))
        while(len(attackers)!=0):
            attackers_ch = [{'type':type,'square':i} for i in attackers]
            type = 'auxillary' 
            attackers_final_list.extend(attackers_ch)
            for square in attackers:
                dummy_board.remove_piece_at(square)
            attackers = list(dummy_board.attackers(square=sq, color=color))
        dummy_board = board.copy()
        type='real'
        while(len(defenders)!=0):
            defenders_ch = [{'type':type,'square':i} for i in defenders]
            type = 'auxillary' 
            defenders_final_list.extend(defenders_ch)
            for square in defenders:
                dummy_board.remove_piece_at(square)
            defenders = list(dummy_board.attackers(square=sq, color=not(color)))
        # print("Sq:"+chess.SQUARE_NAMES[sq])
        # print("Attackers"+json.dumps([chess.SQUARE_NAMES[sq['square']] for sq in attackers_final_list]))
        # print("Defenders"+json.dumps([chess.SQUARE_NAMES[sq['square']] for sq in defenders_final_list]))
        return(len(attackers_final_list)-len(defenders_final_list))
    def piece_value_check(self, piece_1, piece_2):
        return self.value[(piece_1.piece_type)] - self.value[(piece_2.piece_type)]

    def sum_piece_value(self, board, color):
        sum = 0
        for i in range(1, 7):
            sum += (len(list(board.pieces(piece_type=i, color=color)))
                    * self.value[i])
        return(sum)
    
    def check_double_attack_fork(self):
        attacks_flag = 0
        if(self.checkmate):
            if(self.checkmate_piece_square == self.new_square_moved_piece):
                attacks_flag += 1
        for sq in self.squares_moved_piece_attacks:
            if(attacks_flag > 1):
                break
            attacks_flag += self.useful_attacks(
                sq, self.moved_piece, self.board)
        if(attacks_flag > 1):
            return True
        else:
            return False

    def check_discovered_attack(self):
        attacks_flag = 0
        discovered_attacks_flag = 0
        neutral_flag = 0
        if(self.checkmate):
            if(self.checkmate_piece_square == self.new_square_moved_piece):
                attacks_flag += 1
            elif(self.checkmate_piece_square in self.pieces_discovery):
                discovered_attacks_flag += 1
            else:
                neutral_flag += 1
        for sq in self.squares_moved_piece_attacks:
            if(attacks_flag > 0):
                break
            attacks_flag += self.useful_attacks(
                sq, self.moved_piece, self.board)
        for sq_dis_piece in self.pieces_discovery:
            same_attack_sq = list(self.board.attacks(sq_dis_piece))
            discovery_piece = self.board.piece_at(sq_dis_piece)
            for sq in same_attack_sq:
                if(discovered_attacks_flag > 0):
                    break
                discovered_attacks_flag += self.useful_attacks(
                    sq, discovery_piece, self.board)
        if(attacks_flag > 0 and discovered_attacks_flag > 0):
            return True
        elif(neutral_flag > 0 and (attacks_flag > 0 or discovered_attacks_flag > 0)):
            return True
        else:
            return False

    def check_absolute_pin(self):
        pins = False
        for sq in self.squares_moved_piece_attacks:
            if(len(list(self.board.pin(color=not(self.moved_piece.color), square=sq))) < 20):
                pins = True
                return pins
        for sq_piece in self.opp_color_attackers:
            if(self.board.is_pinned(color=not(self.moved_piece.color), square=sq_piece)):
                pins = True
                return pins

    def check_discovered_check(self):
        opp_king_attack_list = list(self.board.attackers(square=list(self.board.pieces(
            chess.KING, not(self.moved_piece.color)))[0], color=self.moved_piece.color))
        if(len(opp_king_attack_list) == 0):
            return False
        elif(len(opp_king_attack_list) > 1):
            return True
        elif(self.new_square_moved_piece not in opp_king_attack_list):
            return True
        else:
            return False

    def check_sacrifice_capture(self):
        if(self.capture_check):
            if(self.piece_value_check(self.old_board.piece_at(self.old_square_moved_piece),self.old_board.piece_at(self.new_square_moved_piece))<=0):
                return True
            # elif()

    def check_skewer(self):
        for sq in self.squares_moved_piece_attacks:
            if(self.useful_attacks(sq, self.moved_piece, self.board) == 1):
                new_board = self.board.copy()
                new_board.remove_piece_at(sq)
                new_attacks = list(
                    new_board.attacks(self.new_square_moved_piece))
                for new_sq in new_attacks:
                    if(new_sq not in self.squares_moved_piece_attacks):
                        if(self.useful_attacks(new_sq, self.moved_piece, new_board) == 1):
                            sq_str = chess.SQUARE_NAMES[sq]
                            new_sq_str = chess.SQUARE_NAMES[new_sq]
                            sq_mv_str = chess.SQUARE_NAMES[self.new_square_moved_piece]
                            if(sq_str[0:1] == new_sq_str[0:1] == sq_mv_str[0:1] or sq_str[-1:] == new_sq_str[-1:] == sq_mv_str[-1:]):
                                if(self.piece_value_check(self.board.piece_at(sq), self.board.piece_at(new_sq)) >= 0):
                                    return True
                            elif(abs(chess.FILE_NAMES.index(sq_str[0: 1])-chess.FILE_NAMES.index(new_sq_str[0: 1])) == abs(chess.RANK_NAMES.index(sq_str[-1:])-chess.RANK_NAMES.index(new_sq_str[-1:])) and abs(chess.FILE_NAMES.index(sq_mv_str[0: 1])-chess.FILE_NAMES.index(new_sq_str[0: 1])) == abs(chess.RANK_NAMES.index(sq_mv_str[-1:])-chess.RANK_NAMES.index(new_sq_str[-1:]))):
                                if(self.piece_value_check(self.board.piece_at(sq), self.board.piece_at(new_sq)) >= 0):
                                    return True
        return False

    def check_annihilation_of_defense(self):
        if(self.capture_check):
            defender_attack_sq = list(self.old_board.attacks(self.new_square_moved_piece))
            dummy_board = self.board.copy()
            defenders_attack_list = list(dummy_board.attackers(color=not(self.moved_piece.color),square=self.new_square_moved_piece))
            king = 'k' if self.moved_piece.color else 'K'
            piece_to_take = chess.SQUARE_NAMES[defenders_attack_list[0]] if dummy_board.piece_at(defenders_attack_list[0]).unicode_symbol!=king else chess.SQUARE_NAMES[defenders_attack_list[1]]
            dummy_board.push(chess.Move.from_uci(piece_to_take+chess.SQUARE_NAMES[self.new_square_moved_piece]))
            legal_move_list = list(dummy_board.legal_moves)
            legal_move_list_sq = [move.uci()[-2:] for move in legal_move_list]
            for sq in defender_attack_sq:
                move_list = [legal_move_list[i] for i,x in enumerate(legal_move_list_sq) if x==chess.SQUARE_NAMES[sq]]
                for move in move_list:
                    dummy_board.push(move)
                    if(dummy_board.is_checkmate()):
                        return True
                    dummy_board.pop()
        return False

    def check_blockade(self):
        if(self.board.is_checkmate()):
            king_col = False
            if(self.board.turn):
                king_col = True
            attacks_by_king = list(self.board.attacks(self.board.king(color=king_col)))
            block_pieces=0
            for sq in attacks_by_king:
                piece = self.board.piece_at(sq)
                if(piece!=None):
                    if(self.board.piece_at(sq).color==king_col):
                        block_pieces+=1
            if(block_pieces>0):
                return True
            else:
                return False
    def check_tactic(self):
        res = {"status": False, "name": []}
        if(self.check_double_attack_fork()):
            res['status'] = True
            res["name"].append("Double Attack/Fork")
        elif(self.check_discovered_check()):
            res['status'] = True
            res["name"].append("Discovered Check")
        elif(self.check_discovered_attack()):
            res['status'] = True
            res["name"].append("Discovered Attack")
        elif(self.check_skewer()):
            res['status'] = True
            res["name"].append("Skewer")
        elif(self.check_absolute_pin()):
            res['status'] = True
            res["name"].append("Absolute Pin")
        return(res)


#%%
