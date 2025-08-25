// Mapping piece letters to Unicode chess symbols
const pieceSymbols = {
    'P': '♙', 'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔',
    'p': '♟', 'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚'
};

// Event listener for the play button
document.getElementById('play-btn').addEventListener('click', () => {
    const landing = document.getElementById('landing');
    const game = document.getElementById('game');
    
    landing.classList.add('fade-out');
    setTimeout(() => {
        landing.style.display = 'none';
        game.style.display = 'block';
        game.classList.add('fade-in');
        initializeGame();
    }, 500);
});

document.getElementById('back-btn').addEventListener('click', () => {
    const landing = document.getElementById('landing');
    const game = document.getElementById('game');
    
    game.classList.add('fade-out');
    setTimeout(() => {
        game.style.display = 'none';
        landing.style.display = 'flex';
        landing.classList.add('fade-in');
    }, 500);
});

async function initializeGame() {
    try {
        const response = await fetch('http://localhost:5000/init-game', { method: 'GET' });
        const data = await response.json();
        updateBoard(data.board);
        updateStatus(data.status);
    } catch (error) {
        console.error('Failed to initialize game:', error);
    }
}

let selectedSquare = null;

function handleSquareClick(event) {
    const square = event.target.closest('.square');
    const row = parseInt(square.dataset.row);
    const col = parseInt(square.dataset.col);

    if (!selectedSquare) {
        // First click - select piece
        const pieceSpan = square.querySelector('span');
        if (pieceSpan && pieceSpan.textContent.trim()) {
            selectedSquare = { row, col };
            square.classList.add('selected');
        }
    } else {
        // Second click - make move
        const fromRow = selectedSquare.row;
        const fromCol = selectedSquare.col;
        document.querySelector('.selected')?.classList.remove('selected');
        selectedSquare = null;
        makeMove(fromRow, fromCol, row, col);
    }
}

async function makeMove(fromRow, fromCol, toRow, toCol) {
    try {
        const response = await fetch('http://localhost:5000/make-move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ fromRow, fromCol, toRow, toCol })
        });
        const data = await response.json();
        updateBoard(data.board);
        updateStatus(data.status);
    } catch (error) {
        console.error('Error making move:', error);
    }
}

function updateStatus(status) {
    document.getElementById('status').textContent = status;
}

function updateBoard(boardState) {
    const chessboard = document.getElementById('chessboard');
    chessboard.innerHTML = '';
    for (let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            const square = document.createElement('div');
            square.className = `square ${(row + col) % 2 === 0 ? 'white' : 'black'}`;
            square.dataset.row = row;
            square.dataset.col = col;

            const symbol = boardState[row][col];
            if (symbol) {
                const piece = document.createElement('span');
                piece.className = symbol === symbol.toUpperCase() ? 'white-piece' : 'black-piece';
                piece.textContent = pieceSymbols[symbol] || '';
                square.appendChild(piece);
            }

            square.addEventListener('click', handleSquareClick);
            chessboard.appendChild(square);
        }
    }
}

// Initialize the game when the script loads if visible
if (document.getElementById('game').style.display !== 'none') {
    initializeGame();
}
