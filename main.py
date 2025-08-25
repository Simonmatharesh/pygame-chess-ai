import pygame
import os
import chess
import random

# ─── Configuration ────────────────────────────────────────────────────────────
MINIMAX_DEPTH = 2
SQUARE_SIZE   = 60
BOARD_SIZE    = 8
WIDTH = HEIGHT = SQUARE_SIZE * BOARD_SIZE
FPS = 30

LIGHT      = (222, 184, 135)
DARK       = (139, 69, 19)

# ─── Load Piece Images ───────────────────────────────────────────────────────
assets = os.path.join(os.path.dirname(__file__), "assets")
imgs = {}
for p in ['r', 'n', 'b', 'q', 'k', 'p']:
    for c in ['w', 'b']:
        name = c + p
        img = pygame.image.load(os.path.join(assets, f"{name}.png"))
        imgs[name] = pygame.transform.scale(img, (SQUARE_SIZE, SQUARE_SIZE))

# ─── Evaluation Function ─────────────────────────────────────────────────────
PIECE_VALUES = {'p': 100, 'n': 320, 'b': 330, 'r': 500, 'q': 900, 'k': 0}
def evaluate_material(bd):
    score = 0
    for sq in chess.SQUARES:
        piece = bd.piece_at(sq)
        if piece:
            value = PIECE_VALUES[piece.symbol().lower()]
            score += value if piece.color else -value
    return score

# ─── Minimax Algorithm ───────────────────────────────────────────────────────
def minimax(bd, depth, maximizing):
    if depth == 0 or bd.is_game_over():
        return evaluate_material(bd), None

    best_move = None
    if maximizing:
        max_eval = float('-inf')
        for move in bd.legal_moves:
            bd.push(move)
            eval, _ = minimax(bd, depth-1, False)
            bd.pop()
            if eval > max_eval:
                max_eval = eval
                best_move = move
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in bd.legal_moves:
            bd.push(move)
            eval, _ = minimax(bd, depth-1, True)
            bd.pop()
            if eval < min_eval:
                min_eval = eval
                best_move = move
        return min_eval, best_move

def find_best_move(bd):
    _, move = minimax(bd, MINIMAX_DEPTH, bd.turn)
    return move

# ─── Pygame Chess GUI ────────────────────────────────────────────────────────
def draw_board(scr, bd):
    colors = [LIGHT, DARK]
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            color = colors[(r + c) % 2]
            pygame.draw.rect(scr, color, pygame.Rect(c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    for sq in chess.SQUARES:
        piece = bd.piece_at(sq)
        if piece:
            col = chess.square_file(sq)
            row = 7 - chess.square_rank(sq)
            key = ('w' if piece.color else 'b') + piece.symbol().lower()
            scr.blit(imgs[key], pygame.Rect(col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess AI by Simon")
    clock = pygame.time.Clock()

    bd = chess.Board()
    selected_sq = None
    running = True

    while running:
        draw_board(screen, bd)
        pygame.display.flip()

        if not bd.is_game_over() and not bd.turn:
            move = find_best_move(bd)
            if move:
                bd.push(move)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                col = x // SQUARE_SIZE
                row = 7 - (y // SQUARE_SIZE)
                sq = chess.square(col, row)

                if selected_sq is None:
                    if bd.piece_at(sq) and bd.piece_at(sq).color == bd.turn:
                        selected_sq = sq
                else:
                    move = chess.Move(selected_sq, sq)
                    if move in bd.legal_moves:
                        bd.push(move)
                    selected_sq = None

        clock.tick(FPS)

    pygame.quit()

# ─── Run GUI only if directly executed ───────────────────────────────────────
if __name__ == "__main__":
    main()
