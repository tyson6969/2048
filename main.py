import pygame
import random
import math
import time

pygame.init()

FPS = 60

WIDTH, HEIGHT = 800, 800
ROWS = 4
COLS = 4


RECT_HEIGHT = HEIGHT // ROWS
RECT_WIDTH = WIDTH // COLS

OUTLINE_COLOR = (187,173,160 )

OUTLINE_THICKNESS = 10
BACKGROUND_COLOR = (205,192,180)
FONT_COLOR = (119,110,101)


FONT = pygame.font.SysFont("comic  sans", 60 , bold = True)
MOVE_VEL = 20



WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("upgraded 2048")

TITLE_FONT = pygame.font.SysFont("comic  sans", 100 , bold = True)
MENU_FONT =  pygame.font.SysFont("comic  sans", 42 , bold = True)
SMALL_FONT = pygame.font.SysFont("comic  sans", 28 , bold = True)



score = 0
moves = 0
merges = 0
highest_tile =2
start_time = 0.0
high_score =0 


pygame.mixer.init()
merge_sound = pygame.mixer.Sound("Deep Meow Sound Effect (UPDATED).wav")



class Tile:

    COLORS = [
        (237, 229 ,218),
        (238, 225 ,201),
        (243, 178, 122),
        (246, 150, 101),
        (247, 124, 95 ),
        (247, 95, 59),
        (237, 208 , 115),
        (237, 204 , 99),
        (236, 202, 80),

    ]

    def __init__ (self, value , row ,col):
        self.value = value
        self.row = row
        self.col = col
        self.x = col* RECT_WIDTH
        self.y = row * RECT_HEIGHT
        self.just_merged = False

    def get_color(self):
        color_index = int(math.log2(self.value)) -1
        color = self.COLORS[color_index]
        return color
        
    
    def draw(self, window):
        color = self.get_color()
        pygame.draw.rect(window , color , (self.x , self.y, RECT_WIDTH, RECT_HEIGHT))
        
        text = FONT.render(str(self.value),1 , FONT_COLOR)
        window.blit(text, (self.x + (RECT_WIDTH /2 - text.get_width()/ 2), self.y + (RECT_HEIGHT /2 - text.get_height() / 2 )) )

        if self.just_merged:
            flash = pygame.Surface((RECT_WIDTH, RECT_HEIGHT), pygame.SRCALPHA)
            flash.fill((255, 255, 255, 100))
            window.blit(flash, (self.x, self.y))
            self.just_merged = False

    def set_pos(self, ceil = False):
        if ceil: 
            self.row = math.ceil(self.y /RECT_HEIGHT)
            self.col = math.ceil(self.x / RECT_WIDTH)  

        else:
            self.row = math.floor(self.y / RECT_HEIGHT)
            self.col = math.floor(self.x / RECT_WIDTH)
        

    def move (self, delta):
        self.x += delta[0]
        self.y += delta[1]



def drawgrid(window):
    for row in range(1, ROWS):
        y = row * RECT_HEIGHT
        pygame.draw.line(window, OUTLINE_COLOR, (0, y), (WIDTH, y), OUTLINE_THICKNESS)

    for col in range(1, COLS):
      x =  col * RECT_WIDTH
      pygame.draw.line(window, OUTLINE_COLOR, (x, 0), (x, HEIGHT), OUTLINE_THICKNESS)
    

    pygame.draw.rect(window, OUTLINE_COLOR, (0,0, WIDTH, HEIGHT), OUTLINE_THICKNESS)


def draw(window, tiles):
    window.fill(BACKGROUND_COLOR)


    for tile in tiles.values():
     tile.draw(window)

    drawgrid(window)

    pygame.display.update()

def get_random_pos(tiles):
    while True:
        row= random.randrange(0, ROWS)
        col = random.randrange(0, COLS)

        if f"{row},{col}" not in tiles :
            break

    return  row , col

def snap(tiles):
    for tile in tiles.values():
        tile.x = tile.col * RECT_WIDTH
        tile.y = tile.row * RECT_HEIGHT


