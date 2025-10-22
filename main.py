import pygame
import pytmx
from pytmx.util_pygame import load_pygame
import os
import sys
import random
from enum import Enum


class State(Enum):
    IDLE = 0
    ATTACKING = 1
    HURT = 2
    DEAD = 3


class Player:
    def __init__(self, x, y, tile_w, tile_h):
        self.tile_w = tile_w
        self.tile_h = tile_h
        self.size_multiplier = 1.0
        self.render_w = int(tile_w * self.size_multiplier)
        self.render_h = int(tile_h * self.size_multiplier)
        self.pixel_x = x * tile_w
        self.pixel_y = y * tile_h
        self.speed = 1
        self.run_speed = 5

        # Combat stats
        self.max_health = 100
        self.health = 100
        self.max_stamina = 100
        self.stamina = 100
        self.stamina_regen = 0.3
        self.attack_damage = 20
        self.attack_cost = 25
        self.attack_range = 80
        self.attack_cooldown = 0
        self.state = State.IDLE
        self.hit_flash = 0

        # Animation
        self.animations = {'down': [], 'up': [], 'left': [], 'right': []}
        self.current_direction = 'down'
        self.frame_index = 0
        self.animation_counter = 0
        self.animation_speed = 0.15
        self.load_animations()

    def load_animations(self):
        image_folder = "image"  # Player images are in 'image' folder
        frames_dict = {
            'down': ["main_frontside_right_walk.png", "main_frontside_left_walk.png", "main_frontside_right_walk.png", "main_frontside_left_walk.png"],
            'up': ["main_backside_left_walk.png", "main_backside_right_walk.png", "main_backside_left_walk.png", "main_backside_right_walk.png"],
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
                        img, (self.render_w, self.render_h))
                    frames.append(img)
                except:
                    placeholder = pygame.Surface(
                        (self.render_w, self.render_h), pygame.SRCALPHA)
                    pygame.draw.rect(placeholder, (100, 150, 255),
                                     (0, 0, self.render_w, self.render_h))
                    frames.append(placeholder)
            self.animations[direction] = frames

    def attack(self, enemies):
        """Attempt to attack nearby enemies"""
        if self.stamina >= self.attack_cost and self.attack_cooldown == 0 and self.state != State.DEAD:
            self.stamina -= self.attack_cost
            self.attack_cooldown = 30  # Cooldown frames

            # Check for enemies in range
            hit_any = False
            for enemy in enemies:
                if enemy.state != State.DEAD:
                    distance = ((self.pixel_x - enemy.pixel_x)**2 +
                                (self.pixel_y - enemy.pixel_y)**2)**0.5
                    if distance <= self.attack_range:
                        enemy.take_damage(self.attack_damage)
                        hit_any = True

            return hit_any
        return False

    def take_damage(self, damage):
        """Take damage from enemy"""
        if self.state != State.DEAD:
            self.health -= damage
            self.hit_flash = 10

            if self.health <= 0:
                self.health = 0
                self.state = State.DEAD
            else:
                self.state = State.HURT

    def update_combat(self):
        """Update combat-related stats"""
        # Regenerate stamina
        if self.state != State.ATTACKING:
            self.stamina = min(
                self.max_stamina, self.stamina + self.stamina_regen)

        # Update cooldowns
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if self.hit_flash > 0:
            self.hit_flash -= 1

        # Reset state if hurt
        if self.state == State.HURT and self.hit_flash == 0:
            self.state = State.IDLE

    def handle_input(self, keys, collision_rects, map_width, map_height):
        if self.state == State.DEAD:
            return

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

    def draw(self, surface, camera_x, camera_y):
        img = self.animations[self.current_direction][self.frame_index]

        # Flash white when hit
        if self.hit_flash > 0:
            flash_img = img.copy()
            flash_img.fill((255, 255, 255, 100),
                           special_flags=pygame.BLEND_RGB_ADD)
            surface.blit(flash_img, (self.pixel_x -
                         camera_x, self.pixel_y - camera_y))
        else:
            surface.blit(img, (self.pixel_x - camera_x,
                         self.pixel_y - camera_y))


