import pygame
import pytmx
from pytmx.util_pygame import load_pygame
import os
import sys

# ------------------------------
# Player class
# ------------------------------


class Player:
    def __init__(self, x, y, tile_w, tile_h):
        self.tile_w = tile_w
        self.tile_h = tile_h
        self.pixel_x = x * tile_w
        self.pixel_y = y * tile_h
        self.speed = 3
        self.run_speed = 5

        # Animation
        self.animations = {'down': [], 'up': [], 'left': [], 'right': []}
        self.current_direction = 'down'
        self.frame_index = 0
        self.animation_counter = 0
        self.animation_speed = 0.15
        self.load_animations()

    def load_animations(self):
        image_folder = "image"
        frames_dict = {
            'down': ["main_frontside.png", "main_frontside_left_walk.png", "main_frontside.png", "main_frontside_right_walk.png"],
            'up': ["main_frontside.png", "main_backside_left_walk.png", "main_frontside.png", "main_backside_right_walk.png"],
            'left': ["main_leftside.png", "main_leftside_walk1.png", "main_leftside.png", "main_leftside_walk2.png"],
            'right': ["main_rightside.png", "main_rightside_walk1.png", "main_rightside.png", "main_rightside_walk2.png"]
        }
        for direction, files in frames_dict.items():
            frames = []
            for f in files:
                try:
                    img = pygame.image.load(os.path.join(
                        image_folder, f)).convert_alpha()
                    img = pygame.transform.scale(
                        img, (self.tile_w, self.tile_h))
                    frames.append(img)
                except:
                    placeholder = pygame.Surface(
                        (self.tile_w, self.tile_h), pygame.SRCALPHA)
                    pygame.draw.rect(placeholder, (100, 150, 255),
                                     (0, 0, self.tile_w, self.tile_h))
                    frames.append(placeholder)
            self.animations[direction] = frames

    def handle_input(self, keys, collision_rects, map_width, map_height):
        current_speed = self.run_speed if (
            keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) else self.speed
        dx = dy = 0
        moving = False

        # Movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= current_speed
            self.current_direction = 'left'
            moving = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += current_speed
            self.current_direction = 'right'
            moving = True
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= current_speed
            if not (keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_RIGHT] or keys[pygame.K_d]):
                self.current_direction = 'up'
            moving = True
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += current_speed
            if not (keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_RIGHT] or keys[pygame.K_d]):
                self.current_direction = 'down'
            moving = True

        # Normalize diagonal
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707

        # Collision check
        new_rect = pygame.Rect(
            self.pixel_x+dx, self.pixel_y+dy, self.tile_w, self.tile_h)
        if not any(new_rect.colliderect(r) for r in collision_rects):
            # Bound check
            if 0 <= new_rect.x <= map_width*self.tile_w - self.tile_w and 0 <= new_rect.y <= map_height*self.tile_h - self.tile_h:
                self.pixel_x += dx
                self.pixel_y += dy

        # Update animation
        if moving:
            self.animation_counter += self.animation_speed
            if self.animation_counter >= 1:
                self.animation_counter = 0
                self.frame_index = (
                    self.frame_index+1) % len(self.animations[self.current_direction])
        else:
            self.frame_index = 0
            self.animation_counter = 0

    def draw(self, surface):
        img = self.animations[self.current_direction][self.frame_index]
        surface.blit(img, (self.pixel_x, self.pixel_y))


# ------------------------------
# Map class
# ------------------------------
class GameMap:
    def __init__(self, tmx_file):
        self.tmx_data = load_pygame(tmx_file)
        self.tile_w = self.tmx_data.tilewidth
        self.tile_h = self.tmx_data.tileheight
        self.width = self.tmx_data.width
        self.height = self.tmx_data.height
        self.collision_rects = self.build_collision_rects()

    def build_collision_rects(self):
        rects = []
        for layer in self.tmx_data.visible_layers:
            print(layer)
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer.iter_data():
                    layer = self.tmx_data.get_layer_by_name("rocks")
                    for x, y, gid in layer.tiles():
                        if gid != 0 and layer.properties.get("blocked"):
                            rects.append(pygame.Rect(
                                x * self.tmx_data.tilewidth,
                                y * self.tmx_data.tileheight,
                                self.tmx_data.tilewidth,
                                self.tmx_data.tileheight
                            ))
        return rects

    def draw(self, surface):
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, image in layer.tiles():
                    if image:
                        surface.blit(image, (x*self.tile_w, y*self.tile_h))


# ------------------------------
# Game class
# ------------------------------
class Game:
    def __init__(self, tmx_file):
        pygame.init()
        self.screen = pygame.display.set_mode((500, 500))
        pygame.display.set_caption("Tiled Map OOP")
        self.clock = pygame.time.Clock()
        self.running = True

        # Map
        self.game_map = GameMap(tmx_file)

        # Player
        self.player = Player(5, 5, self.game_map.tile_w, self.game_map.tile_h)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        keys = pygame.key.get_pressed()
        self.player.handle_input(
            keys, self.game_map.collision_rects, self.game_map.width, self.game_map.height)

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.game_map.draw(self.screen)
        self.player.draw(self.screen)
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        pygame.quit()


# ------------------------------
# Run
# ------------------------------
if __name__ == "__main__":
    tmx_file = "winter_boss_room.tmx"
    game = Game(tmx_file)
    game.run()