def move_tiles(window, tiles, clock, direction):

    global score, moves, merges, highest_tile, high_score

    updated = True
    blocks = set()
    did_move = False


    if direction == "left":
        sort_func = lambda x: x.col
        reverse = False 
        delta = (-MOVE_VEL, 0)
        boundary_check = lambda tile: tile.col == 0
        get_next_tile = lambda tile: tiles.get(f"{tile.row},{tile.col - 1}")
        merge_check = lambda tile, next_tile: tile.x > next_tile.x + MOVE_VEL
        move_check = (lambda tile, next_tile: tile.x > next_tile.x + RECT_WIDTH + MOVE_VEL)
        ceil = True

    elif direction == "right":
        sort_func = lambda x: x.col
        reverse = True 
        delta = (MOVE_VEL, 0)
        boundary_check = lambda tile: tile.col == COLS - 1
        get_next_tile = lambda tile: tiles.get(f"{tile.row},{tile.col + 1}")
        merge_check = lambda tile, next_tile: tile.x < next_tile.x - MOVE_VEL
        move_check = (lambda tile, next_tile: tile.x + RECT_WIDTH + MOVE_VEL < next_tile.x )
        ceil = False

    elif direction == "up":
        sort_func = lambda x: x.row
        reverse = False 
        delta = (0, -MOVE_VEL)
        boundary_check = lambda tile: tile.row == 0
        get_next_tile = lambda tile: tiles.get(f"{tile.row -1 },{tile.col }")
        merge_check = lambda tile, next_tile: tile.y > next_tile.y + MOVE_VEL
        move_check = (lambda tile, next_tile: tile.y > next_tile.y + RECT_HEIGHT + MOVE_VEL)
        ceil = True

    elif direction == "down":
        sort_func = lambda x: x.row
        reverse = True
        delta = (0, MOVE_VEL)
        boundary_check = lambda tile: tile.row == ROWS - 1
        get_next_tile = lambda tile: tiles.get(f"{tile.row +1 },{tile.col }")
        merge_check = lambda tile, next_tile: tile.y < next_tile.y - MOVE_VEL
        move_check = (lambda tile, next_tile: tile.y + RECT_HEIGHT + MOVE_VEL< next_tile.y )
        ceil = False


    while updated:
        clock.tick(FPS)
        updated = False
        sorted_tiles = sorted(tiles.values(), key=sort_func, reverse=reverse)

        for i, tile in enumerate(sorted_tiles):
            if boundary_check(tile):
                continue

            next_tile = get_next_tile(tile)
            if not next_tile:
                tile.move(delta)
            elif tile.value == next_tile.value and tile not in blocks and next_tile not in blocks:
                if merge_check (tile, next_tile):
                    tile.move(delta)
                else:
                    next_tile.value *= 2
                    sorted_tiles.pop(i)
                    blocks.add(next_tile)
                    did_move = True
                    score += next_tile.value
                    merges += 1
                    if next_tile.value > highest_tile:
                        highest_tile = next_tile.value
                    if score > high_score:
                        high_score = score

                    next_tile.just_merged = True
                    if merge_sound:
                        merge_sound.play()

            elif move_check(tile, next_tile):
                tile.move(delta)
            else:
                continue

            tile.set_pos(ceil)
            updated = True


        update_tiles(window, tiles, sorted_tiles)


    snap(tiles)
    draw(window, tiles)

    if did_move:
        moves +=1


    return end_tiles(tiles)


def end_tiles(tiles):
    if len(tiles) == ROWS * COLS:
        return"lost"
    
    row, col = get_random_pos(tiles)  
    tiles[f"{row},{col}"] = Tile(random.choice([2,4]), row, col)
    return "contuine"



def update_tiles(window, tiles, sorted_tiles):
    tiles.clear()
    for tile in sorted_tiles:
         tiles[f"{tile.row},{tile.col}"] = tile

    draw(window, tiles)
    


def generate_tiles():
    tiles = {}
    for _ in range (2):
        row, col = get_random_pos(tiles)
        tiles[f"{row},{col}"] = Tile(2, row , col)

    return tiles  


