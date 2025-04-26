import pygame
import random
import sys
from pygame.locals import *

# Constantes
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
GRID_WIDTH = 10
GRID_HEIGHT = 20
BLOCK_SIZE = 30
MARGIN_X = (SCREEN_WIDTH - GRID_WIDTH * BLOCK_SIZE) // 2
MARGIN_Y = SCREEN_HEIGHT - (GRID_HEIGHT * BLOCK_SIZE) - 50

# Couleurs
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Formes des pièces (Tetriminos)
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]]   # Z
]

# Couleurs des pièces
COLORS = [CYAN, YELLOW, MAGENTA, ORANGE, BLUE, GREEN, RED]

class TetrisPiece:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.randint(0, len(SHAPES) - 1)
        self.shape = SHAPES[self.type]
        self.color = COLORS[self.type]
        self.rotation = 0

    def rotate(self):
        self.rotation = (self.rotation + 1) % 4
        self.shape = self._rotate_shape(self.shape, self.rotation)

    def _rotate_shape(self, shape, rotation):
        if rotation == 0:
            return shape
        elif rotation == 1:
            # Rotation 90 degrés
            return [[shape[y][x] for y in range(len(shape)-1, -1, -1)] for x in range(len(shape[0]))]
        elif rotation == 2:
            # Rotation 180 degrés
            return [[shape[y][x] for x in range(len(shape[0])-1, -1, -1)] for y in range(len(shape)-1, -1, -1)]
        elif rotation == 3:
            # Rotation 270 degrés
            return [[shape[y][x] for y in range(len(shape))] for x in range(len(shape[0])-1, -1, -1)]

