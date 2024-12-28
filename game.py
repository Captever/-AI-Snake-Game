import pygame
import sys

# Pygame 초기화
pygame.init()

# 화면 설정
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Snake")

# 색상 정의
WHITE = (255, 255, 255)
GRAY = (127, 127, 127)

# 게임 루프
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 화면 그리기
    screen.fill(GRAY)
    
    # 화면 업데이트
    pygame.display.flip()

# Pygame 종료
pygame.quit()
sys.exit()
