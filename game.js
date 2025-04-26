// --- DOM Elements ---
const canvas = document.getElementById('tetrisCanvas');
const context = canvas.getContext('2d');

// --- Constants ---
const GRID_WIDTH = 10;
const GRID_HEIGHT = 20;
const BLOCK_SIZE = 30;

// Calculate canvas size based on grid
canvas.width = GRID_WIDTH * BLOCK_SIZE;
canvas.height = GRID_HEIGHT * BLOCK_SIZE;

// Scale context for block size
context.scale(BLOCK_SIZE, BLOCK_SIZE);

const COLORS = [
    null, // 0 represents empty cell
    'cyan',    // I
    'yellow',  // O
    'purple',  // T
    'orange',  // L
    'blue',    // J
    'lime',    // S  (Green wasn't contrasting enough)
    'red'      // Z
];

const SHAPES = [
    [], // Placeholder for null color
    [[1, 1, 1, 1]],             // I
    [[1, 1], [1, 1]],           // O
    [[0, 1, 0], [1, 1, 1]],     // T (Adjusted for standard Tetris rotation)
    [[0, 0, 1], [1, 1, 1]],     // L (Adjusted)
    [[1, 0, 0], [1, 1, 1]],     // J (Adjusted)
    [[0, 1, 1], [1, 1, 0]],     // S
    [[1, 1, 0], [0, 1, 1]]      // Z
];

// --- Game State ---
let grid = createGrid(GRID_WIDTH, GRID_HEIGHT);
let currentPiece = createPiece();
let score = 0;
let lines = 0;
let level = 1; // We can implement level later
let gameOver = false;

// --- Game Loop Variables ---
let lastTime = 0;
let dropCounter = 0;
let dropInterval = 1000; // ms (1 second initially)

// --- Functions ---

function createGrid(width, height) {
    const matrix = [];
    while (height--) {
        matrix.push(new Array(width).fill(0));
    }
    return matrix;
}

function createPiece() {
    const typeId = Math.floor(Math.random() * (SHAPES.length - 1)) + 1;
    const shape = SHAPES[typeId];
    return {
        x: Math.floor(GRID_WIDTH / 2) - Math.floor(shape[0].length / 2),
        y: 0,
        shape: shape,
        colorIndex: typeId
    };
}

function drawMatrix(matrix, offsetX, offsetY) {
    matrix.forEach((row, y) => {
        row.forEach((value, x) => {
            if (value !== 0) {
                context.fillStyle = COLORS[value];
                context.fillRect(x + offsetX, y + offsetY, 1, 1);
                 // Add a subtle border to blocks
                context.strokeStyle = 'black';
                context.lineWidth = 0.05;
                context.strokeRect(x + offsetX, y + offsetY, 1, 1);
            }
        });
    });
}

function draw() {
    // Clear canvas (scaled coordinates)
    context.fillStyle = '#34495e'; // Match CSS background
    context.fillRect(0, 0, canvas.width / BLOCK_SIZE, canvas.height / BLOCK_SIZE);

    // Draw the fixed blocks on the grid
    drawMatrix(grid, 0, 0);

    // Draw the currently falling piece
    drawMatrix(currentPiece.shape, currentPiece.x, currentPiece.y);

    // TODO: Draw score, next piece, game over screen
}

function mergePieceToGrid() {
    currentPiece.shape.forEach((row, y) => {
        row.forEach((value, x) => {
            if (value !== 0) {
                grid[y + currentPiece.y][x + currentPiece.x] = currentPiece.colorIndex;
            }
        });
    });
}

function checkCollision(piece, grid) {
    for (let y = 0; y < piece.shape.length; ++y) {
        for (let x = 0; x < piece.shape[y].length; ++x) {
            if (piece.shape[y][x] !== 0) { // Check only filled cells of the piece
                const gridY = y + piece.y;
                const gridX = x + piece.x;

                // Check boundaries
                if (gridX < 0 || gridX >= GRID_WIDTH || gridY >= GRID_HEIGHT) {
                    return true; // Collision with walls or floor
                }
                // Check collision with existing blocks on the grid
                // Important: gridY must be >= 0 because piece starts at y=0
                if (gridY >= 0 && grid[gridY] && grid[gridY][gridX] !== 0) {
                    return true;
                }
            }
        }
    }
    return false;
}

