import pygame
import engine
import AI

# Initializing global variables
WIDTH = HEIGHT = 512
DIMENSION = 8
SQUARE_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

# Loading images as a dictionary with key == piece identifier and \
# value == directiory to the image file in folder


def load_images():
    pieces = ["wR", "wN", "wB", "wQ", "wK", "wP",
              "bR", "bN", "bB", "bQ", "bK", "bP"]

    for piece in pieces:
        IMAGES[piece] = pygame.transform.scale(pygame.image.load(
            "ChessEngine/images/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE))


def main():
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    screen.fill(pygame.Color("white"))
    # game state keeps track of pieces positions on board
    game_state = engine.GameState()

    load_images()

    running = True
    initial_square_selected = ()
    squares_clicked = []

    valid_moves = game_state.get_valid_moves()
    move_made = False
    animate = False
    game_over = False

    is_white_human = True
    is_black_human = False

    while running:
        is_human_turn = (game_state.is_white_move and is_white_human) or (
            not game_state.is_white_move and is_black_human)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Evaluating which square(s) was/were being clicked on when \
            # making a move
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not game_over:
                    location = pygame.mouse.get_pos()
                    column = location[0] // SQUARE_SIZE
                    row = location[1] // SQUARE_SIZE

                    if initial_square_selected == (row, column):
                        initial_square_selected = ()
                        squares_clicked = []
                    # Incase the same square is clicked again
                    else:
                        initial_square_selected = (row, column)
                        squares_clicked.append(initial_square_selected)
                    # When 2 distinct squares are clicked, our move is complete and \
                    # ready to be evaluated
                    if len(squares_clicked) == 2:
                        move = engine.Move(
                            squares_clicked[0], squares_clicked[1], game_state.board)
                        # Checking if move is valid, otherwise ignore it
                        for valid_move in valid_moves:
                            if move == valid_move and valid_move.is_enpassant_move:
                                move.is_enpassant_move = True
                                game_state.make_move(move)
                                move_made = True
                                animate = True
                                break
                            if move.is_pawn_promotion and move == valid_move:
                                game_state.make_move(move)
                                move_made = True
                                animate = True
                                break
                            if valid_move.is_castling_move and move == valid_move:
                                move.is_castling_move = True
                                game_state.make_move(move)
                                move_made = True
                                animate = True
                                break
                            elif move == valid_move:
                                game_state.make_move(move)
                                move_made = True
                                animate = True
                                break
                        initial_square_selected = ()
                        squares_clicked = []
            # Incase player wishes to undo their move
            elif event.type == pygame.KEYDOWN:
                # Press key "z" to undo
                if event.key == pygame.K_z and len(game_state.move_log):
                    game_state.undo_move()
                    game_state.undo_move()
                    move_made = True
                    game_over = False

                # Press key "r" to reset the game
                if event.key == pygame.K_r:
                    game_state = engine.GameState()
                    valid_moves = game_state.get_valid_moves()
                    move_made = False
                    animate = False
                    initial_square_selected = ()
                    squares_clicked = []
                    game_over = False

            elif not game_over and not is_human_turn:
                AI_move = AI.find_best_move(game_state, valid_moves)
                if not AI_move:
                    AI_move = AI.random_move(valid_moves)
                game_state.make_move(AI_move)
                move_made = True
                animate = True
                is_human_turn = True

            # Once a valid move has been made, get new valid moves \
            # w.r.t the new game state(pieces positioning)
            if move_made:
                if animate:
                    animate_move(
                        game_state.move_log[-1], screen, game_state.board, clock)
                animate = False

                if (game_state.is_white_move and (game_state.white_queen_side_castling or game_state.white_king_side_castling)) or \
                        (not game_state.is_white_move and (game_state.black_king_side_castling or game_state.black_queen_side_castling)):
                    # Storing so it doesnt get altered when finding valid_moves
                    temp = game_state.enpassant_possible
                    game_state.enpassant_possible = ()

                    # Getting previous_valid_moves to check castling rights
                    game_state.is_white_move = not game_state.is_white_move
                    game_state.previous_valid_moves = game_state.get_valid_moves()
                    game_state.is_white_move = not game_state.is_white_move

                    # Getting it back to its original value
                    game_state.enpassant_possible = temp

                valid_moves = game_state.get_valid_moves()
                move_made = False

        # Visualizing the current game state of chee board
        draw_chess_board(screen, game_state, valid_moves,
                         initial_square_selected)

        if game_state.stale_mate:
            game_over = True
            text = "Stalemate"
            draw_text(screen, text)
        elif game_state.check_mate:
            game_over = True
            team_won = "White" if not game_state.is_white_move else "Black"
            text = team_won + " wins by Checkmate"
            draw_text(screen, text)

        clock.tick(MAX_FPS)
        pygame.display.flip()


# Handles all graphics within the game
def draw_chess_board(screen, game_state, valid_moves, square_selected):
    draw_squares(screen)
    highlight_square(screen, game_state, valid_moves, square_selected)
    draw_pieces(screen, game_state.board)


# Draw squares on the board
def draw_squares(screen):
    global colors
    colors = {"white": pygame.Color(
        "white"), "grey": pygame.Color("grey")}

    # Dimensions = 8x8 which is the number of sqaures present in chess board
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            if (row + column) % 2 == 0:
                pygame.draw.rect(screen, colors["white"], pygame.Rect(
                    column*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            else:
                pygame.draw.rect(screen, colors["grey"], pygame.Rect(
                    column*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


# Drawing the pieces over them squares on screen
def draw_pieces(screen, board):
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            piece = board[row][column]
            if piece != "__":
                # IMAGES id the dictionary containing all the images
                screen.blit(IMAGES[piece],  pygame.Rect(
                    column*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


# Highlight square selected and the valid squares where the move can be made
def highlight_square(screen, game_state, valid_moves, square_selected):
    if square_selected:
        row, column = square_selected
        if (game_state.board[row][column][0] == "w" and game_state.is_white_move) or \
                (game_state.board[row][column][0] == "b" and not game_state.is_white_move):
            # Highlighting the square selected = Blue
            surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
            surface.set_alpha(100)
            surface.fill(pygame.Color('blue'))
            screen.blit(surface, (column * SQUARE_SIZE, row * SQUARE_SIZE))
            # Higlighting the possible moves squares
            for move in valid_moves:
                if move.start_row == row and move.start_column == column:
                    # Highlighting the sqaure if the move captures opponents piece
                    if move.piece_captured != "__":
                        surface.fill(pygame.Color('red'))
                        screen.blit(surface, (move.end_column *
                                              SQUARE_SIZE, move.end_row * SQUARE_SIZE))
                    else:
                        # Otheriwse, if it is a neutral move, highlight it as yellow
                        surface.fill(pygame.Color('yellow'))
                        screen.blit(surface, (move.end_column *
                                              SQUARE_SIZE, move.end_row * SQUARE_SIZE))


# Animating the move motion of the piece
def animate_move(move, screen, board, clock):
    colors = [pygame.Color("white"), pygame.Color("grey")]

    delta_row = move.end_row - move.start_row
    delta_column = move.end_column - move.start_column

    frames_per_square = 10
    total_frames = frames_per_square * (abs(delta_row) + abs(delta_column))

    for frame in range(total_frames + 1):
        row, column = (move.start_row + (delta_row * frame / total_frames),
                       move.start_column + (delta_column * frame / total_frames))

        draw_squares(screen)
        draw_pieces(screen, board)

        color = colors[(move.end_row + move.end_column) % 2]
        end_square = pygame.Rect(move.end_column * SQUARE_SIZE,
                                 move.end_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        pygame.draw.rect(screen, color, end_square)

        if move.piece_captured != "__":
            screen.blit(IMAGES[move.piece_captured], end_square)

        screen.blit(IMAGES[move.piece_moved], pygame.Rect(
            column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        pygame.display.flip()
        clock.tick(60)


def draw_text(screen, text):
    font = pygame.font.SysFont("Helvitca", 32, True, False)
    text_object = font.render(text, 0, pygame.Color("black"))
    text_location = pygame.Rect(0, 0, WIDTH, HEIGHT).move(
        WIDTH/2 - text_object.get_width()/2, HEIGHT/2 - text_object.get_height()/2)
    screen.blit(text_object, text_location.move(2, 2))
    pygame.display.flip()


if __name__ == "__main__":
    main()