def draw_button(window, text, cx, cy, w, h, color, text_color = (255,255,255)):
    rect = pygame.Rect(cx - w // 2, cy- h// 2, w, h)
    pygame.draw.rect(window,color,rect , border_radius=12)
    label = MENU_FONT.render(text, True, text_color)
    window.blit(label, (rect.centerx - label.get_width() // 2, rect.centery - label.get_height() // 2))

    return rect 


def lose_screen(window, clock):
    elapsed = time.time() - start_time
    mins = int(elapsed // 60)
    secs = int(elapsed % 60)
    time_text = f"{mins:02d}:{secs:02d}"

    btn_color = (119,110,101)
    red_color = (195, 80, 84)

    while True:
        window.fill(BACKGROUND_COLOR)
        title = TITLE_FONT.render("game over", True, FONT_COLOR)
        window.blit(title, (WIDTH // 2 - title.get_width() // 2, 55))

        stats = [
            f"score         {score}",
            f"best score    {high_score}",
            f"highest tile  {highest_tile}",
            f"moves made    {moves}",
            f"merges        {merges}",
            f"time          {time_text}",
        ]

        for i, line in enumerate(stats ):
            surf = SMALL_FONT.render(line, True, FONT_COLOR)
            window.blit(surf, (WIDTH // 2 - surf.get_width() // 2, 200 + i * 50) )

        menu_btn = draw_button(window, "main menu",WIDTH // 2, 610, 280, 62, btn_color )
        quit_btn = draw_button(window, "quit",      WIDTH // 2, 690, 280, 62, red_color)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if menu_btn.collidepoint(event.pos):
                    return "menu"
                if quit_btn.collidepoint(event.pos):
                    return "quit"

def wildcard_screen(window, clock):

    grid_size = 4
    MIN_SIZE = 3
    MAX_SIZE = 8

    arrow_color = (143,122,102)
    btn_color=(119,110,101)

    while True:
        window.fill(BACKGROUND_COLOR)
        tittle = MENU_FONT.render("pick your grid size",True, FONT_COLOR)
        window.blit(tittle ,(WIDTH // 2 - tittle.get_width()// 2,60 ))

        size_text = TITLE_FONT.render(F'{grid_size}x {grid_size}', True, FONT_COLOR)
        window.blit(size_text, (WIDTH // 2 - size_text.get_width()// 2, 160))

        hint = SMALL_FONT.render(f"(min {MIN_SIZE}  —  max {MAX_SIZE})", True, FONT_COLOR)
        window.blit(hint, (WIDTH // 2 - hint.get_width()// 2, 300))

        left_btn = draw_button(window,"<",          160,    300,110,70, arrow_color)
        right_btn = draw_button(window, " >",       640,    300,110,70, arrow_color)
        go_btn = draw_button(window, "Start game", WIDTH //2 , 490, 260, 70, (199,144, 90))
        back_btn = draw_button(window, "Go back", WIDTH //2, 590, 180 , 55, btn_color)

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if left_btn.collidepoint(event.pos):
                    grid_size = max(MIN_SIZE, grid_size -1 )
                elif right_btn.collidepoint(event.pos):
                    grid_size = min(MAX_SIZE, grid_size +1 )
                elif go_btn.collidepoint(event.pos):
                    return grid_size
                elif back_btn.collidepoint(event.pos):
                    return None


def start_screen(window, clock):
    gamemodes = [
        ("easy   —  4 x 4",  4),
        ("normal — 5 x 5",   5),
        ("hard   —  6 x 6",  6),
    ]

    btn_colors = [
        (119, 175, 120),  
        (220, 160,  60),   
        (195,  80,  80),   
    ]

    wildcard_color = (100,130, 195)
    btn_w , btn_h = 360, 65
    start_y = 280

    while True:
        window.fill(BACKGROUND_COLOR)

        title = TITLE_FONT.render("2048", True, FONT_COLOR)
        window.blit(title, (WIDTH //2 - title.get_width() // 2,0))

        sub = SMALL_FONT.render("choose a difficuly", True, FONT_COLOR)
        window.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 180))


        
        rects = []

        for i, (label, _ ) in enumerate(gamemodes):
            cy = start_y + i * (btn_h + 18 )
            rect = draw_button(window, label, WIDTH // 2, cy, btn_w, btn_h , btn_colors[i])
            rects.append(rect)


        wild_rect = draw_button(window, "wild card", WIDTH //2, start_y + 3 * (btn_h + 18 )+ 20, btn_w, btn_h, wildcard_color)




        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None

            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, rect in enumerate(rects):
                    if rect.collidepoint(event.pos):
                        return gamemodes[i][1]

                if wild_rect.collidepoint(event.pos):
                    chosen = wildcard_screen(window, clock)
                    if chosen is not None:
                        return chosen
                


            
        clock.tick(FPS)



def main(window):

    global ROWS, COLS, RECT_HEIGHT, RECT_WIDTH, FONT
    global score, moves, merges, highest_tile, start_time

    clock = pygame.time.Clock()

    while True:

        score = 0
        moves = 0
        merges = 0
        highest_tile = 2 

        grid_size = start_screen(window, clock)
        if grid_size is None:
            return
        

        ROWS = grid_size
        COLS = grid_size
        RECT_HEIGHT = HEIGHT // ROWS
        RECT_WIDTH= WIDTH // COLS 
        
        font_size = max(28, 60 - (grid_size - 4 )* 10)
        FONT = pygame.font.SysFont("comic sans", font_size, bold = True)
        start_time = time.time()
        
        



        

        tiles = generate_tiles()
        run = True
        while run:
            clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    break

                if event.type == pygame.KEYDOWN :
                    result = None
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a: 
                        move_tiles(window,tiles,clock, "left")

                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:  
                        move_tiles(window,tiles,clock, "right")

                    elif event.key == pygame.K_UP or event.key == pygame.K_w:  
                        move_tiles(window,tiles,clock, "up")

                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s: 
                        move_tiles(window,tiles,clock, "down")

                    elif result == "lost":
                        action = lose_screen(window, clock)
                        if action == "menu":
                         run = False
                        else:
                            return
                    
            draw(window, tiles)
    
    


if __name__ == "__main__":
    main(WINDOW)