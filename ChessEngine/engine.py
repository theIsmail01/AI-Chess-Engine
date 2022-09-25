class GameState():
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["__", "__", "__", "__", "__", "__", "__", "__"],
            ["__", "__", "__", "__", "__", "__", "__", "__"],
            ["__", "__", "__", "__", "__", "__", "__", "__"],
            ["__", "__", "__", "__", "__", "__", "__", "__"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.is_white_move = True
        self.move_log = []
        self.piece_functions = {"P": self.get_pawn_moves,
                                "B": self.get_bishop_moves,
                                "R": self.get_rook_moves,
                                "Q": self.get_queen_moves,
                                "N": self.get_knight_moves,
                                "K": self.get_king_moves}

        self.check_mate = False
        self.stale_mate = False

        self.enpassant_possible = ()

        self.castling_rights = True

        # Castling Rights
        self.white_queen_side_castling = True
        self.white_king_side_castling = True
        self.black_queen_side_castling = True
        self.black_king_side_castling = True

        self.previous_valid_moves = []

        # [White Queen side, White King side, Black Queen side, Black King side]
        self.castle_rights_log = [[True, True, True, True]]

        self.enpassant_log = [()]

    def make_move(self, move):
        self.board[move.start_row][move.start_column] = "__"
        # Taking care of special moves specific cases
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_column] = move.piece_moved[0] + "Q"
        elif move.is_enpassant_move:
            self.board[move.end_row][move.end_column] = move.piece_moved
            self.board[move.start_row][move.end_column] = "__"
        elif move.is_castling_move:
            self.board[move.end_row][move.end_column] = move.piece_moved
            if move.end_column == 2:
                self.board[move.end_row][3] = move.piece_moved[0] + "R"
                self.board[move.end_row][0] = "__"
            else:
                self.board[move.end_row][5] = move.piece_moved[0] + "R"
                self.board[move.end_row][7] = "__"
        else:
            self.board[move.end_row][move.end_column] = move.piece_moved

        # Updating the enpassant_possible variable
        if move.piece_moved[1] == "P" and abs(move.start_row - move.end_row) == 2:
            self.enpassant_possible = (
                (move.start_row + move.end_row) // 2, move.start_column)
        else:
            self.enpassant_possible = ()

        # Keeping a log of all moves being made
        self.move_log.append(move)

        # Updating castling rights
        self.update_castling_rights(move)

        # Switching move turns
        self.is_white_move = not self.is_white_move
        self.enpassant_log.append(self.enpassant_possible)

    def update_castling_rights(self, move):
        if self.white_queen_side_castling or self.white_king_side_castling or \
           self.black_queen_side_castling or self.black_king_side_castling:
            if move.piece_moved[0] == "w":
                if move.piece_moved[1] == "K":
                    self.white_queen_side_castling = False
                    self.white_king_side_castling = False
                elif move.piece_moved[1] == "R" and move.start_row == 7 and move.start_column == 0:
                    self.white_queen_side_castling = False
                elif move.piece_moved[1] == "R" and move.start_row == 7 and move.start_column == 7:
                    self.white_king_side_castling = False
                if move.piece_captured[1] == "R" and move.end_row == 0 and move.end_column == 0:
                    self.black_queen_side_castling = False
                elif move.piece_captured[1] == "R" and move.end_row == 0 and move.end_column == 7:
                    self.black_king_side_castling = False
            elif move.piece_moved[0] == "b":
                if move.piece_moved[1] == "K":
                    self.black_queen_side_castling = False
                    self.black_king_side_castling = False
                elif move.piece_moved[1] == "R" and move.start_row == 0 and move.start_column == 0:
                    self.black_queen_side_castling = False
                elif move.piece_moved[1] == "R" and move.start_row == 0 and move.start_column == 7:
                    self.black_king_side_castling = False
                if move.piece_captured[1] == "R" and move.end_row == 7 and move.end_column == 0:
                    self.white_queen_side_castling = False
                elif move.piece_captured[1] == "R" and move.end_row == 7 and move.end_column == 7:
                    self.white_king_side_castling = False

        temp = [self.white_queen_side_castling,
                self.white_king_side_castling,
                self.black_queen_side_castling,
                self.black_king_side_castling]

        self.castle_rights_log.append(temp)

    def undo_move(self):
        last_move = self.move_log.pop()
        self.board[last_move.start_row][last_move.start_column] = last_move.piece_moved
        # Undoing an enpassant move
        if last_move.is_enpassant_move:
            self.board[last_move.end_row][last_move.end_column] = "__"
            self.board[last_move.start_row][last_move.end_column] = last_move.piece_captured
        # Undoing castling move
        elif last_move.is_castling_move:
            self.board[last_move.end_row][last_move.end_column] = "__"
            if last_move.end_column == 2:
                self.board[last_move.end_row][2] = "__"
                self.board[last_move.end_row][3] = "__"
                self.board[last_move.end_row][0] = last_move.piece_moved[0] + "R"
            else:
                self.board[last_move.end_row][6] = "__"
                self.board[last_move.end_row][5] = "__"
                self.board[last_move.end_row][7] = last_move.piece_moved[0] + "R"
        # Undoing a normal move
        else:
            self.board[last_move.end_row][last_move.end_column] = last_move.piece_captured
        self.is_white_move = not self.is_white_move

        # Updating castling rights after every undone move
        self.castle_rights_log.pop()
        self.white_queen_side_castling = self.castle_rights_log[-1][0]
        self.white_king_side_castling = self.castle_rights_log[-1][1]
        self.black_queen_side_castling = self.castle_rights_log[-1][2]
        self.black_king_side_castling = self.castle_rights_log[-1][3]

        self.check_mate = False
        self.stale_mate = False

        self.enpassant_log.pop()
        self.enpassant_possible = self.enpassant_log[-1]

    def get_valid_moves(self):
        temp_enpassant_possible = self.enpassant_possible

        temp_white_queen_castling = self.white_queen_side_castling
        temp_white_king_castling = self.white_king_side_castling
        temp_black_queen_side_castling = self.black_queen_side_castling
        temp_black_king_side_castling = self.black_king_side_castling

        all_possible_moves = self.get_all_possible_moves()
        all_valid_moves = []

        for move in all_possible_moves:
            self.make_move(move)
            opponent_moves = self.get_all_possible_moves()
            if not self.is_check(opponent_moves):
                all_valid_moves.append(move)
            self.undo_move()

        if all_valid_moves:
            self.stale_mate = False
            self.check_mate = False
        else:
            self.is_white_move = not self.is_white_move
            opponent_moves = self.get_all_possible_moves()
            if self.is_check(opponent_moves):
                self.is_white_move = not self.is_white_move
                self.check_mate = True
            else:
                self.is_white_move = not self.is_white_move
                self.stale_mate = True

        self.white_queen_side_castling = temp_white_queen_castling
        self.white_king_side_castling = temp_white_king_castling
        self.black_king_side_castling = temp_black_king_side_castling
        self.black_queen_side_castling = temp_black_queen_side_castling

        self.enpassant_possible = temp_enpassant_possible
        return all_valid_moves

    def is_check(self, moves):
        for move in moves:
            if move.piece_captured[1] == "K":
                return True
        return False

    def get_all_possible_moves(self):
        moves = []
        for row in range(len(self.board)):
            for column in range(len(self.board[row])):
                if self.board[row][column] != "__":
                    color = self.board[row][column][0]
                    if (color == "w" and self.is_white_move) or \
                            (color == "b" and not self.is_white_move):
                        piece = self.board[row][column][1]
                        self.piece_functions[piece](row, column, moves)
        castling_moves = self.get_castling_moves()
        for move in castling_moves:
            moves.append(move)
        return moves

    def get_pawn_moves(self, row, column, moves):
        piece_color = self.board[row][column][0]

        if piece_color == "w":
            # Captures to the left
            if row > 0 and column - 1 >= 0 and \
                    self.board[row - 1][column - 1][0] == "b":
                move = Move((row, column),
                            (row - 1, column - 1), self.board)
                moves.append(move)
            # Enpassant left capture
            elif (row - 1, column - 1) == self.enpassant_possible:
                move = Move((row, column), (row - 1, column - 1),
                            self.board, is_enpassant_move=True)
                moves.append(move)
            # Captures to the right
            if row > 0 and column + 1 <= 7 and \
                    self.board[row - 1][column + 1][0] == "b":
                move = Move((row, column),
                            (row - 1, column + 1), self.board)
                moves.append(move)
            # Enpassant right capture
            elif (row - 1, column + 1) == self.enpassant_possible:
                move = Move((row, column), (row - 1, column + 1),
                            self.board, is_enpassant_move=True)
                moves.append(move)
            # 1 space moving forward
            if row > 0 and self.board[row - 1][column] == "__":
                move = Move((row, column),
                            (row - 1, column), self.board)
                moves.append(move)
                # 2 space moving forward
                if row == 6 and self.board[row - 2][column] == "__":
                    move = Move((row, column),
                                (row - 2, column), self.board)
                    moves.append(move)

        elif piece_color == "b":
            # Captures to the left
            if row < 7 and column - 1 >= 0 and \
                    self.board[row + 1][column - 1][0] == "w":
                move = Move((row, column),
                            (row + 1, column - 1), self.board)
                moves.append(move)
            # Enpassant left capture
            elif (row + 1, column - 1) == self.enpassant_possible:
                move = Move((row, column), (row + 1, column - 1),
                            self.board, is_enpassant_move=True)
                moves.append(move)
            # Captures to the right
            if row < 7 and column + 1 <= 7 and \
                    self.board[row + 1][column + 1][0] == "w":
                move = Move((row, column),
                            (row + 1, column + 1), self.board)
                moves.append(move)
            # Enpassant right capture
            elif (row + 1, column + 1) == self.enpassant_possible:
                move = Move((row, column), (row + 1, column + 1),
                            self.board, is_enpassant_move=True)
                moves.append(move)
            # 1 space moving forward
            if row < 6 and self.board[row + 1][column] == "__":
                move = Move((row, column),
                            (row + 1, column), self.board)
                moves.append(move)
                # 2 space moving forward
                if row == 1 and self.board[row + 2][column] == "__":
                    move = Move((row, column),
                                (row + 2, column), self.board)
                    moves.append(move)

    def get_rook_moves(self, row, column, moves):
        piece_color = self.board[row][column][0]
        opponent_color = "b" if piece_color == "w" else "w"

        # Checking forward spaces
        i = 1
        while row - i >= 0:
            if self.board[row - i][column][0] == opponent_color or \
                    self.board[row - i][column][0] == "_":
                move = Move((row, column), (row - i, column), self.board)
                moves.append(move)
            if self.board[row - i][column][0] == opponent_color or \
                    self.board[row - i][column][0] == piece_color:
                break
            i += 1
        # Checking backward spaces
        i = 1
        while row + i <= 7:
            if self.board[row + i][column][0] == opponent_color or \
                    self.board[row + i][column][0] == "_":
                move = Move((row, column), (row + i, column), self.board)
                moves.append(move)
            if self.board[row + i][column][0] == opponent_color or \
                    self.board[row + i][column][0] == piece_color:
                break
            i += 1
        # Checking right-side spaces
        i = 1
        while column + i <= 7:
            if self.board[row][column + i][0] == opponent_color or \
                    self.board[row][column + i][0] == "_":
                move = Move((row, column), (row, column + i), self.board)
                moves.append(move)
            if self.board[row][column + i][0] == opponent_color or \
                    self.board[row][column + i][0] == piece_color:
                break
            i += 1
        # Checking left-side spaces
        i = 1
        while column - i >= 0:
            if self.board[row][column - i][0] == opponent_color or \
                    self.board[row][column - i][0] == "_":
                move = Move((row, column), (row, column - i), self.board)
                moves.append(move)
            if self.board[row][column - i][0] == opponent_color or \
                    self.board[row][column - i][0] == piece_color:
                break
            i += 1

    def get_knight_moves(self, row, column, moves):
        piece_color = self.board[row][column][0]

        if row + 2 <= 7:
            if column + 1 <= 7 and self.board[row + 2][column + 1][0] != piece_color:
                move = Move((row, column), (row + 2, column + 1), self.board)
                moves.append(move)
            if column - 1 >= 0 and self.board[row + 2][column - 1][0] != piece_color:
                move = Move((row, column), (row + 2, column - 1), self.board)
                moves.append(move)
        if row + 1 <= 7:
            if column + 2 <= 7 and self.board[row + 1][column + 2][0] != piece_color:
                move = Move((row, column), (row + 1, column + 2), self.board)
                moves.append(move)
            if column - 2 >= 0 and self.board[row + 1][column - 2][0] != piece_color:
                move = Move((row, column), (row + 1, column - 2), self.board)
                moves.append(move)
        if row - 1 >= 0:
            if column + 2 <= 7 and self.board[row - 1][column + 2][0] != piece_color:
                move = Move((row, column), (row - 1, column + 2), self.board)
                moves.append(move)
            if column - 2 >= 0 and self.board[row - 1][column - 2][0] != piece_color:
                move = Move((row, column), (row - 1, column - 2), self.board)
                moves.append(move)
        if row - 2 >= 0:
            if column + 1 <= 7 and self.board[row - 2][column + 1][0] != piece_color:
                move = Move((row, column), (row - 2, column + 1), self.board)
                moves.append(move)
            if column - 1 >= 0 and self.board[row - 2][column - 1][0] != piece_color:
                move = Move((row, column), (row - 2, column - 1), self.board)
                moves.append(move)

    def get_bishop_moves(self, row, column, moves):
        piece_color = self.board[row][column][0]
        opponent_color = "b" if piece_color == "w" else "w"

        # Checking for Top-Left spaces
        i = 1
        while row - i >= 0 and column - i >= 0:
            if self.board[row - i][column - i][0] == opponent_color or \
                    self.board[row - i][column - i][0] == "_":
                move = Move((row, column),
                            (row - i, column - i), self.board)
                moves.append(move)
            if self.board[row - i][column - i][0] == opponent_color or \
                    self.board[row - i][column - i][0] == piece_color:
                break
            i += 1
        # Checking for Top-Right spaces
        i = 1
        while row - i >= 0 and column + i <= 7:
            if self.board[row - i][column + i][0] == opponent_color or \
                    self.board[row - i][column + i][0] == "_":
                move = Move((row, column),
                            (row - i, column + i), self.board)
                moves.append(move)
            if self.board[row - i][column + i][0] == opponent_color or \
                    self.board[row - i][column + i][0] == piece_color:
                break
            i += 1
        # Checking for Bottom-Left spaces
        i = 1
        while row + i <= 7 and column - i >= 0:
            if self.board[row + i][column - i][0] == opponent_color or \
                    self.board[row + i][column - i][0] == "_":
                move = Move((row, column),
                            (row + i, column - i), self.board)
                moves.append(move)
            if self.board[row + i][column - i][0] == opponent_color or \
                    self.board[row + i][column - i][0] == piece_color:
                break
            i += 1
        # Checking for Bottom-Right spaces
        i = 1
        while row + i <= 7 and column + i <= 7:
            if self.board[row + i][column + i][0] == opponent_color or \
                    self.board[row + i][column + i][0] == "_":
                move = Move((row, column),
                            (row + i, column + i), self.board)
                moves.append(move)
            if self.board[row + i][column + i][0] == opponent_color or \
                    self.board[row + i][column + i][0] == piece_color:
                break
            i += 1

    def get_queen_moves(self, row, column, moves):
        piece_color = self.board[row][column][0]
        opponent_color = "b" if piece_color == "w" else "w"

        # Checking for Top-Left spaces
        i = 1
        while row - i >= 0 and column - i >= 0:
            if self.board[row - i][column - i][0] == opponent_color or \
                    self.board[row - i][column - i][0] == "_":
                move = Move((row, column),
                            (row - i, column - i), self.board)
                moves.append(move)
            if self.board[row - i][column - i][0] == opponent_color or \
                    self.board[row - i][column - i][0] == piece_color:
                break
            i += 1
        # Checking for Top-Right spaces
        i = 1
        while row - i >= 0 and column + i <= 7:
            if self.board[row - i][column + i][0] == opponent_color or \
                    self.board[row - i][column + i][0] == "_":
                move = Move((row, column),
                            (row - i, column + i), self.board)
                moves.append(move)
            if self.board[row - i][column + i][0] == opponent_color or \
                    self.board[row - i][column + i][0] == piece_color:
                break
            i += 1
        # Checking for Bottom-Left spaces
        i = 1
        while row + i <= 7 and column - i >= 0:
            if self.board[row + i][column - i][0] == opponent_color or \
                    self.board[row + i][column - i][0] == "_":
                move = Move((row, column),
                            (row + i, column - i), self.board)
                moves.append(move)
            if self.board[row + i][column - i][0] == opponent_color or \
                    self.board[row + i][column - i][0] == piece_color:
                break
            i += 1
        # Checking for Bottom-Right spaces
        i = 1
        while row + i <= 7 and column + i <= 7:
            if self.board[row + i][column + i][0] == opponent_color or \
                    self.board[row + i][column + i][0] == "_":
                move = Move((row, column),
                            (row + i, column + i), self.board)
                moves.append(move)
            if self.board[row + i][column + i][0] == opponent_color or \
                    self.board[row + i][column + i][0] == piece_color:
                break
            i += 1
        # Checking forward spaces
        i = 1
        while row - i >= 0:
            if self.board[row - i][column][0] == opponent_color or \
                    self.board[row - i][column][0] == "_":
                move = Move((row, column), (row - i, column), self.board)
                moves.append(move)
            if self.board[row - i][column][0] == opponent_color or \
                    self.board[row - i][column][0] == piece_color:
                break
            i += 1
        # Checking backward spaces
        i = 1
        while row + i <= 7:
            if self.board[row + i][column][0] == opponent_color or \
                    self.board[row + i][column][0] == "_":
                move = Move((row, column), (row + i, column), self.board)
                moves.append(move)
            if self.board[row + i][column][0] == opponent_color or \
                    self.board[row + i][column][0] == piece_color:
                break
            i += 1
        # Checking right-side spaces
        i = 1
        while column + i <= 7:
            if self.board[row][column + i][0] == opponent_color or \
                    self.board[row][column + i][0] == "_":
                move = Move((row, column), (row, column + i), self.board)
                moves.append(move)
            if self.board[row][column + i][0] == opponent_color or \
                    self.board[row][column + i][0] == piece_color:
                break
            i += 1
        # Checking left-side spaces
        i = 1
        while column - i >= 0:
            if self.board[row][column - i][0] == opponent_color or \
                    self.board[row][column - i][0] == "_":
                move = Move((row, column), (row, column - i), self.board)
                moves.append(move)
            if self.board[row][column - i][0] == opponent_color or \
                    self.board[row][column - i][0] == piece_color:
                break
            i += 1

    def get_king_moves(self, row, column, moves):
        piece_color = self.board[row][column][0]

        # Checking forward spaces
        if row - 1 >= 0:
            if self.board[row - 1][column][0] != piece_color:
                move = Move((row, column), (row - 1, column), self.board)
                moves.append(move)
            if column - 1 >= 0 and self.board[row - 1][column - 1][0] != piece_color:
                move = Move((row, column),
                            (row - 1, column - 1), self.board)
                moves.append(move)
            if column + 1 <= 7 and self.board[row - 1][column + 1][0] != piece_color:
                move = Move((row, column),
                            (row - 1, column + 1), self.board)
                moves.append(move)
        # Checking sideways spaces
        if column - 1 >= 0 and self.board[row][column - 1][0] != piece_color:
            move = Move((row, column), (row, column - 1), self.board)
            moves.append(move)
        if column + 1 <= 7 and self.board[row][column + 1][0] != piece_color:
            move = Move((row, column), (row, column + 1), self.board)
            moves.append(move)
        # Checking for downward spaces
        if row + 1 <= 7:
            if self.board[row + 1][column][0] != piece_color:
                move = Move((row, column), (row + 1, column), self.board)
                moves.append(move)
            if column - 1 >= 0 and self.board[row + 1][column - 1][0] != piece_color:
                move = Move((row, column),
                            (row + 1, column - 1), self.board)
                moves.append(move)
            if column + 1 <= 7 and self.board[row + 1][column + 1][0] != piece_color:
                move = Move((row, column),
                            (row + 1, column + 1), self.board)
                moves.append(move)

    def get_castling_moves(self):
        moves = []
        if self.is_white_move:
            queen_side, king_side = self.white_queen_side_castling, self.white_king_side_castling
            if queen_side or king_side:
                for opponent_move in self.previous_valid_moves:
                    # Checking if king is on check
                    if opponent_move.piece_captured[1] == "K":
                        queen_side = king_side = False
                    # Checking if squares on queen size are in check
                    elif (opponent_move.end_row == 7 and
                          (opponent_move.end_column == 2 or opponent_move.end_column == 3)):
                        queen_side = False
                    # Checking if squares on king size are in check
                    elif (opponent_move.end_row == 7 and
                          (opponent_move.end_column == 5 or opponent_move.end_column == 6)):
                        king_side = False
                if queen_side:
                    # Checking if sqaures on queen side are empty
                    for column in range(1, 4):
                        if self.board[7][column] != "__":
                            queen_side = False
                    if queen_side:
                        move = Move((7, 4), (7, 2), self.board,
                                    is_castling_move=True)
                        moves.append(move)
                if king_side:
                    # Checking if sqaures on king side are empty
                    for column in range(5, 7):
                        if self.board[7][column] != "__":
                            king_side = False
                    if king_side:
                        move = Move((7, 4), (7, 6), self.board,
                                    is_castling_move=True)
                        moves.append(move)

        else:
            queen_side, king_side = self.black_queen_side_castling, self.black_king_side_castling
            if queen_side or king_side:
                for opponent_move in self.previous_valid_moves:
                    # Checking if king is on check
                    if opponent_move.piece_captured[1] == "K":
                        queen_side = king_side = False
                    # Checking if squares on queen size are in check
                    elif (opponent_move.end_row == 0 and
                          (opponent_move.end_column == 2 or opponent_move.end_column == 3)):
                        queen_side = False
                    # Checking if squares on king size are in check
                    elif (opponent_move.end_row == 0 and
                          (opponent_move.end_column == 5 or opponent_move.end_column == 6)):
                        king_side = False
                if queen_side:
                    # Checking if sqaures on queen side are empty
                    for column in range(1, 4):
                        if self.board[0][column] != "__":
                            queen_side = False
                    if queen_side:
                        move = Move((0, 4), (0, 2), self.board,
                                    is_castling_move=True)
                        moves.append(move)
                if king_side:
                    # Checking if sqaures on king side are empty
                    for column in range(5, 7):
                        if self.board[0][column] != "__":
                            king_side = False
                    if king_side:
                        move = Move((0, 4), (0, 6), self.board,
                                    is_castling_move=True)
                        moves.append(move)

        return moves


class Move():

    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                                     "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {value: key for key, value in ranks_to_rows.items()}

    files_to_columns = {"a": 0, "b": 1, "c": 2, "d": 3,
                        "e": 4, "f": 5, "g": 6, "h": 7}
    columns_to_files = {value: key for key, value in files_to_columns.items()}

    def __init__(self, start_square, end_square, board, is_enpassant_move=False, is_castling_move=False):
        self.start_row = start_square[0]
        self.start_column = start_square[1]

        self.end_row = end_square[0]
        self.end_column = end_square[1]

        self.piece_moved = board[self.start_row][self.start_column]
        self.piece_captured = board[self.end_row][self.end_column]

        self.is_enpassant_move = is_enpassant_move

        self.is_castling_move = is_castling_move

        if self.is_enpassant_move:
            self.piece_captured = "wP" if self.piece_moved == "bP" else "bP"

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.get_chess_notation == other.get_chess_notation
        return False

    @property
    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_column) + \
            self.get_rank_file(self.end_row, self.end_column)

    def get_rank_file(self, row, column):
        return self.columns_to_files[column] + self.rows_to_ranks[row]

    @property
    def is_pawn_promotion(self):
        if self.piece_moved == "wP" and self.end_row == 0:
            return True
        elif self.piece_moved == "bP" and self.end_row == 7:
            return True