class Enemy:
    def __init__(self, x, y, tile_w, tile_h, enemy_type='goblin'):
        self.tile_w = tile_w
        self.tile_h = tile_h
        self.size_multiplier = 3.0
        self.render_w = int(tile_w * self.size_multiplier)
        self.render_h = int(tile_h * self.size_multiplier)
        self.pixel_x = x * tile_w
        self.pixel_y = y * tile_h
        self.enemy_type = enemy_type

        # Combat stats
        if enemy_type == 'goblin':
            self.max_health = 50
            self.speed = 1.5
            self.attack_damage = 10
            self.attack_range = 60
            self.color = (100, 200, 100)
        elif enemy_type == 'orc':
            self.max_health = 80
            self.speed = 1.0
            self.attack_damage = 15
            self.attack_range = 70
            self.color = (200, 100, 100)
        else:  # skeleton
            self.max_health = 40
            self.speed = 2.0
            self.attack_damage = 8
            self.attack_range = 50
            self.color = (200, 200, 200)

        self.health = self.max_health
        self.attack_cooldown = 0
        self.state = State.IDLE
        self.hit_flash = 0

        # AI
        self.detection_range = 200
        self.wander_timer = 0
        self.wander_direction = [0, 0]

        # Animation
        self.frame_index = 0
        self.animation_counter = 0
        self.create_sprite()

    def create_sprite(self):
        """Create a simple enemy sprite"""
        self.image = pygame.Surface(
            (self.render_w, self.render_h), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, self.color,
                            (10, 10, self.render_w-20, self.render_h-20))
        pygame.draw.circle(self.image, self.color,
                           (self.render_w//2, self.render_h//3), 15)
        # Eyes
        pygame.draw.circle(self.image, (255, 0, 0),
                           (self.render_w//2 - 8, self.render_h//3 - 3), 4)
        pygame.draw.circle(self.image, (255, 0, 0),
                           (self.render_w//2 + 8, self.render_h//3 - 3), 4)

    def take_damage(self, damage):
        """Take damage"""
        if self.state != State.DEAD:
            self.health -= damage
            self.hit_flash = 10

            if self.health <= 0:
                self.health = 0
                self.state = State.DEAD
            else:
                self.state = State.HURT

    def update(self, player, collision_rects, map_width, map_height):
        """Update enemy AI and movement"""
        if self.state == State.DEAD:
            return

        # Update combat state
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.hit_flash > 0:
            self.hit_flash -= 1
        if self.state == State.HURT and self.hit_flash == 0:
            self.state = State.IDLE

        # Check distance to player
        distance = ((self.pixel_x - player.pixel_x)**2 +
                    (self.pixel_y - player.pixel_y)**2)**0.5

        if distance <= self.detection_range and player.state != State.DEAD:
            # Chase player
            dx = player.pixel_x - self.pixel_x
            dy = player.pixel_y - self.pixel_y
            length = (dx**2 + dy**2)**0.5

            if length > 0:
                dx = (dx / length) * self.speed
                dy = (dy / length) * self.speed

                # Try to move
                new_rect = pygame.Rect(self.pixel_x + dx, self.pixel_y + dy,
                                       self.tile_w, self.tile_h)
                if not any(new_rect.colliderect(r) for r in collision_rects):
                    self.pixel_x += dx
                    self.pixel_y += dy

            # Attack if in range
            if distance <= self.attack_range and self.attack_cooldown == 0:
                player.take_damage(self.attack_damage)
                self.attack_cooldown = 60  # Attack cooldown
        else:
            # Wander
            if self.wander_timer <= 0:
                self.wander_timer = random.randint(60, 180)
                self.wander_direction = [
                    random.uniform(-1, 1), random.uniform(-1, 1)]
            else:
                self.wander_timer -= 1
                dx = self.wander_direction[0] * self.speed * 0.5
                dy = self.wander_direction[1] * self.speed * 0.5

                new_rect = pygame.Rect(self.pixel_x + dx, self.pixel_y + dy,
                                       self.tile_w, self.tile_h)
                if not any(new_rect.colliderect(r) for r in collision_rects):
                    if 0 <= new_rect.x <= map_width*self.tile_w and 0 <= new_rect.y <= map_height*self.tile_h:
                        self.pixel_x += dx
                        self.pixel_y += dy

    def draw(self, surface, camera_x, camera_y):
        """Draw enemy"""
        img = self.image.copy()

        # Flash when hit
        if self.hit_flash > 0:
            img.fill((255, 255, 255, 100), special_flags=pygame.BLEND_RGB_ADD)

        # Fade out when dead
        if self.state == State.DEAD:
            img.set_alpha(100)

        surface.blit(img, (self.pixel_x - camera_x, self.pixel_y - camera_y))

        # Draw health bar
        if self.state != State.DEAD:
            bar_width = self.render_w
            bar_height = 5
            bar_x = self.pixel_x - camera_x
            bar_y = self.pixel_y - camera_y - 10

            # Background
            pygame.draw.rect(surface, (100, 0, 0),
                             (bar_x, bar_y, bar_width, bar_height))
            # Health
            health_width = int((self.health / self.max_health) * bar_width)
            pygame.draw.rect(surface, (0, 255, 0),
                             (bar_x, bar_y, health_width, bar_height))


class Camera:
    def __init__(self, screen_width, screen_height, map_width, map_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.map_width = map_width
        self.map_height = map_height
        self.x = 0
        self.y = 0

    def update(self, target_x, target_y, target_width, target_height):
        self.x = target_x + target_width // 2 - self.screen_width // 2
        self.y = target_y + target_height // 2 - self.screen_height // 2
        self.x = max(0, min(self.x, self.map_width - self.screen_width))
        self.y = max(0, min(self.y, self.map_height - self.screen_height))

    def update_screen_size(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height


class GameMap:
    def __init__(self, tmx_file):
        # Try to load TMX normally first. If it fails due to missing tileset
        # references (common when TMX references ../../layers/...), try to
        # rewrite tileset 'source' attributes to point to files located in the
        # same directory as the TMX file and load that temporary fixed TMX.
        try:
            self.tmx_data = load_pygame(tmx_file)
        except Exception as e:
            # Catch any error and attempt to auto-fix tileset paths
            print(f"Error loading TMX file: {e}")
            print("Attempting to auto-fix tileset source paths...")

            import xml.etree.ElementTree as ET

            tmx_dir = os.path.dirname(os.path.abspath(tmx_file))
            tree = ET.parse(tmx_file)
            root = tree.getroot()
            changed = False

            # Iterate tileset elements and try to point them at local .tsx
            for tileset in root.findall('tileset'):
                src = tileset.get('source')
                if src:
                    base = os.path.basename(src)
                    candidate = os.path.join(tmx_dir, base)
                    if os.path.exists(candidate):
                        # Use absolute path so loader can find it regardless
                        # of current working directory
                        tileset.set('source', candidate)
                        changed = True
                    else:
                        # Create a minimal .tsx in the map directory that points
                        # to a placeholder image so pytmx can load the tileset.
                        placeholder_tsx = candidate
                        placeholder_img = os.path.join(
                            tmx_dir, base.replace('.tsx', '.png'))
                        try:
                            # Create placeholder image if missing
                            if not os.path.exists(placeholder_img):
                                try:
                                    from PIL import Image
                                    Image.new('RGBA', (32, 32), (0, 0, 0, 0)).save(
                                        placeholder_img)
                                except Exception:
                                    with open(placeholder_img, 'wb') as f:
                                        f.write(b'\x89PNG\r\n\x1a\n')

                            # Write a basic TSX file referencing the placeholder image
                            with open(placeholder_tsx, 'w', encoding='utf-8') as f:
                                f.write(
                                    '<?xml version="1.0" encoding="UTF-8"?>\n')
                                f.write(
                                    f'<tileset version="1.10" tiledversion="1.11.2" name="{base.replace('.tsx', '')}" tilewidth="32" tileheight="32" tilecount="1" columns="1">\n')
                                f.write(
                                    f' <image source="{os.path.basename(placeholder_img)}" width="32" height="32"/>\n')
                                f.write('</tileset>\n')

                            tileset.set('source', placeholder_tsx)
                            changed = True
                            print(
                                f"Created placeholder tileset: {placeholder_tsx}")
                        except Exception:
                            pass

            if changed:
                fixed_path = os.path.join(tmx_dir, os.path.basename(
                    tmx_file).replace('.tmx', '_fixed.tmx'))
                tree.write(fixed_path, encoding='utf-8', xml_declaration=True)
                print(f"Wrote fixed TMX to: {fixed_path}")
                # Also try to fix referenced .tsx files by making their image
                # sources absolute (or creating placeholder images if missing).
                for tileset in root.findall('tileset'):
                    src = tileset.get('source')
                    if not src:
                        continue
                    tsx_path = src
                    # If source is not absolute, it was set to candidate above
                    if not os.path.isabs(tsx_path):
                        tsx_path = os.path.join(tmx_dir, tsx_path)

                    if not os.path.exists(tsx_path):
                        continue

                    try:
                        ts_tree = ET.parse(tsx_path)
                        ts_root = ts_tree.getroot()
                        img = ts_root.find('image')
                        if img is not None:
                            img_src = img.get('source')
                            if img_src:
                                img_base = os.path.basename(img_src)
                                img_candidate = os.path.join(tmx_dir, img_base)
                                # If image exists next to the TMX, rewrite to that
                                if os.path.exists(img_candidate):
                                    img.set('source', img_candidate)
                                    ts_tree.write(
                                        tsx_path, encoding='utf-8', xml_declaration=True)
                                else:
                                    # Create a tiny placeholder PNG next to TMX so loader
                                    # can proceed. Placeholder size uses 32x32.
                                    placeholder_path = img_candidate
                                    if not os.path.exists(placeholder_path):
                                        try:
                                            from PIL import Image
                                            placeholder = Image.new(
                                                'RGBA', (32, 32), (0, 0, 0, 0))
                                            placeholder.save(placeholder_path)
                                            print(
                                                f"Created placeholder image: {placeholder_path}")
                                            img.set('source', placeholder_path)
                                            ts_tree.write(
                                                tsx_path, encoding='utf-8', xml_declaration=True)
                                        except Exception:
                                            # If PIL not available, create a minimal PNG binary
                                            try:
                                                with open(placeholder_path, 'wb') as f:
                                                    f.write(
                                                        b'\x89PNG\r\n\x1a\n')
                                                img.set(
                                                    'source', placeholder_path)
                                                ts_tree.write(
                                                    tsx_path, encoding='utf-8', xml_declaration=True)
                                                print(
                                                    f"Wrote minimal placeholder PNG: {placeholder_path}")
                                            except Exception:
                                                pass
                    except Exception:
                        # Ignore errors while patching tileset files
                        pass

                # Try loading the fixed TMX
                try:
                    self.tmx_data = load_pygame(fixed_path)
                except Exception as load_err:
                    print("Auto-fix failed when loading the fixed TMX:", load_err)
                    raise
            else:
                print("No local tileset files found to fix the TMX.\n"
                      "Make sure your .tsx files are next to the .tmx or adjust paths in the TMX.")
                raise

        self.tile_w = self.tmx_data.tilewidth
        self.tile_h = self.tmx_data.tileheight
        self.width = self.tmx_data.width
        self.height = self.tmx_data.height
        self.collision_rects = self.build_collision_rects()

    def build_collision_rects(self):
        rects = []
        try:
            # Look for the collision layer
            collision_layer = self.tmx_data.get_layer_by_name("collision")
            if collision_layer and collision_layer.properties.get("blocked"):
                for x, y, gid in collision_layer.tiles():
                    if gid != 0:
                        rects.append(pygame.Rect(
                            x * self.tmx_data.tilewidth,
                            y * self.tmx_data.tileheight,
                            self.tmx_data.tilewidth,
                            self.tmx_data.tileheight
                        ))
        except Exception as e:
            print(f"Warning: Could not load collision layer: {e}")

        # Alternative: Check all layers for blocked tiles
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                if layer.properties.get("blocked"):
                    for x, y, gid in layer.tiles():
                        if gid != 0:
                            rects.append(pygame.Rect(
                                x * self.tmx_data.tilewidth,
                                y * self.tmx_data.tileheight,
                                self.tmx_data.tilewidth,
                                self.tmx_data.tileheight
                            ))
        return rects

    def draw(self, surface, camera_x, camera_y):
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, image in layer.tiles():
                    if image:
                        surface.blit(
                            image, (x*self.tile_w - camera_x, y*self.tile_h - camera_y))


def draw_ui_bar(surface, x, y, w, h, value, max_value, color, bg_color, label):
    """Draw a status bar with label"""
    font = pygame.font.Font(None, 20)
    label_surf = font.render(label, True, (255, 255, 255))
    surface.blit(label_surf, (x, y - 18))

    # Background
    pygame.draw.rect(surface, bg_color, (x, y, w, h))
    # Fill
    fill_w = int((value / max_value) * w)
    pygame.draw.rect(surface, color, (x, y, fill_w, h))
    # Border
    pygame.draw.rect(surface, (0, 0, 0), (x, y, w, h), 2)

    # Text
    text = font.render(f"{int(value)}/{int(max_value)}", True, (255, 255, 255))
    text_rect = text.get_rect(center=(x + w//2, y + h//2))
    surface.blit(text, text_rect)


class Game:
    def __init__(self, tmx_file, fullscreen=False):
        pygame.init()
        self.default_width = 800
        self.default_height = 600
        self.fullscreen = fullscreen

        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.screen_width = self.screen.get_width()
            self.screen_height = self.screen.get_height()
        else:
            self.screen_width = self.default_width
            self.screen_height = self.default_height
            self.screen = pygame.display.set_mode(
                (self.screen_width, self.screen_height))

        pygame.display.set_caption("Medieval RPG - Press SPACE to Attack")
        self.clock = pygame.time.Clock()
        self.running = True

        # Map
        self.game_map = GameMap(tmx_file)

        # Player
        self.player = Player(10, 22, self.game_map.tile_w,
                             self.game_map.tile_h)

        # Enemies
        self.enemies = [
            Enemy(10, 10, self.game_map.tile_w,
                  self.game_map.tile_h, 'goblin'),
            Enemy(15, 8, self.game_map.tile_w, self.game_map.tile_h, 'orc'),
            Enemy(8, 15, self.game_map.tile_w,
                  self.game_map.tile_h, 'skeleton'),
        ]

        # Camera
        self.camera = Camera(
            self.screen_width,
            self.screen_height,
            self.game_map.width * self.game_map.tile_w,
            self.game_map.height * self.game_map.tile_h
        )

        # UI
        self.font = pygame.font.Font(None, 24)
        self.message = ""
        self.message_timer = 0

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen

        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.screen_width = self.screen.get_width()
            self.screen_height = self.screen.get_height()
        else:
            self.screen_width = self.default_width
            self.screen_height = self.default_height
            self.screen = pygame.display.set_mode(
                (self.screen_width, self.screen_height))

        self.camera.update_screen_size(self.screen_width, self.screen_height)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11 or (event.key == pygame.K_RETURN and (pygame.key.get_mods() & pygame.KMOD_ALT)):
                    self.toggle_fullscreen()
                elif event.key == pygame.K_ESCAPE:
                    if self.fullscreen:
                        self.toggle_fullscreen()
                    else:
                        self.running = False
                elif event.key == pygame.K_SPACE:
                    # Attack
                    if self.player.attack(self.enemies):
                        self.message = "Hit!"
                        self.message_timer = 30
                    else:
                        if self.player.stamina < self.player.attack_cost:
                            self.message = "Not enough stamina!"
                        elif self.player.attack_cooldown > 0:
                            self.message = "Attack on cooldown!"
                        else:
                            self.message = "No enemy in range!"
                        self.message_timer = 30

    def update(self):
        keys = pygame.key.get_pressed()
        self.player.handle_input(
            keys, self.game_map.collision_rects, self.game_map.width, self.game_map.height)

        # Update player combat
        self.player.update_combat()

        # Update enemies
        for enemy in self.enemies:
            enemy.update(self.player, self.game_map.collision_rects,
                         self.game_map.width, self.game_map.height)

        # Update camera
        self.camera.update(
            self.player.pixel_x,
            self.player.pixel_y,
            self.player.tile_w,
            self.player.tile_h
        )

        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= 1

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.game_map.draw(self.screen, self.camera.x, self.camera.y)

        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen, self.camera.x, self.camera.y)

        # Draw player
        self.player.draw(self.screen, self.camera.x, self.camera.y)

        # Draw UI
        draw_ui_bar(self.screen, 10, 10, 200, 25, self.player.health,
                    self.player.max_health, (46, 204, 113), (34, 139, 34), "Health")
        draw_ui_bar(self.screen, 10, 50, 200, 20, self.player.stamina,
                    self.player.max_stamina, (241, 196, 15), (150, 100, 0), "Stamina")

        # Draw controls
        controls = self.font.render(
            "WASD/Arrows: Move | SHIFT: Run | SPACE: Attack", True, (255, 255, 255))
        self.screen.blit(controls, (10, self.screen_height - 30))

        # Draw message
        if self.message_timer > 0:
            msg_surf = self.font.render(self.message, True, (255, 255, 0))
            self.screen.blit(msg_surf, (self.screen_width //
                             2 - msg_surf.get_width() // 2, 100))

        # Draw game over
        if self.player.state == State.DEAD:
            game_over_font = pygame.font.Font(None, 72)
            game_over_surf = game_over_font.render(
                "YOU DIED!", True, (255, 0, 0))
            self.screen.blit(game_over_surf,
                             (self.screen_width // 2 - game_over_surf.get_width() // 2,
                              self.screen_height // 2))

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(100)
        pygame.quit()


def find_tmx_file():
    """Find the TMX file in common locations"""
    # Possible locations to check
    possible_paths = [
        os.path.join("map", "winter_boss_room.tmx"),
        os.path.join("map", "boss_room_angel.tmx"),
        "winter_boss_room.tmx",
        "boss_room_angel.tmx"
    ]

    # Check if map folder exists and list its contents
    if os.path.exists("map"):
        print("Contents of 'map' folder:")
        for file in os.listdir("map"):
            if file.endswith('.tmx'):
                print(f"  - {file}")
                possible_paths.insert(0, os.path.join("map", file))
    else:
        print("'map' folder not found!")

    # Check current directory for TMX files
    print("\nTMX files in current directory:")
    for file in os.listdir("."):
        if file.endswith('.tmx'):
            print(f"  - {file}")
            if file not in possible_paths:
                possible_paths.insert(0, file)

    # Try each path
    for path in possible_paths:
        if os.path.exists(path):
            print(f"\nUsing map file: {path}")
            return path

    # If no file found
    print("\nERROR: No TMX file found!")
    print("Please ensure you have a .tmx file in either:")
    print("  - The 'map' folder")
    print("  - The current directory")
    return None


if __name__ == "__main__":
    # Find the TMX file
    tmx_file = find_tmx_file()

    if tmx_file is None:
        print("\nPlease place your TMX map file in the 'map' folder or current directory.")
        sys.exit(1)

    start_fullscreen = False
    if len(sys.argv) > 1 and sys.argv[1].lower() in ['fullscreen', '-f', '--fullscreen']:
        start_fullscreen = True

    try:
        game = Game(tmx_file, fullscreen=start_fullscreen)
        game.run()
    except Exception as e:
        print(f"\nError starting game: {e}")
        sys.exit(1)
