import pygame
import os
import chess

# ─── Configuration ────────────────────────────────────────────────────────────
MINIMAX_DEPTH = 2    # 2 plies of look-ahead yields a weak ~300–500 Elo
SQUARE_SIZE   = 60
BOARD_SIZE    = 8
WIDTH = HEIGHT = SQUARE_SIZE * BOARD_SIZE
FPS = 30

# Colors
LIGHT      = (222,184,135)
DARK       = (139,69,19)
HIGHLIGHT  = (0,255,0,100)

# ─── Pygame Setup ────────────────────────────────────────────────────────────
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess AI by Simon (minimax)")
clock = pygame.time.Clock()

# ─── Load Piece Images ───────────────────────────────────────────────────────
assets = os.path.join(os.path.dirname(__file__),"assets")
imgs = {}
for p in ['r','n','b','q','k','p']:
    for c in ['w','b']:
        name = c+p
        img = pygame.image.load(os.path.join(assets,f"{name}.png"))
        imgs[name] = pygame.transform.scale(img,(SQUARE_SIZE,SQUARE_SIZE))

# ─── Chess Board State ───────────────────────────────────────────────────────
board = chess.Board()

# ─── Evaluation Function ─────────────────────────────────────────────────────
PIECE_VALUES = {'p': 100, 'n': 320, 'b': 330, 'r': 500, 'q': 900, 'k': 0}
def evaluate_material(bd):
    """Positive = good for White, Negative = good for Black."""
    score = 0
    for sq in chess.SQUARES:
        piece = bd.piece_at(sq)
        if piece:
            val = PIECE_VALUES[piece.symbol().lower()]
            score += val if piece.color==chess.WHITE else -val
    return score

# ─── Minimax with Alpha-Beta ─────────────────────────────────────────────────
def minimax(bd, depth, alpha, beta, maximizing_player):
    if depth == 0 or bd.is_game_over():
        return evaluate_material(bd)
    if maximizing_player:
        max_eval = -99999
        for mv in bd.legal_moves:
            bd.push(mv)
            val = minimax(bd, depth-1, alpha, beta, False)
            bd.pop()
            max_eval = max(max_eval, val)
            alpha = max(alpha, val)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = 99999
        for mv in bd.legal_moves:
            bd.push(mv)
            val = minimax(bd, depth-1, alpha, beta, True)
            bd.pop()
            min_eval = min(min_eval, val)
            beta = min(beta, val)
            if beta <= alpha:
                break
        return min_eval

def find_best_move(bd, depth):
    best_move = None
    best_value = -99999 if bd.turn==chess.WHITE else 99999
    for mv in bd.legal_moves:
        bd.push(mv)
        val = minimax(bd, depth-1, -99999, 99999, bd.turn==chess.BLACK)
        bd.pop()
        if bd.turn==chess.WHITE:
            if val > best_value:
                best_value, best_move = val, mv
        else:
            if val < best_value:
                best_value, best_move = val, mv
    return best_move

# ─── Drawing Helpers ─────────────────────────────────────────────────────────
def draw_board():
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            color = LIGHT if (r+c)%2==0 else DARK
            pygame.draw.rect(screen,color,(c*SQUARE_SIZE,r*SQUARE_SIZE,SQUARE_SIZE,SQUARE_SIZE))

def draw_pieces():
    for sq in chess.SQUARES:
        p = board.piece_at(sq)
        if p:
            col = chess.square_file(sq)
            row = 7 - chess.square_rank(sq)
            key = ('w' if p.color else 'b') + p.symbol().lower()
            screen.blit(imgs[key],(col*SQUARE_SIZE,row*SQUARE_SIZE))

def mouse_to_square(pos):
    x,y = pos
    col = x//SQUARE_SIZE
    row = y//SQUARE_SIZE
    return chess.square(col,7-row), (row,col)

# ─── Main Loop ───────────────────────────────────────────────────────────────
selected = None

running = True
while running:
    draw_board()
    draw_pieces()

    # highlight selection
    if selected:
        _, (r,c) = selected
        s = pygame.Surface((SQUARE_SIZE,SQUARE_SIZE),pygame.SRCALPHA)
        s.fill(HIGHLIGHT)
        screen.blit(s,(c*SQUARE_SIZE,r*SQUARE_SIZE))

    pygame.display.flip()
    clock.tick(FPS)

    for e in pygame.event.get():
        if e.type==pygame.QUIT:
            running=False

        # Human plays White
        elif e.type==pygame.MOUSEBUTTONDOWN and board.turn==chess.WHITE:
            sq, rc = mouse_to_square(e.pos)
            if not selected:
                p = board.piece_at(sq)
                if p and p.color==chess.WHITE:
                    selected = (sq, rc)
            else:
                move = chess.Move(selected[0], sq)
                if move in board.legal_moves:
                    board.push(move)
                selected = None

    # AI plays Black
    if board.turn==chess.BLACK and not board.is_game_over():
        ai_move = find_best_move(board, MINIMAX_DEPTH)
        if ai_move:
            board.push(ai_move)

pygame.quit()
