import pygame
import os
pygame.init()


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

WIDTH, HEIGHT = 900,500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
FPS = 60
CLOCK = pygame.time.Clock()
pygame.display.set_caption("Python Skywars")



def draw_window():
    pygame.draw.line(WIN, WHITE, [0,250], [900,250], int(2.5))

    pygame.display.update()

def main():
    run = True
    while run:
        CLOCK.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        draw_window()

if __name__ == '__main__':
    main()