class TetrisGame:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Tetris')
        
        self.font = pygame.font.SysFont('Arial', 30)
        self.big_font = pygame.font.SysFont('Arial', 50)
        
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self._new_piece()
        self.next_piece = self._new_piece()
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines = 0
        self.fall_speed = 0.5  # secondes entre les chutes
        self.last_move = pygame.time.get_ticks()
        
        self.clock = pygame.time.Clock()

    def _new_piece(self):
        return TetrisPiece(GRID_WIDTH // 2 - 1, 0)

    def _check_collision(self, x, y, shape):
        for i in range(len(shape)):
            for j in range(len(shape[0])):
                if shape[i][j]:
                    if (y + i >= GRID_HEIGHT or 
                        x + j < 0 or 
                        x + j >= GRID_WIDTH or 
                        self.grid[y + i][x + j]):
                        return True
        return False

    def _add_to_grid(self):
        for i in range(len(self.current_piece.shape)):
            for j in range(len(self.current_piece.shape[0])):
                if self.current_piece.shape[i][j]:
                    self.grid[self.current_piece.y + i][self.current_piece.x + j] = self.current_piece.color

    def _clear_lines(self):
        lines_cleared = 0
        for i in range(GRID_HEIGHT):
            if all(self.grid[i]):
                lines_cleared += 1
                # Déplacer toutes les lignes au-dessus vers le bas
                for k in range(i, 1, -1):
                    self.grid[k] = self.grid[k-1][:]
                self.grid[0] = [0 for _ in range(GRID_WIDTH)]
        
        if lines_cleared:
            self.lines += lines_cleared
            self.score += [0, 40, 100, 300, 1200][lines_cleared] * self.level
            self.level = self.lines // 10 + 1
            self.fall_speed = max(0.05, 0.5 - (self.level - 1) * 0.05)

    def _draw_grid(self):
        for i in range(GRID_HEIGHT):
            for j in range(GRID_WIDTH):
                pygame.draw.rect(self.screen, GRAY, 
                               [MARGIN_X + j * BLOCK_SIZE, 
                                MARGIN_Y + i * BLOCK_SIZE, 
                                BLOCK_SIZE, BLOCK_SIZE], 1)
                if self.grid[i][j]:
                    pygame.draw.rect(self.screen, self.grid[i][j], 
                                   [MARGIN_X + j * BLOCK_SIZE + 1, 
                                    MARGIN_Y + i * BLOCK_SIZE + 1, 
                                    BLOCK_SIZE - 2, BLOCK_SIZE - 2])

    def _draw_current_piece(self):
        if self.current_piece:
            for i in range(len(self.current_piece.shape)):
                for j in range(len(self.current_piece.shape[0])):
                    if self.current_piece.shape[i][j]:
                        pygame.draw.rect(self.screen, self.current_piece.color, 
                                       [MARGIN_X + (self.current_piece.x + j) * BLOCK_SIZE + 1, 
                                        MARGIN_Y + (self.current_piece.y + i) * BLOCK_SIZE + 1, 
                                        BLOCK_SIZE - 2, BLOCK_SIZE - 2])

    def _draw_next_piece(self):
        text_next = self.font.render("Next Piece:", True, WHITE)
        self.screen.blit(text_next, (MARGIN_X + GRID_WIDTH * BLOCK_SIZE + 20, MARGIN_Y))
        
        for i in range(len(self.next_piece.shape)):
            for j in range(len(self.next_piece.shape[0])):
                if self.next_piece.shape[i][j]:
                    pygame.draw.rect(self.screen, self.next_piece.color, 
                                   [MARGIN_X + GRID_WIDTH * BLOCK_SIZE + 50 + j * BLOCK_SIZE, 
                                    MARGIN_Y + 50 + i * BLOCK_SIZE, 
                                    BLOCK_SIZE - 2, BLOCK_SIZE - 2])

    def _draw_score(self):
        text_score = self.font.render(f"Score: {self.score}", True, WHITE)
        text_level = self.font.render(f"Level: {self.level}", True, WHITE)
        text_lines = self.font.render(f"Lines: {self.lines}", True, WHITE)
        
        self.screen.blit(text_score, (MARGIN_X + GRID_WIDTH * BLOCK_SIZE + 20, MARGIN_Y + 150))
        self.screen.blit(text_level, (MARGIN_X + GRID_WIDTH * BLOCK_SIZE + 20, MARGIN_Y + 190))
        self.screen.blit(text_lines, (MARGIN_X + GRID_WIDTH * BLOCK_SIZE + 20, MARGIN_Y + 230))

    def _draw_game_over(self):
        if self.game_over:
            text_game_over = self.big_font.render("GAME OVER", True, RED)
            text_rect = text_game_over.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(text_game_over, text_rect)
            
            text_restart = self.font.render("Press R to restart", True, WHITE)
            text_rect = text_restart.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
            self.screen.blit(text_restart, text_rect)

    def draw(self):
        self.screen.fill(BLACK)
        self._draw_grid()
        self._draw_current_piece()
        self._draw_next_piece()
        self._draw_score()
        self._draw_game_over()
        pygame.display.update()

    def fall(self):
        now = pygame.time.get_ticks()
        if now - self.last_move > self.fall_speed * 1000:
            self.last_move = now
            if not self._check_collision(self.current_piece.x, self.current_piece.y + 1, self.current_piece.shape):
                self.current_piece.y += 1
            else:
                self._add_to_grid()
                self._clear_lines()
                self.current_piece = self.next_piece
                self.next_piece = self._new_piece()
                
                if self._check_collision(self.current_piece.x, self.current_piece.y, self.current_piece.shape):
                    self.game_over = True

    def move(self, dx):
        if not self._check_collision(self.current_piece.x + dx, self.current_piece.y, self.current_piece.shape):
            self.current_piece.x += dx

    def rotate_piece(self):
        original_shape = self.current_piece.shape
        original_rotation = self.current_piece.rotation
        
        self.current_piece.rotate()
        
        if self._check_collision(self.current_piece.x, self.current_piece.y, self.current_piece.shape):
            for dx in [-1, 1, -2, 2]:
                if not self._check_collision(self.current_piece.x + dx, self.current_piece.y, self.current_piece.shape):
                    self.current_piece.x += dx
                    return
            
            self.current_piece.shape = original_shape
            self.current_piece.rotation = original_rotation

    def hard_drop(self):
        while not self._check_collision(self.current_piece.x, self.current_piece.y + 1, self.current_piece.shape):
            self.current_piece.y += 1
        self.last_move = pygame.time.get_ticks()

    def reset(self):
        self.__init__()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                
                if not self.game_over:
                    if event.type == KEYDOWN:
                        if event.key == K_LEFT:
                            self.move(-1)
                        elif event.key == K_RIGHT:
                            self.move(1)
                        elif event.key == K_DOWN:
                            self.fall()
                        elif event.key == K_UP:
                            self.rotate_piece()
                        elif event.key == K_SPACE:
                            self.hard_drop()
                else:
                    if event.type == KEYDOWN and event.key == K_r:
                        self.reset()
            
            if not self.game_over:
                self.fall()
            
            self.draw()
            self.clock.tick(60)

if __name__ == "__main__":
    game = TetrisGame()
    game.run() 

    