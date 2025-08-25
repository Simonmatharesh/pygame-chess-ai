from flask import Flask, jsonify, request
from flask_cors import CORS
import chess
from main import find_best_move  # Import the AI function that uses its internal depth

app = Flask(__name__)
CORS(app)

# Global chess board instance
board = chess.Board()

def get_board_state():
    """Convert chess.Board to 2D array representation"""
    state = [['' for _ in range(8)] for _ in range(8)]
    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if piece:
            col = chess.square_file(sq)
            row = 7 - chess.square_rank(sq)
            symbol = piece.symbol().upper() if piece.color else piece.symbol().lower()
            state[row][col] = symbol
    return state

@app.route('/init-game', methods=['GET'])
def init_game():
    global board
    board = chess.Board()
    return jsonify({
        'valid': True,
        'board': get_board_state(),
        'status': "White's turn"
    })

@app.route('/make-move', methods=['POST'])
def make_move():
    global board
    data = request.json
    print("Received move data:", data)
    try:
        # Check if we have all required move data
        if any(v is None for v in [data.get('fromRow'), data.get('fromCol'), 
                                 data.get('toRow'), data.get('toCol')]):
            return jsonify({
                'valid': False,
                'board': get_board_state(),
                'status': "Invalid move data",
                'error': 'Incomplete move data'
            })

        from_row = 7 - int(data['fromRow'])
        from_col = int(data['fromCol'])
        to_row = 7 - int(data['toRow'])
        to_col = int(data['toCol'])

        from_sq = chess.square(from_col, from_row)
        to_sq = chess.square(to_col, to_row)
        move = chess.Move(from_sq, to_sq)

        if move in board.legal_moves:
            board.push(move)
            # AI move
            ai_move = find_best_move(board)
            if ai_move:
                board.push(ai_move)
            status = "White's turn" if board.turn else "Black's turn"
            return jsonify({
                'valid': True,
                'board': get_board_state(),
                'status': status
            })
        else:
            # Invalid move
            status = "White's turn" if board.turn else "Black's turn"
            return jsonify({
                'valid': False,
                'board': get_board_state(),
                'status': status,
                'error': 'Illegal move'
            })
    except Exception as e:
        print("Error in /make-move:", e)
        # Return failure but include board state
        return jsonify({
            'valid': False,
            'board': get_board_state(),
            'status': "Error",
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
