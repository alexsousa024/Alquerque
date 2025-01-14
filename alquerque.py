import sys
import random
import pygame
from multiprocessing import Pool

# Cores
WHITE = (236, 240, 232)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Configurações do tabuleiro
BOARD_SIZE = 5
SQUARE_SIZE = 80
WIDTH = HEIGHT = SQUARE_SIZE * BOARD_SIZE
FPS = 30
# Espaços do tabuleiro e peças respetivas

EMPTY = 0
PLAYER1 = 1
PLAYER2 = 2
turn = PLAYER1
# Outras váriaveis:

selected_piece = None
valid_moves = []

# Variavel utilizada para verificar se um movimento em captura está a decorrer (útil para capturas múltiplas)
capture_in_progress = None


# tabuleiro 5 x 5  - tipíco do tabuleiro do Alquerque
def create_board():
    board = [
        [PLAYER2, PLAYER2, PLAYER2, PLAYER2, PLAYER2],
        [PLAYER2, PLAYER2, PLAYER2, PLAYER2, PLAYER2],
        [PLAYER2, PLAYER2, EMPTY, PLAYER1, PLAYER1],
        [PLAYER1, PLAYER1, PLAYER1, PLAYER1, PLAYER1],
        [PLAYER1, PLAYER1, PLAYER1, PLAYER1, PLAYER1],
    ]
    return board


