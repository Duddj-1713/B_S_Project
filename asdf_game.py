import pygame, random, math, os, sys, json
from pytmx.util_pygame import load_pygame

pygame.init()

screen_w = 1280
screen_h = 720
screen = pygame.display.set_mode((screen_w, screen_h)) #스크린 사이즈 1280 * 720

clock = pygame.time.Clock()

def draw_outline(text, font, x, y, thickness, color): #텍스트 이미지 윤곽선 추가하는 함수
    for dx in range(-thickness, thickness * 2, thickness):
        for dy in range(-thickness, thickness * 2, thickness):
            if not (dx == 0 and dy == 0):
                outline_text = font.render(text, True, color)
                outline_text_rect = outline_text.get_rect(center=(x + dx, y + dy))
                screen.blit(outline_text, outline_text_rect)

BASE_DIR = os.path.dirname(__file__)

sprite_group = pygame.sprite.Group()


class Player:
    def __init__(self):
        self.hp = 100
        self.atk = 20
        self.speed = 0

        self.acceleration = 2
        self.friction = 0.5
        self.max_speed = 20

        self.moving_angle = 0

        self.world_x = screen_w // 2
        self.world_y = screen_h // 2

        self.pov_x = self.world_x - screen_w // 2 + 32
        self.pov_y = self.world_y - screen_h // 2 + 32

    def update(self, view_w, view_h):
        dx, dy = 0, 0

        if key_press[pygame.K_w]:
            dy -= 1
        if key_press[pygame.K_s]:
            dy += 1
        if key_press[pygame.K_a]:
            dx -= 1
        if key_press[pygame.K_d]:
            dx += 1

        if dx != 0 or dy != 0:
            self.speed = min(self.speed + self.acceleration * dt, self.max_speed)

            length = math.hypot(dx, dy)
            dx /= length
            dy /= length

            self.world_x += self.speed * dx
            self.world_y += self.speed * dy

            self.pov_x = self.world_x - view_w // 2 + 32
            self.pov_y = self.world_y - view_h // 2 + 32
        else:
            self.speed = max(self.speed - self.friction * dt, 0)

            self.world_x += self.speed * dx
            self.world_y += self.speed * dy

            self.pov_x = self.world_x - view_w // 2 + 32
            self.pov_y = self.world_y - view_h // 2 + 32

class Game:
    def __init__(self): #클래스 초기화
        global screen

        self.player = Player()     
        self.map1_tmx_data = load_pygame(os.path.join(BASE_DIR, 'map_data', 'map1.tmx')) #튜토리얼 맵 데이터

        self.min_zoom = 0.7
        self.max_zoom = 3.0
        self.zoom = 1.5

        self.game_screen = pygame.Surface((int(screen_w / self.zoom), int(screen_h / self.zoom))) 


    def update(self): #게임 내 연산 함수
        global screen

        for event in events:
            if event.type == pygame.MOUSEWHEEL:
                self.zoom += event.y * 0.1
                self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom))
                w = int(screen_w / self.zoom)
                h = int(screen_h / self.zoom)
                self.game_screen = pygame.Surface((w, h))

        self.player.update(self.game_screen.get_width(), self.game_screen.get_height())


    def draw(self): #게임 내 에셋 불러오기
        tile_w = self.map1_tmx_data.tilewidth
        tile_h = self.map1_tmx_data.tileheight

        view_w, view_h = self.game_screen.get_width(), self.game_screen.get_height()

        start_col = max(0, int(self.player.pov_x // tile_w) - 1)
        start_row = max(0, int(self.player.pov_y // tile_h) - 1)
        end_col = min(self.map1_tmx_data.width, start_col + view_w // tile_w + 3)
        end_row = min(self.map1_tmx_data.height, start_row + view_h // tile_h + 3)

        for layer in self.map1_tmx_data.visible_layers: #화면 surface에 타일 그리기
            if hasattr(layer, 'data'):
                for x in range(start_col, end_col): #플래이어 화면에만 보이는 타일만 불러오기
                    for y in range(start_row, end_row):
                        gid = layer.data[y][x]
                        surf = self.map1_tmx_data.get_tile_image_by_gid(gid)
                        if surf:
                            pos = (x * tile_w - self.player.pov_x, y * tile_h - self.player.pov_y)
                            self.game_screen.blit(surf, pos)

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)


running = True

game = Game() #게임 클래스 불러오기

while running: #메인 루프

    dt = clock.tick(60) / 1000
    events = pygame.event.get()
    key_press = pygame.key.get_pressed()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    game.update()
    game.draw()

    scaled = pygame.transform.scale(game.game_screen, (screen_w, screen_h))
    screen.blit(scaled, (0, 0))
    pygame.display.flip()

pygame.quit()