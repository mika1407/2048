import pygame
import random
import math

# Alustetaan Pygame
pygame.init()

# --- VAKIOT ---
FPS = 60
WIDTH, HEIGHT = 600, 600
ROWS, COLS = 4, 4

RECT_HEIGHT = HEIGHT // ROWS
RECT_WIDTH = WIDTH // COLS 

OUTLINE_COLOR = (187, 173, 160)
OUTLINE_THICKNESS = 10
PADDING = 10 

BACKGROUND_COLOR = (205, 192, 180)
FONT_COLOR = (119, 110, 101)

# Fontit
FONT = pygame.font.SysFont("comicsans", 50, bold=True)
LARGE_FONT = pygame.font.SysFont("comicsans", 80, bold=True)
SUB_FONT = pygame.font.SysFont("comicsans", 30, bold=True)

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048 - Täydellinen Versio")

# --- LUOKAT ---
class Tile:
    COLORS = [
        (237, 229, 218), (238, 225, 201), (243, 178, 122),
        (246, 150, 101), (247, 124, 95), (247, 95, 59),
        (237, 208, 115), (237, 204, 99), (236, 202, 80),
        (237, 197, 63), (237, 194, 46)
    ]

    def __init__(self, value, row, col):
        self.value = value
        self.row = row
        self.col = col
        self.set_pos()

    def get_color(self):
        color_index = int(math.log2(self.value)) - 1
        if color_index < len(self.COLORS):
            return self.COLORS[color_index]
        return (60, 58, 50)

    def draw(self, window):
        color = self.get_color()
        # Piirretään laatta
        pygame.draw.rect(
            window, 
            color, 
            (self.x + PADDING, self.y + PADDING, 
             RECT_WIDTH - PADDING * 2, RECT_HEIGHT - PADDING * 2)
        )

        # Piirretään numero
        text = FONT.render(str(self.value), 1, FONT_COLOR)
        window.blit(
            text,
            (self.x + (RECT_WIDTH / 2 - text.get_width() / 2),
             self.y + (RECT_HEIGHT / 2 - text.get_height() / 2))
        )

    def set_pos(self):
        self.x = self.col * RECT_WIDTH
        self.y = self.row * RECT_HEIGHT

# --- FUNKTIOT ---
def draw_grid(window):
    for col in range(1, COLS):
        x = col * RECT_WIDTH
        pygame.draw.line(window, OUTLINE_COLOR, (x, 0), (x, HEIGHT), OUTLINE_THICKNESS)
    for row in range(1, ROWS):
        y = row * RECT_HEIGHT
        pygame.draw.line(window, OUTLINE_COLOR, (0, y), (WIDTH, y), OUTLINE_THICKNESS)
    pygame.draw.rect(window, OUTLINE_COLOR, (0, 0, WIDTH, HEIGHT), OUTLINE_THICKNESS)

def draw(window, tiles, game_state):
    window.fill(BACKGROUND_COLOR)
    draw_grid(window)
    
    for tile in tiles.values():
        tile.draw(window)

    # Pelin loppunäkymä (Overlay)
    if game_state != "playing":
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 200)) # Läpinäkyvä valkoinen
        window.blit(overlay, (0, 0))
        
        if game_state == "lost":
            msg = "PELI OHI"
            color = (150, 0, 0)
        else:
            msg = "VOITIT!"
            color = (0, 120, 0)
            
        text = LARGE_FONT.render(msg, 1, color)
        sub_text = SUB_FONT.render("Paina R aloittaaksesi alusta", 1, FONT_COLOR)
        
        window.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/2 - text.get_height()/2 - 20))
        window.blit(sub_text, (WIDTH/2 - sub_text.get_width()/2, HEIGHT/2 + 60))

    pygame.display.update()

def get_random_pos(tiles):
    cells = [(r, c) for r in range(ROWS) for c in range(COLS) if f"{r}{c}" not in tiles]
    if not cells:
        return None
    return random.choice(cells)

def check_game_over(tiles):
    if len(tiles) < 16:
        return "playing"
    
    # Tarkistetaan onko mahdollisia siirtoja jäljellä (vaaka ja pysty)
    for r in range(ROWS):
        for c in range(COLS):
            val = tiles[f"{r}{c}"].value
            # Tarkista oikealle ja alas
            for dr, dc in [(0, 1), (1, 0)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < ROWS and 0 <= nc < COLS:
                    if tiles[f"{nr}{nc}"].value == val:
                        return "playing"
    return "lost"

def move_tiles(tiles, direction):
    moved = False
    merged_cells = set()
    
    # Määritetään läpikäyntijärjestys suunnan mukaan
    if direction == "left":
        rows = range(ROWS); cols = range(1, COLS); dr, dc = 0, -1
    elif direction == "right":
        rows = range(ROWS); cols = range(COLS - 2, -1, -1); dr, dc = 0, 1
    elif direction == "up":
        rows = range(1, ROWS); cols = range(COLS); dr, dc = -1, 0
    elif direction == "down":
        rows = range(ROWS - 2, -1, -1); cols = range(COLS); dr, dc = 1, 0

    for r in rows:
        for c in cols:
            tile = tiles.get(f"{r}{c}")
            if not tile: continue
            
            curr_r, curr_c = r, c
            while True:
                next_r, next_c = curr_r + dr, curr_c + dc
                if not (0 <= next_r < ROWS and 0 <= next_c < COLS):
                    break
                
                target = tiles.get(f"{next_r}{next_c}")
                if not target:
                    # Liiku tyhjään ruutuun
                    tiles.pop(f"{curr_r}{curr_c}")
                    tile.row, tile.col = next_r, next_c
                    tiles[f"{next_r}{next_c}"] = tile
                    curr_r, curr_c = next_r, next_c
                    moved = True
                elif target.value == tile.value and f"{next_r}{next_c}" not in merged_cells:
                    # Yhdistä laatat
                    tiles.pop(f"{curr_r}{curr_c}")
                    target.value *= 2
                    merged_cells.add(f"{next_r}{next_c}")
                    moved = True
                    break
                else:
                    break
            tile.set_pos()

    if moved:
        new_pos = get_random_pos(tiles)
        if new_pos:
            tiles[f"{new_pos[0]}{new_pos[1]}"] = Tile(2, new_pos[0], new_pos[1])
    
    # Tarkista voitto (2048)
    for t in tiles.values():
        if t.value == 2048:
            return "won"
            
    return check_game_over(tiles)

def reset_game():
    tiles = {}
    for _ in range(2):
        row, col = get_random_pos(tiles)
        tiles[f"{row}{col}"] = Tile(2, row, col)
    return tiles

# --- PÄÄOHJELMA ---
def main():
    clock = pygame.time.Clock()
    tiles = reset_game()
    game_state = "playing"

    run = True
    while run:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            if event.type == pygame.KEYDOWN:
                # Uudelleenkäynnistys R-näppäimellä
                if event.key == pygame.K_r:
                    tiles = reset_game()
                    game_state = "playing"
                
                # Liikkuminen vain jos peli on käynnissä
                if game_state == "playing":
                    direction = None
                    if event.key == pygame.K_LEFT: direction = "left"
                    elif event.key == pygame.K_RIGHT: direction = "right"
                    elif event.key == pygame.K_UP: direction = "up"
                    elif event.key == pygame.K_DOWN: direction = "down"
                    
                    if direction:
                        game_state = move_tiles(tiles, direction)

        draw(WINDOW, tiles, game_state)

    pygame.quit()

if __name__ == "__main__":
    main()