# Função que desenha as peças redondas e liga-as ao PLAYER 1 e PLAYER2
def draw_pieces(screen, board):
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            piece = board[y][x]
            if piece == PLAYER1:
                pygame.draw.circle(screen, RED,
                                   (x * SQUARE_SIZE + SQUARE_SIZE // 2, y * SQUARE_SIZE + SQUARE_SIZE // 2),
                                   SQUARE_SIZE // 4)
            elif piece == PLAYER2:
                pygame.draw.circle(screen, BLUE,
                                   (x * SQUARE_SIZE + SQUARE_SIZE // 2, y * SQUARE_SIZE + SQUARE_SIZE // 2),
                                   SQUARE_SIZE // 4)


# Função que desenha o tabuleiro(com as linhas tipícias do tabuleiro de Alquerque)
def draw_board(screen, board, mode):
    screen.fill(WHITE)

    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            color = WHITE

            pygame.draw.rect(screen, color, (x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            pygame.draw.circle(screen, BLACK, (x * SQUARE_SIZE + SQUARE_SIZE // 2, y * SQUARE_SIZE + SQUARE_SIZE // 2),
                               3)
            # Linhas horizontais
            if x < BOARD_SIZE - 1:
                pygame.draw.line(screen, BLACK,
                                 (x * SQUARE_SIZE + SQUARE_SIZE // 2, y * SQUARE_SIZE + SQUARE_SIZE // 2),
                                 ((x + 1) * SQUARE_SIZE + SQUARE_SIZE // 2, y * SQUARE_SIZE + SQUARE_SIZE // 2))
            # Linhas verticais
            if y < BOARD_SIZE - 1:
                pygame.draw.line(screen, BLACK,
                                 (x * SQUARE_SIZE + SQUARE_SIZE // 2, y * SQUARE_SIZE + SQUARE_SIZE // 2),
                                 (x * SQUARE_SIZE + SQUARE_SIZE // 2, (y + 1) * SQUARE_SIZE + SQUARE_SIZE // 2))

    # linhas diagonais
    pygame.draw.line(screen, BLACK, (SQUARE_SIZE // 2, SQUARE_SIZE // 2),
                     ((BOARD_SIZE - 1) * SQUARE_SIZE + SQUARE_SIZE // 2,
                      (BOARD_SIZE - 1) * SQUARE_SIZE + SQUARE_SIZE // 2))
    pygame.draw.line(screen, BLACK, ((BOARD_SIZE - 1) * SQUARE_SIZE + SQUARE_SIZE // 2, SQUARE_SIZE // 2),
                     (SQUARE_SIZE // 2, (BOARD_SIZE - 1) * SQUARE_SIZE + SQUARE_SIZE // 2))
    pygame.draw.line(screen, BLACK, ((BOARD_SIZE - 3) * SQUARE_SIZE + SQUARE_SIZE // 2, SQUARE_SIZE // 2),
                     (SQUARE_SIZE // 2, (BOARD_SIZE - 3) * SQUARE_SIZE + SQUARE_SIZE // 2))
    pygame.draw.line(screen, BLACK, (SQUARE_SIZE // 2, (BOARD_SIZE - 3) * SQUARE_SIZE + SQUARE_SIZE // 2),
                     ((BOARD_SIZE - 3) * SQUARE_SIZE + SQUARE_SIZE // 2,
                      (BOARD_SIZE - 1) * SQUARE_SIZE + SQUARE_SIZE // 2))
    pygame.draw.line(screen, BLACK, ((BOARD_SIZE - 3) * SQUARE_SIZE + SQUARE_SIZE // 2, SQUARE_SIZE // 2),
                     ((BOARD_SIZE - 1) * SQUARE_SIZE + SQUARE_SIZE // 2,
                      (BOARD_SIZE - 3) * SQUARE_SIZE + SQUARE_SIZE // 2))
    pygame.draw.line(screen, BLACK, (
        (BOARD_SIZE - 1) * SQUARE_SIZE + SQUARE_SIZE // 2, (BOARD_SIZE - 3) * SQUARE_SIZE + SQUARE_SIZE // 2),
                     ((BOARD_SIZE - 3) * SQUARE_SIZE + SQUARE_SIZE // 2,
                      (BOARD_SIZE - 1) * SQUARE_SIZE + SQUARE_SIZE // 2))

    draw_pieces(screen, board)

    if selected_piece:
        x, y = selected_piece
        pygame.draw.circle(screen, (255, 255, 0),
                           (x * SQUARE_SIZE + SQUARE_SIZE // 2, y * SQUARE_SIZE + SQUARE_SIZE // 2), SQUARE_SIZE // 4,
                           3)

    for x, y in valid_moves:
        pygame.draw.circle(screen, (0, 255, 0),
                           (x * SQUARE_SIZE + SQUARE_SIZE // 2, y * SQUARE_SIZE + SQUARE_SIZE // 2), SQUARE_SIZE // 8)
    if mode != 3:
        highlight_movable_pieces(screen, board, turn, capture_in_progress)


# Verificação de se o movimento diagonal é um movimento válido, visto que nem todas as diagonais existem no tabuleiro
def is_valid_diagonal(x1, y1, x2, y2):
    if x1 == x2 or y1 == y2:
        return False

    if abs(x1 - x2) == abs(y1 - y2):
        return (x1 + y1) % 2 == 0 or (x1 == y1) or (x1 == BOARD_SIZE - 1 - y1)

    return False


# Função que verifica que, dado uma posição de uma peça, existem peças adversarias adjacentes, e espaços vazios na posição posterior,
# de forma a verificar se existem movimentos de captura
def has_capture_moves(board, player):
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            if board[y][x] == player:
                capture_moves = get_capture_moves(board, x, y, player)
                if len(capture_moves) > 0:
                    return True
    return False


# Função que calcula as movimentos de captura possíveis
def get_capture_moves(board, x, y, player):
    capture_moves = []
    opponent = PLAYER2 if player == PLAYER1 else PLAYER1
    directions = [(-1, -1), (-1, 1), (1, -1), (1, 1), (0, 1), (1, 0), (0, -1), (-1, 0)]

    for dx, dy in directions:
        new_x, new_y = x + dx, y + dy
        if 0 <= new_x < BOARD_SIZE and 0 <= new_y < BOARD_SIZE:
            if board[new_y][new_x] == opponent:
                capture_x, capture_y = new_x + dx, new_y + dy
                if 0 <= capture_x < BOARD_SIZE and 0 <= capture_y < BOARD_SIZE and board[capture_y][capture_x] == EMPTY:
                    if dx == 0 or dy == 0 or is_valid_diagonal(x, y, capture_x, capture_y):
                        capture_moves.append((capture_x, capture_y))
    return capture_moves


# Função que calcula os movimentos válidos, incluindo aqui os movimentos simples, e os movimentos de captura.
def get_valid_moves(board, x, y, player):
    moves = []
    opponent = PLAYER2 if player == PLAYER1 else PLAYER1
    directions = [(-1, -1), (-1, 1), (1, -1), (1, 1), (0, 1), (1, 0), (0, -1), (-1, 0)]
    capture_moves = get_capture_moves(board, x, y, player)
    for dx, dy in directions:
        new_x, new_y = x + dx, y + dy
        if 0 <= new_x < BOARD_SIZE and 0 <= new_y < BOARD_SIZE:
            if board[new_y][new_x] == EMPTY and (dx == 0 or dy == 0 or is_valid_diagonal(x, y, new_x, new_y)):
                moves.append((new_x, new_y))
            elif board[new_y][new_x] == opponent:
                capture_x, capture_y = new_x + dx, new_y + dy
                if 0 <= capture_x < BOARD_SIZE and 0 <= capture_y < BOARD_SIZE and board[capture_y][capture_x] == EMPTY:
                    if dx == 0 or dy == 0 or is_valid_diagonal(new_x, new_y, capture_x, capture_y):
                        moves.append((capture_x, capture_y))
    if has_capture_moves(board, player):
        moves = capture_moves

    return moves


# Verifica se o player em questão ganhou o jogo, vendo se existem peças adversárias
def check_win(board, player):
    opponent = PLAYER1 if player == PLAYER2 else PLAYER2
    return not any(opponent in row for row in board)


# Verifica se existe um empate, vendo se existe uma peça por cada jogador e se não existem movimentos de captura possiveis!
def is_draw(board):
    player1_pieces = sum(row.count(PLAYER1) for row in board)
    player2_pieces = sum(row.count(PLAYER2) for row in board)

    if player1_pieces == 1 and player2_pieces == 1:
        player1_capture_moves = has_capture_moves(board, PLAYER1)
        player2_capture_moves = has_capture_moves(board, PLAYER2)

        if not player1_capture_moves and not player2_capture_moves:
            return True

    return False


# Faz a peça saltar a peça adversária, verificando primeiro de é uma diagonal válida
def is_capture_move(board, x1, y1, x2, y2, player):
    if abs(x1 - x2) == 2 and abs(y1 - y2) == 2:
        if is_valid_diagonal(x1, y1, x2, y2):
            captured_x, captured_y = (x1 + x2) // 2, (y1 + y2) // 2
            opponent = PLAYER2 if player == PLAYER1 else PLAYER1
            return board[captured_y][captured_x] == opponent
    elif (abs(x1 - x2) == 2 and y1 == y2) or (abs(y1 - y2) == 2 and x1 == x2):
        captured_x, captured_y = (x1 + x2) // 2, (y1 + y2) // 2
        opponent = PLAYER2 if player == PLAYER1 else PLAYER1
        return board[captured_y][captured_x] == opponent
    return False


# Operador - Movimento a peça do tabuleiro e verifica e executa os movimentos de captura
def move_piece(board, x1, y1, x2, y2, player):
    board[y2][x2] = board[y1][x1]
    board[y1][x1] = EMPTY
    if is_capture_move(board, x1, y1, x2, y2, player):
        capture_piece(board, x1, y1, x2, y2)
        return True
    return False


# Verifica se existem movimentos de captura adicionais(útil na função main)
def check_additional_capture_moves(board, x, y, player):
    capture_moves = get_capture_moves(board, x, y, player)
    return len(capture_moves) > 0


# Remove a peça capturada
def capture_piece(board, x1, y1, x2, y2):
    captured_x, captured_y = (x1 + x2) // 2, (y1 + y2) // 2
    board[captured_y][captured_x] = EMPTY


# Função para dar destaque ás peças que se conseguem mover, para ajudar no modo: Player vs Player (pygame)
def highlight_movable_pieces(screen, board, player, capture_in_progress):
    has_capture = has_capture_moves(board, player)
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            if board[y][x] == player:
                moves = get_valid_moves(board, x, y, player)
                if len(moves) > 0:
                    if has_capture:
                        for move in moves:
                            if is_capture_move(board, x, y, move[0], move[1], player):
                                if capture_in_progress is None or capture_in_progress == (x, y):
                                    pygame.draw.circle(screen, (255, 255, 0),
                                                       (x * SQUARE_SIZE + SQUARE_SIZE // 2,
                                                        y * SQUARE_SIZE + SQUARE_SIZE // 2),
                                                       SQUARE_SIZE // 4, 3)
                                    break
                    else:
                        if capture_in_progress is None:
                            pygame.draw.circle(screen, (255, 255, 0),
                                               (x * SQUARE_SIZE + SQUARE_SIZE // 2, y * SQUARE_SIZE + SQUARE_SIZE // 2),
                                               SQUARE_SIZE // 4, 3)


# Menu Inicial  - Pygame
def menu_screen(screen, cpu_vs_cpu):
    menu_font = pygame.font.Font(None, 36)
    option1_text = menu_font.render("Player vs. Player", True, BLACK)
    option2_text = menu_font.render("Player vs. CPU", True, BLACK)
    option3_text = menu_font.render("CPU vs. CPU", True, BLACK)
    rules_text = menu_font.render("Rules", True, BLACK)

    option1_rect = option1_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
    option2_rect = option2_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    option3_rect = option3_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
    rules_rect = rules_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120))

    menu = True
    while menu:
        screen.fill(WHITE)
        screen.blit(option1_text, option1_rect)
        screen.blit(option2_text, option2_rect)
        screen.blit(option3_text, option3_rect)
        screen.blit(rules_text, rules_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if option1_rect.collidepoint(mouse_x, mouse_y):
                    menu = False
                    return 1, None
                elif option2_rect.collidepoint(mouse_x, mouse_y):
                    menu = False
                    cpu_difficulty = cpu_difficulty_screen(screen, cpu_vs_cpu=False)

                    if cpu_difficulty != 0:
                        return 2, cpu_difficulty
                elif option3_rect.collidepoint(mouse_x, mouse_y):
                    menu = False
                    cpu_difficulties = cpu_vs_cpu_difficulty_screen(screen)
                    return 3, cpu_difficulties
                elif rules_rect.collidepoint(mouse_x, mouse_y):
                    menu = True
                    rules_menu(screen)


# Menu de dificuldade da CPU para o modo jogador vs CPU
def cpu_difficulty_screen(screen, cpu_vs_cpu=False):
    title_font = pygame.font.Font(None, 35)
    menu_font = pygame.font.Font(None, 28)
    title_text = "Select CPU Difficulty"
    difficulty_title = title_font.render(title_text, True, BLACK)

    difficulties = ["Easy", "Medium", "Hard"]

    difficulty_rects = []
    for i, diff in enumerate(difficulties):
        difficulty_text = menu_font.render(diff, True, BLACK)
        difficulty_rect = difficulty_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100 + i * 50))
        difficulty_rects.append(difficulty_rect)

    while True:
        screen.fill(WHITE)
        screen.blit(difficulty_title, (WIDTH // 2 - difficulty_title.get_width() // 2, 10))

        for i, diff in enumerate(difficulties):
            difficulty_text = menu_font.render(diff, True, BLACK)
            screen.blit(difficulty_text, difficulty_rects[i])

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for i, rect in enumerate(difficulty_rects):
                    if rect.collidepoint(mouse_x, mouse_y):
                        return i + 1, None


# Menu de difuldade das cpu no modo CPU vs CPU
def cpu_vs_cpu_difficulty_screen(screen):
    title_font = pygame.font.Font(None, 35)
    menu_font = pygame.font.Font(None, 28)
    title_text = "Select CPU 1 Difficulty"
    difficulty_title = title_font.render(title_text, True, BLACK)

    difficulties = ["Easy", "Medium", "Hard"]

    difficulty_rects = []
    for i, diff in enumerate(difficulties):
        difficulty_text = menu_font.render(diff, True, BLACK)
        difficulty_rect = difficulty_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100 + i * 50))
        difficulty_rects.append(difficulty_rect)

    while True:
        screen.fill(WHITE)
        screen.blit(difficulty_title, (WIDTH // 2 - difficulty_title.get_width() // 2, 10))

        for i, diff in enumerate(difficulties):
            difficulty_text = menu_font.render(diff, True, BLACK)
            screen.blit(difficulty_text, difficulty_rects[i])

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for i, rect in enumerate(difficulty_rects):
                    if rect.collidepoint(mouse_x, mouse_y):
                        difficulty_player1 = i + 1

                        title_text = "Select CPU 2 Difficulty"
                        difficulty_title = title_font.render(title_text, True, BLACK)
                        screen.fill(WHITE)
                        screen.blit(difficulty_title, (WIDTH // 2 - difficulty_title.get_width() // 2, 10))

                        for i, diff in enumerate(difficulties):
                            difficulty_text = menu_font.render(diff, True, BLACK)
                            screen.blit(difficulty_text, difficulty_rects[i])

                        pygame.display.flip()

                        event = pygame.event.wait()
                        while event.type != pygame.MOUSEBUTTONDOWN:
                            event = pygame.event.poll()
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()

                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        for i, rect in enumerate(difficulty_rects):
                            if rect.collidepoint(mouse_x, mouse_y):
                                difficulty_player2 = i + 1
                                return difficulty_player1, difficulty_player2


# Menu de resultado, tanto de vitoria ou empate.
def end_screen(screen, result):
    end_font = pygame.font.Font(None, 36)
    result_text = end_font.render(result, True, BLACK)
    result_rect = result_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))

    restart_text = end_font.render("Press R to restart or Q to quit.", True, BLACK)
    restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))

    end = True
    while end:
        screen.fill(WHITE)
        screen.blit(result_text, result_rect)
        screen.blit(restart_text, restart_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r:
                    end = False


# Menu das regras

def rules_menu(screen):
    title_font = pygame.font.Font(None, 35)
    menu_font = pygame.font.Font(None, 28)
    rules_title = title_font.render("Alquerque Rules", True, BLACK)

    rules_text = [
        ["1. Game played on 5x5 grid",
         "   with diagonals.",
         "2. Each player has 12 pieces on the",
         "   board.",
         "3. Players take turns moving one",
         "   piece to an adjacent empty point.",
         "4. Pieces jump over opponent's ",
         "   pieces to capture them.", ],
        [
            "5. Jumping can be chained in one",
            "   turn.",
            "6. Player capturing all opponent's ",
            "   pieces wins.",
            "7. Draws happen when the same ",
            "   moves are repeated 3 times ",
            "   or if both players only have ",
            "   one piece"]
    ]

    back_text = menu_font.render("Back", True, BLACK)
    back_rect = back_text.get_rect(center=(WIDTH // 4, HEIGHT - 50))

    next_text = menu_font.render("Next", True, BLACK)
    next_rect = next_text.get_rect(center=(3 * WIDTH // 4, HEIGHT - 50))

    page = 0
    rules = True
    while rules:
        screen.fill(WHITE)
        screen.blit(rules_title, (WIDTH // 2 - rules_title.get_width() // 2, 10))
        for i, line in enumerate(rules_text[page]):
            rule_line = menu_font.render(line, True, BLACK)
            screen.blit(rule_line, (50, 60 + i * 30))

        screen.blit(back_text, back_rect)
        if page == 0:
            screen.blit(next_text, next_rect)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if back_rect.collidepoint(mouse_x, mouse_y):
                    if page == 0:
                        rules = False
                    else:
                        page -= 1
                elif next_rect.collidepoint(mouse_x, mouse_y) and page == 0:
                    page += 1


# CPU
# Função para melhor a função de heurística

# Funlão utilizada para simular jogos inteiros com movimentos aleatórios
def random_playout(board, player):
    current_player = player
    opponent = PLAYER2 if player == PLAYER1 else PLAYER1

    while not (check_win(board, player) or check_win(board, opponent) or is_draw(board)):
        all_moves = []
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                if board[y][x] == current_player:
                    moves = get_valid_moves(board, x, y, current_player)
                    for move in moves:
                        all_moves.append((x, y, move[0], move[1]))

        if not all_moves:
            break

        x1, y1, x2, y2 = random.choice(all_moves)
        captured = move_piece(board, x1, y1, x2, y2, current_player)
        if captured:
            capture_piece(board, x1, y1, x2, y2)

        current_player = opponent
        opponent = PLAYER2 if current_player == PLAYER1 else PLAYER1

    if check_win(board, player):
        return 1
    elif check_win(board, opponent):
        return -1
    else:
        return 0

    
# Função Monte Carlo Tree Search 

def simulate_move(move, board, player, simulations):
    x1, y1, x2, y2 = move
    new_board = [row.copy() for row in board]
    captured = move_piece(new_board, x1, y1, x2, y2, player)
    if captured:
        capture_piece(new_board, x1, y1, x2, y2)

    wins = 0
    for _ in range(simulations):
        playout_board = [row.copy() for row in new_board]
        wins += random_playout(playout_board, player)

    return wins

def monte_carlo_tree_search(board, player, simulations):
    best_move = None
    best_score = float('-inf')

    all_moves = []
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            if board[y][x] == player:
                moves = get_valid_moves(board, x, y, player)
                for move in moves:
                    all_moves.append((x, y, move[0], move[1]))

    with Pool() as pool:
        scores = pool.starmap(simulate_move, [(move, board, player, simulations) for move in all_moves])

    if scores:
        best_score = max(scores)
        best_move_index = scores.index(best_score)
        best_move = all_moves[best_move_index]

    return best_move

#Função Minimax
def evaluate(board, player, board_positions):
    opponent = PLAYER2 if player == PLAYER1 else PLAYER1
    player_score = 0
    opponent_score = 0

    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            if board[y][x] == player:
                player_score += 1 + (BOARD_SIZE // 2 - abs(x - BOARD_SIZE // 2)) * 0.1 + (BOARD_SIZE // 2 - abs(y - BOARD_SIZE // 2)) * 0.1
            elif board[y][x] == opponent:
                opponent_score += 1 + (BOARD_SIZE // 2 - abs(x - BOARD_SIZE // 2)) * 0.1 + (BOARD_SIZE // 2 - abs(y - BOARD_SIZE // 2)) * 0.1

    current_board_position = str(board)
    if current_board_position in board_positions[player]:
        player_score -= 1 * board_positions[player][current_board_position]

    return player_score - opponent_score


#Monte Carlo Tree Search 
def minimax(board, depth, alpha, beta, maximizing_player, player, board_positions):
    opponent = PLAYER2 if player == PLAYER1 else PLAYER1

    if depth == 0 or check_win(board, player) or check_win(board, opponent):
        return evaluate(board, player, board_positions) * (1 if maximizing_player else -1) * depth

    if maximizing_player:
        max_eval = float('-inf')
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                if board[y][x] == player:
                    moves = get_valid_moves(board, x, y, player)
                    for move in moves:
                        new_board = [row.copy() for row in board]
                        move_piece(new_board, x, y, move[0], move[1], player)
                        eval = minimax(new_board, depth - 1, alpha, beta, False, player, board_positions)
                        max_eval = max(max_eval, eval)
                        alpha = max(alpha, eval)
                        if beta <= alpha:
                            break
        return max_eval

    else:
        min_eval = float('inf')
        opponent = PLAYER2 if player == PLAYER1 else PLAYER1
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                if board[y][x] == opponent:
                    moves = get_valid_moves(board, x, y, opponent)
                    for move in moves:
                        new_board = [row.copy() for row in board]
                        move_piece(new_board, x, y, move[0], move[1], opponent)
                        eval = minimax(new_board, depth - 1, alpha, beta, True, player, board_positions)
                        min_eval = min(min_eval, eval)
                        beta = min(beta, eval)
                        if beta <= alpha:
                            break
        return min_eval



def get_best_move(board, depth, player, board_positions):
    best_move = None
    best_value = float('-inf')

    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            if board[y][x] == player:
                moves = get_valid_moves(board, x, y, player)
                for move in moves:
                    new_board = [row.copy() for row in board]
                    captured = move_piece(new_board, x, y, move[0], move[1], player)
                    if captured:
                        capture_piece(new_board, x, y, move[0], move[1])
                    move_value = minimax(new_board, depth - 1, float('-inf'), float('inf'), False, player, board_positions)

                    if move_value > best_value:
                        best_value = move_value
                        best_move = (x, y, move[0], move[1])

    return best_move





def handle_cpu_turn(board, difficulty1, difficulty2, turn, board_positions, algorithm):
    simulations_mapping = {1: 200, 2: 400, 3: 1000}
    depth_mapping = {1: 2, 2: 4, 3: 6}
    

    if algorithm == 0:  # 
        if turn == PLAYER1:
            depth = depth_mapping[difficulty1]
        else:
            depth = depth_mapping[difficulty2]
        best_move = get_best_move(board, depth, player)  
    elif algorithm == 1:  # Monte Carlo Tree Search
        if turn == PLAYER1:
            simulations = simulations_mapping[difficulty1]
        else:
            simulations = simulations_mapping[difficulty2]
        best_move = monte_carlo_tree_search(board, turn, simulations)

    if best_move:
        x1, y1, x2, y2 = best_move
        captured = move_piece(board, x1, y1, x2, y2, turn)
        if captured:
            capture_piece(board, x1, y1, x2, y2)
        return x2, y2, captured
    return None

#Menu de seleção do algoritmo 
def algorithm_selection_menu(screen):
    font = pygame.font.Font(None, 36)
    title_font = pygame.font.Font(None, 50)
    title = title_font.render("Escolha o algoritmo da CPU", True, BLACK)
    mcts_text = font.render("1. Monte Carlo Tree Search (MCTS)", True, BLACK)
    minimax_text = font.render("2. Minimax", True, BLACK)
    option_text = font.render("Pressione 1 ou 2 para selecionar", True, BLACK)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return 1  # MCTS
                if event.key == pygame.K_2:
                    return 0  # Minimax

        screen.fill(WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3 - title.get_height() // 2))
        screen.blit(mcts_text, (WIDTH // 2 - mcts_text.get_width() // 2, HEIGHT // 2 - mcts_text.get_height() // 2))
        screen.blit(minimax_text, (WIDTH // 2 - minimax_text.get_width() // 2, HEIGHT // 2 + minimax_text.get_height()))
        screen.blit(option_text, (WIDTH // 2 - option_text.get_width() // 2, HEIGHT - option_text.get_height() * 2))
        pygame.display.update()



# FUNÇÃO MAIN
def main(mode, difficulty, difficulty2=None, cpu_vs_cpu=False,algorithm = 0):
    global turn, selected_piece, valid_moves
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Alquerque")
    clock = pygame.time.Clock()

    board = create_board()
    additional_capture = False
    capture_in_progress = None
    board_positions = {PLAYER1: {}, PLAYER2: {}}
    current_board_position = str(board)

    while True:
        game_over = False
        win_message = None
        # MODO 2 - Jogador vs CPU e é a vez do CPU a jogar
        if mode == 2 and turn == PLAYER2 and not cpu_vs_cpu:
            cpu_result = handle_cpu_turn(board, difficulty, difficulty2, turn, board_positions, algorithm)
            if cpu_result:
                grid_x, grid_y, captured = cpu_result
                if not captured or not check_additional_capture_moves(board, grid_x, grid_y, turn):
                    turn = PLAYER1
        # Modo 3 - CPU VS CPU:
        if cpu_vs_cpu:
            if turn == PLAYER1:
                current_difficulty = difficulty
            else:
                current_difficulty = difficulty2

            if is_draw(board):
                end_screen(screen, "Draw by lack of material")
                board_positions = {}
                board = create_board()
                turn = PLAYER1
            cpu_turn = handle_cpu_turn(board, current_difficulty, current_difficulty, turn, board_positions, algorithm)

            if cpu_turn:
                grid_x, grid_y, captured = cpu_turn
                if not captured or not check_additional_capture_moves(board, grid_x, grid_y, turn):
                    turn = PLAYER2 if turn == PLAYER1 else PLAYER1
                    # Verifica se as jogadas repetidas e se os movimentos forem repetidos mais que 3 vezes, termina o jogo.
                    current_board_position = str(board)
                    board_positions[turn][current_board_position] = board_positions[turn].get(current_board_position,
                                                                                              0) + 1
                    if board_positions[turn][current_board_position] >= 3:
                        game_over = True
                        win_message = "Draw by repetition"
            else:
                turn = PLAYER2 if turn == PLAYER1 else PLAYER1

        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            grid_x, grid_y = x // SQUARE_SIZE, y // SQUARE_SIZE

            if selected_piece and selected_piece == (grid_x, grid_y):
                selected_piece = None
                valid_moves = []
            elif mode == 1 or mode == 2:
                if not selected_piece:
                    if board[grid_y][grid_x] == turn:
                        if not capture_in_progress or capture_in_progress == (grid_x, grid_y):
                            selected_piece = (grid_x, grid_y)
                            valid_moves = get_valid_moves(board, grid_x, grid_y, turn)
                else:
                    if (grid_x, grid_y) in valid_moves:
                        captured = move_piece(board, selected_piece[0], selected_piece[1], grid_x, grid_y, turn)

                        if not captured or not check_additional_capture_moves(board, grid_x, grid_y, turn):
                            turn = PLAYER2 if turn == PLAYER1 else PLAYER1
                            additional_capture = False
                            capture_in_progress = None
                        else:
                            additional_capture = True
                            capture_in_progress = (grid_x, grid_y)

                        selected_piece = None
                        valid_moves = []
                        current_board_position = str(board)
                        board_positions[turn][current_board_position] = board_positions[turn].get(
                            current_board_position, 0) + 1

                        if board_positions[turn][current_board_position] >= 3:
                            game_over = True
                            win_message = "Draw by repetition"

                        if check_win(board, PLAYER1):
                            game_over = True
                            win_message = "Player 1 wins!"
                        elif check_win(board, PLAYER2):
                            game_over = True
                            win_message = "Player 2 wins!"

            elif board[grid_y][grid_x] == turn:
                if not capture_in_progress or capture_in_progress == (grid_x, grid_y):
                    selected_piece = (grid_x, grid_y)
                    valid_moves = get_valid_moves(board, grid_x, grid_y, turn)

        if mode == 2 and turn == PLAYER2 and not cpu_vs_cpu:
            difficulty2 = difficulty
            cpu_result = handle_cpu_turn(board, difficulty, difficulty2, turn, board_positions,algorithm)
            if cpu_result:
                grid_x, grid_y, captured = cpu_result
                if not captured or not check_additional_capture_moves(board, grid_x, grid_y, turn):
                    turn = PLAYER1

        if check_win(board, PLAYER1):
            game_over = True
            win_message = "Player 1 wins!"
        elif check_win(board, PLAYER2):
            game_over = True
            win_message = "Player 2 wins!"
        elif is_draw(board):
            game_over = True
            win_message = "It's a draw!"

        if game_over:
            end_screen(screen, win_message)
            board_positions = {PLAYER1: {}, PLAYER2: {}}
            current_board_position = None
            board = create_board()
            turn = PLAYER1
            game_over = False

        draw_board(screen, board, mode)
        pygame.display.flip()
        clock.tick(FPS)


# Inicia o jogo e define o tamanho da janela,
# E  aqui é manutorizado o modo de jogo e exibe a tela do menu para selecionar as opções do jogo e iniciar o jogo com base nas opções selecionadas pelo usuário.
if __name__ == "__main__":
    while True:
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Alquerque")

        # Chama o menu de seleção de algoritmo e armazena o resultado na variável selected_algorithm
        selected_algorithm = algorithm_selection_menu(screen)
        
        selected_mode, difficulties = menu_screen(screen, cpu_vs_cpu=False)

        if selected_mode == 2:
            cpu_vs_cpu = False
            selected_difficulty, _ = difficulties
            selected_difficulty2 = None

        elif selected_mode == 3:
            cpu_vs_cpu = True
            selected_difficulty, selected_difficulty2 = difficulties
        else:
            selected_difficulty = 0
            selected_difficulty2 = None
            cpu_vs_cpu = False

        main(selected_mode, selected_difficulty, selected_difficulty2, cpu_vs_cpu, selected_algorithm)

