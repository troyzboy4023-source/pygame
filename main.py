import pygame
import pytmx
from pytmx.util_pygame import load_pygame
import os

print("Current working directory:", os.getcwd())

pygame.init()
SCREEN_W, SCREEN_H = 1000, 1000
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Tiled Map")

# TMX ачаалах
tmx_data = load_pygame("tiledd.tmx")

# Player image load & tile хэмжээтэй адил жижигрүүлэх
tile_w, tile_h = tmx_data.tilewidth, tmx_data.tileheight
player_image = pygame.image.load("male_vamp.png").convert_alpha()
player_image = pygame.transform.scale(player_image, (tile_w, tile_h))

# Player position (tile координат дээр)
player_x, player_y = 5, 5  # 5x5 tile дээр


def render_map(surface, tmx):
    for layer in tmx.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, image in layer.tiles():
                if image:
                    surface.blit(
                        image, (x * tmx.tilewidth, y * tmx.tileheight))


running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))
    render_map(screen, tmx_data)

    # Player-г map дээр draw хийх
    px = player_x * tile_w
    py = player_y * tile_h
    screen.blit(player_image, (px, py))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
