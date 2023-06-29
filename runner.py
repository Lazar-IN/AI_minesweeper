#pre prvog pokretanja instalirati pygame sa komandom: pip install pygame
import pygame
import sys
import time
from minesweeper import Minesweeper, MinesweeperAI

#Dimenzije table i br mina
HEIGHT = 9
WIDTH = 9
MINES = 10
# Boje
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
WHITE = (255, 255, 255)
PINK = (147, 255, 135)
RED = (255, 0, 0)
#Naziv prozora, dimenzija prozora i inicjalizacija velicine prozora
pygame.display.set_caption('MINOLOVAC')
pygame.init()
size = width, height = 1000, 700
screen = pygame.display.set_mode(size)
#fontovi
OPEN_SANS = "assets/fonts/OpenSans-Regular.ttf"
smallFont = pygame.font.Font(OPEN_SANS, 20)
mediumFont = pygame.font.Font(OPEN_SANS, 28)
largeFont = pygame.font.Font(OPEN_SANS, 40)
#dimenzije table
BOARD_PADDING = 20
board_width = ((2 / 3) * width) - (BOARD_PADDING * 2)
board_height = height - (BOARD_PADDING * 2)
cell_size = int(min(board_width / WIDTH, board_height / HEIGHT))
board_origin = (BOARD_PADDING, BOARD_PADDING)
flag = pygame.image.load("assets/images/flag.png")
flag = pygame.transform.scale(flag, (cell_size, cell_size))
mine = pygame.image.load("assets/images/mine.png")
mine = pygame.transform.scale(mine, (cell_size, cell_size))
mine_red = pygame.image.load("assets/images/mine-red.png")
mine_red = pygame.transform.scale(mine_red, (cell_size, cell_size))


#inicijalizacija same igre i ai 
mine_detonated = None
game = Minesweeper(height=HEIGHT, width=WIDTH, mines=MINES)
ai = MinesweeperAI(height=HEIGHT, width=WIDTH)
#broj otkrivenih polja,broj oznacenih polja i bool vrednost za pobedu/poraz
revealed = set()
flags = set()
lost = False
instructions = True
#autoplay brzina i inicijalna stanja pri otvaranju igre
autoplay = False
autoplaySpeed = 0.3
makeAiMove = False
showInference = False