function pieceDrop() {
    currentPiece.y++;
    if (checkCollision(currentPiece, grid)) {
        currentPiece.y--; // Revert move
        mergePieceToGrid();
        clearLines();
        currentPiece = createPiece(); // Get new piece
        // Check for game over immediately after new piece spawns
        if (checkCollision(currentPiece, grid)) {
            gameOver = true;
            console.log("GAME OVER!");
            // TODO: Show game over message
        }
    }
    dropCounter = 0; // Reset drop counter after manual or automatic drop
}

function pieceMove(direction) {
    currentPiece.x += direction;
    if (checkCollision(currentPiece, grid)) {
        currentPiece.x -= direction; // Revert if collision
    }
}

function rotateMatrix(matrix) {
    // Transpose + Reverse rows = 90 degree clockwise rotation
    const rows = matrix.length;
    const cols = matrix[0].length;
    const rotated = [];

    for (let j = 0; j < cols; j++) {
        rotated[j] = new Array(rows);
    }

    for (let i = 0; i < rows; i++) {
        for (let j = 0; j < cols; j++) {
            rotated[j][i] = matrix[i][j];
        }
    }

    rotated.forEach(row => row.reverse());
    return rotated;
}

function pieceRotate() {
    const originalShape = currentPiece.shape;
    const rotatedShape = rotateMatrix(currentPiece.shape);
    const originalX = currentPiece.x;
    let offset = 1;

    currentPiece.shape = rotatedShape;

    // Wall kick logic (simple version)
    while (checkCollision(currentPiece, grid)) {
        currentPiece.x += offset;
        offset = -(offset + (offset > 0 ? 1 : -1)); // Try -1, then 2, then -2 etc.
        if (offset > currentPiece.shape[0].length) { // If offset is too large, rotation failed
            currentPiece.shape = originalShape; // Revert shape
            currentPiece.x = originalX; // Revert position
            return; // Exit rotation attempt
        }
    }
}

function clearLines() {
    let linesClearedThisTurn = 0;
    outer: for (let y = GRID_HEIGHT - 1; y >= 0; --y) {
        for (let x = 0; x < GRID_WIDTH; ++x) {
            if (grid[y][x] === 0) {
                continue outer; // Row not full, check next row up
            }
        }

        // If we reach here, the row is full
        const removedRow = grid.splice(y, 1)[0].fill(0);
        grid.unshift(removedRow); // Add empty row at the top
        linesClearedThisTurn++;
        y++; // Re-check the current row index as rows shifted down
    }

    if (linesClearedThisTurn > 0) {
        lines += linesClearedThisTurn;
        // Basic scoring - adjust as needed
        score += [0, 40, 100, 300, 1200][linesClearedThisTurn];
        console.log(`Score: ${score}, Lines: ${lines}`);
        // TODO: Update score display on screen
        // TODO: Implement level increase and speed up
    }
}


// --- Game Loop ---
function gameLoop(time = 0) {
    if (gameOver) {
        // TODO: Display Game Over message persistently
        return;
    }

    const deltaTime = time - lastTime;
    lastTime = time;

    dropCounter += deltaTime;
    if (dropCounter > dropInterval) {
        pieceDrop();
    }

    draw();
    requestAnimationFrame(gameLoop);
}

// --- Event Listeners ---
document.addEventListener('keydown', event => {
    if (gameOver) return;

    switch (event.key) {
        case 'ArrowLeft':
        case 'a': // Add WASD alternative
            pieceMove(-1);
            break;
        case 'ArrowRight':
        case 'd':
            pieceMove(1);
            break;
        case 'ArrowDown':
        case 's':
            pieceDrop();
            break;
        case 'ArrowUp':
        case 'w':
            pieceRotate();
            break;
        case ' ':
             // TODO: Implement hard drop
            console.log("Hard drop (not implemented yet)");
            break;
    }
});

// --- Start Game ---
console.log("Starting Tetris...");
currentPiece = createPiece(); // Initialize first piece
gameLoop(); 