while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
    screen.fill(BLACK)

    if instructions:
        #pocetni prozor(prikaz pravila)
        title = largeFont.render("MINOLOVAC", True, WHITE)
        titleRect = title.get_rect()
        titleRect.center = ((width / 2), 50)
        screen.blit(title, titleRect)

        rules = [
            "Levim klikom otvorite polje.",
            "Desnim klikom oznacite polje kao minu.",
            "Oznacite sva polja kako biste pobedili!"
        ]
        for i, rule in enumerate(rules):
            line = smallFont.render(rule, True, WHITE)
            lineRect = line.get_rect()
            lineRect.center = ((width / 2), 150 + 30 * i)
            screen.blit(line, lineRect)

        #pokreni igru dugme(sa neta)
        buttonRect = pygame.Rect((width / 4), (3 / 4) * height, width / 2, 50)
        buttonText = mediumFont.render("Pokreni igru!", True, BLACK)
        buttonTextRect = buttonText.get_rect()
        buttonTextRect.center = buttonRect.center
        pygame.draw.rect(screen, PINK, buttonRect)
        screen.blit(buttonText, buttonTextRect)
        click, _, _ = pygame.mouse.get_pressed()
        if click == 1:
            mouse = pygame.mouse.get_pos()
            if buttonRect.collidepoint(mouse):
                instructions = False
                time.sleep(0.3)

        pygame.display.flip()
        continue

    #iscrtavanje table
    cells = []
    for i in range(HEIGHT):
        row = []
        for j in range(WIDTH):

            rect = pygame.Rect(
                board_origin[0] + j * cell_size,
                board_origin[1] + i * cell_size,
                cell_size, cell_size
            )
            pygame.draw.rect(screen, GRAY, rect)
            pygame.draw.rect(screen, WHITE, rect, 3)
            #dodavanje mina
            if game.is_mine((i, j)) and lost:
                if (i,j) == mine_detonated:
                    screen.blit(mine_red, rect)
                else:
                    screen.blit(mine, rect)
            elif (i, j) in flags:
                screen.blit(flag, rect)
            elif (i, j) in revealed:
                neighbors = smallFont.render(
                    str(game.nearby_mines((i, j))),
                    True, BLACK
                )
                neighborsTextRect = neighbors.get_rect()
                neighborsTextRect.center = rect.center
                screen.blit(neighbors, neighborsTextRect)
            elif (i, j) in ai.safes and showInference:
                pygame.draw.rect(screen, PINK, rect)
                pygame.draw.rect(screen, WHITE, rect, 3)
            elif (i, j) in ai.mines and showInference:
                pygame.draw.rect(screen, RED, rect)
                pygame.draw.rect(screen, WHITE, rect, 3)
            row.append(rect)
        cells.append(row)

    # Autoplay dugme
    autoplayBtn = pygame.Rect(
        (2 / 3) * width + BOARD_PADDING, BOARD_PADDING,
        (width / 3) - BOARD_PADDING * 2, 50
    )
    bText = "Autoplay" if not autoplay else "Stop"
    buttonText = mediumFont.render(bText, True, BLACK)
    buttonRect = buttonText.get_rect()
    buttonRect.center = autoplayBtn.center
    pygame.draw.rect(screen, PINK, autoplayBtn)
    screen.blit(buttonText, buttonRect)

    # AI potez dugme
    aiButton = pygame.Rect(
        (2 / 3) * width + BOARD_PADDING, BOARD_PADDING + 70,
        (width / 3) - BOARD_PADDING * 2, 50
    )
    buttonText = mediumFont.render("AI potez", True, BLACK)
    buttonRect = buttonText.get_rect()
    buttonRect.center = aiButton.center
    if not autoplay:
        pygame.draw.rect(screen, WHITE, aiButton)
        screen.blit(buttonText, buttonRect)

    # dugme za restart
    resetButton = pygame.Rect(
        (2 / 3) * width + BOARD_PADDING, BOARD_PADDING + 140,
        (width / 3) - BOARD_PADDING * 2, 50
    )
    buttonText = mediumFont.render("Restart", True, BLACK)
    buttonRect = buttonText.get_rect()
    buttonRect.center = resetButton.center
    if not autoplay:
        pygame.draw.rect(screen, WHITE, resetButton)
        screen.blit(buttonText, buttonRect)

    # krajnja poruka
    text = "Izgubio si!" if lost else "Pobedio si!" if game.mines == flags else ""
    text = mediumFont.render(text, True, WHITE)
    textRect = text.get_rect()
    textRect.center = ((5 / 6) * width, BOARD_PADDING + 232)
    screen.blit(text, textRect)

    # krajnji prikaz svih polja
    safesMinesButton = pygame.Rect(
        (2 / 3) * width + BOARD_PADDING, BOARD_PADDING + 280,
        (width / 3) - BOARD_PADDING * 2, 50
    )
    bText = "Prikazi predikciju" if not showInference else "Sakrij predikciju"
    buttonText = smallFont.render(bText, True, BLACK)
    buttonRect = buttonText.get_rect()
    buttonRect.center = safesMinesButton.center
    if not autoplay:
        pygame.draw.rect(screen, WHITE, safesMinesButton)
        screen.blit(buttonText, buttonRect)

    move = None

    left, _, right = pygame.mouse.get_pressed()

    if right == 1 and not lost and not autoplay:
        mouse = pygame.mouse.get_pos()
        for i in range(HEIGHT):
            for j in range(WIDTH):
                if cells[i][j].collidepoint(mouse) and (i, j) not in revealed:
                    if (i, j) in flags:
                        flags.remove((i, j))
                    else:
                        flags.add((i, j))
                    time.sleep(0.2)

    elif left == 1:
        mouse = pygame.mouse.get_pos()

        #autoplay dugme je kliknuto(provera)
        if autoplayBtn.collidepoint(mouse):
            if not lost:
                autoplay = not autoplay
            else:
                autoplay = False
            time.sleep(0.2)
            continue

        # AI dugme je kliknuto(provera)
        elif aiButton.collidepoint(mouse) and not lost:
            makeAiMove = True
            time.sleep(0.2)

        #restart dugme je klinnuto
        elif resetButton.collidepoint(mouse):
            game = Minesweeper(height=HEIGHT, width=WIDTH, mines=MINES)
            ai = MinesweeperAI(height=HEIGHT, width=WIDTH)
            revealed = set()
            flags = set()
            lost = False
            mine_detonated = None
            continue

        #prikazi predikciju dugme je kliknuto
        elif safesMinesButton.collidepoint(mouse):
            showInference = not showInference
            time.sleep(0.2)

        #potez(korisnik)
        elif not lost:
            for i in range(HEIGHT):
                for j in range(WIDTH):
                    if (cells[i][j].collidepoint(mouse)
                            and (i, j) not in flags
                            and (i, j) not in revealed):
                        move = (i, j)

    #potez(AI)
    if autoplay or makeAiMove:
        if makeAiMove:
            makeAiMove = False
        move = ai.make_safe_move()
        if move is None:
            move = ai.make_random_move()
            if move is None:
                flags = ai.mines.copy()
                print("Nema preostalih poteza.")
                autoplay = False
            else:
                print("Nema poznatih sigurnih poteza, AI pravi nasumican potez.")
        else:
            print("AI pravi siguran potez.")

        #delay za AI
        if autoplay:
            time.sleep(autoplaySpeed)

    #AI pravi potez, knowlegde update
    if move:
        if game.is_mine(move):
            lost = True
            mine_detonated = move
            autoplay = False
        else:
            nearby = game.nearby_mines(move)
            revealed.add(move)
            ai.add_knowledge(move, nearby)

    pygame.display.flip()
