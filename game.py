import pygame
import pytmx
from pytmx.util_pygame import load_pygame
import os
import sys
import random
import math
from enum import Enum


class State(Enum):
    IDLE = 0
    ATTACKING = 1
    HURT = 2
    DEAD = 3


class Projectile:
    def __init__(self, x, y, target_x, target_y, damage, is_enemy=False, projectile_type='default'):
        self.x = x
        self.y = y
        self.damage = damage
        self.speed = 8
        self.is_enemy = is_enemy
        self.active = True
        self.projectile_type = projectile_type

        dx = target_x - x
        dy = target_y - y
        length = math.sqrt(dx**2 + dy**2)
        if length > 0:
            self.vel_x = (dx / length) * self.speed
            self.vel_y = (dy / length) * self.speed
        else:
            self.vel_x = 0
            self.vel_y = 0

        # Load appropriate projectile image based on type
        try:
            base_dir = os.path.join(os.path.dirname(
                os.path.abspath(__file__)), 'image')

            if projectile_type == 'fire':
                img_path = os.path.join(base_dir, 'fire_effect.png')
            elif projectile_type == 'water':
                img_path = os.path.join(base_dir, 'water_effect.png')
            elif projectile_type == 'void':
                img_path = os.path.join(base_dir, 'void_effect.png')
            elif projectile_type == 'ice':
                img_path = os.path.join(base_dir, 'ice_effect.png')
            elif projectile_type == 'lightning':
                img_path = os.path.join(base_dir, 'lightning_effect.png')
            elif projectile_type == 'holy':
                img_path = os.path.join(base_dir, 'holy_effect.png')
            else:
                img_path = os.path.join(base_dir, 'projectile.png')

            if os.path.exists(img_path):
                self.image = pygame.image.load(img_path).convert_alpha()
                self.image = pygame.transform.scale(self.image, (20, 20))
            else:
                # Fallback with color coding
                self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
                if projectile_type == 'fire':
                    pygame.draw.circle(self.image, (255, 100, 0), (10, 10), 10)
                elif projectile_type == 'water':
                    pygame.draw.circle(self.image, (0, 150, 255), (10, 10), 10)
                elif projectile_type == 'void':
                    pygame.draw.circle(self.image, (150, 0, 200), (10, 10), 10)
                elif projectile_type == 'ice':
                    pygame.draw.circle(
                        self.image, (150, 200, 255), (10, 10), 10)
                elif projectile_type == 'lightning':
                    pygame.draw.circle(
                        self.image, (255, 255, 100), (10, 10), 10)
                elif projectile_type == 'holy':
                    pygame.draw.circle(
                        self.image, (255, 255, 200), (10, 10), 10)
                else:
                    pygame.draw.circle(self.image, (255, 200, 0), (10, 10), 10)
        except Exception as e:
            print(f"Error loading projectile image: {e}")
            self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 200, 0), (10, 10), 10)

        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.rect.center = (self.x, self.y)

    def check_collision(self, collision_rects):
        """Check if projectile hits a collision tile"""
        for rect in collision_rects:
            if self.rect.colliderect(rect):
                return True
        return False

    def draw(self, surface, camera_x, camera_y):
        surface.blit(self.image, (self.x - camera_x -
                     10, self.y - camera_y - 10))


class FloatingText:
    def __init__(self, x, y, text, color=(255, 0, 0)):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.timer = 60
        self.vel_y = -2
        self.alpha = 255

    def update(self):
        self.y += self.vel_y
        self.timer -= 1
        self.alpha = int((self.timer / 60) * 255)

    def draw(self, surface, camera_x, camera_y):
        if self.timer > 0:
            font = pygame.font.Font(None, 36)
            text_surf = font.render(self.text, True, self.color)
            text_surf.set_alpha(self.alpha)
            surface.blit(text_surf, (self.x - camera_x, self.y - camera_y))

    def is_alive(self):
        return self.timer > 0


class DialogueSystem:
    def __init__(self):
        self.active = False
        self.dialogues = []
        self.current_index = 0
        self.font = pygame.font.Font(None, 28)

    def start_dialogue(self, dialogues):
        self.dialogues = dialogues
        self.current_index = 0
        self.active = len(dialogues) > 0

    def next(self):
        if self.active:
            self.current_index += 1
            if self.current_index >= len(self.dialogues):
                self.active = False
                self.current_index = 0

    def draw(self, surface, screen_width, screen_height):
        if not self.active or not self.dialogues:
            return

        box_height = 120
        box_y = screen_height - box_height - 10
        box_rect = pygame.Rect(10, box_y, screen_width - 20, box_height)

        bg_surf = pygame.Surface((box_rect.width, box_rect.height))
        bg_surf.set_alpha(200)
        bg_surf.fill((20, 20, 40))
        surface.blit(bg_surf, box_rect.topleft)

        pygame.draw.rect(surface, (255, 255, 255), box_rect, 3)

        if self.current_index < len(self.dialogues):
            text = self.dialogues[self.current_index]
            words = text.split(' ')
            lines = []
            current_line = ""
            max_width = box_rect.width - 40

            for word in words:
                test_line = current_line + word + " "
                if self.font.size(test_line)[0] < max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word + " "
            if current_line:
                lines.append(current_line)

            y_offset = box_y + 20
            for line in lines[:3]:
                text_surf = self.font.render(
                    line.strip(), True, (255, 255, 255))
                surface.blit(text_surf, (box_rect.x + 20, y_offset))
                y_offset += 30

        prompt = self.font.render(
            "Press SPACE to continue...", True, (200, 200, 200))
        surface.blit(prompt, (box_rect.x + 20, box_rect.bottom - 35))


class NPC:
    """Interactive NPC that can be talked to"""

    def __init__(self, x, y, tile_w, tile_h, npc_name='barman', dialogues=None):
        self.tile_w = tile_w
        self.tile_h = tile_h
        self.size_multiplier = 2.0
        self.render_w = int(tile_w * self.size_multiplier)
        self.render_h = int(tile_h * self.size_multiplier)
        self.pixel_x = x
        self.pixel_y = y
        self.npc_name = npc_name
        self.interaction_range = 80

        if dialogues is None:
            self.dialogues = self.get_default_dialogues()
        else:
            self.dialogues = dialogues

        self.load_image()

    def get_default_dialogues(self):
        """Get default dialogues based on NPC type"""
        if self.npc_name.lower() == 'barman':
            return [
                "Welcome to the inn, weary traveler!",
                "I've been running this establishment for many years.",
                "If you're looking for adventure, head north to the main map.",
                "But beware! Dangerous creatures lurk in those lands.",
                "The boss rooms are especially perilous. Make sure you're prepared!",
                "Come back anytime you need rest and healing. Safe travels!"
            ]
        else:
            return [
                f"Greetings, traveler! I am {self.npc_name}.",
                "The world is full of dangers and mysteries.",
                "Be careful on your journey!"
            ]

    def load_image(self):
        try:
            img_path = os.path.join(os.path.dirname(
                os.path.abspath(__file__)), 'image', f'{self.npc_name}.png')
            if os.path.exists(img_path):
                self.image = pygame.image.load(img_path).convert_alpha()
                self.image = pygame.transform.scale(
                    self.image, (self.render_w, self.render_h))
            else:
                # Fallback placeholder
                self.image = pygame.Surface(
                    (self.render_w, self.render_h), pygame.SRCALPHA)
                if 'barman' in self.npc_name.lower():
                    pygame.draw.rect(self.image, (139, 69, 19),
                                     (10, 10, self.render_w-20, self.render_h-20))
                    pygame.draw.circle(
                        self.image, (255, 220, 177), (self.render_w//2, self.render_h//3), 15)
                else:
                    pygame.draw.rect(self.image, (100, 100, 200),
                                     (10, 10, self.render_w-20, self.render_h-20))
                    pygame.draw.circle(
                        self.image, (255, 220, 177), (self.render_w//2, self.render_h//3), 15)
        except Exception as e:
            print(f"Error loading NPC image: {e}")
            self.image = pygame.Surface(
                (self.render_w, self.render_h), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (100, 100, 200),
                             (10, 10, self.render_w-20, self.render_h-20))

    def can_interact(self, player):
        """Check if player is close enough to interact"""
        distance = math.sqrt((self.pixel_x - player.pixel_x)
                             ** 2 + (self.pixel_y - player.pixel_y)**2)
        return distance <= self.interaction_range

    def draw(self, surface, camera_x, camera_y):
        surface.blit(self.image, (self.pixel_x -
                     camera_x, self.pixel_y - camera_y))

        # Draw name tag
        font = pygame.font.Font(None, 20)
        name_surf = font.render(self.npc_name.upper(), True, (255, 255, 255))
        name_x = self.pixel_x - camera_x + \
            (self.render_w - name_surf.get_width()) // 2
        name_y = self.pixel_y - camera_y - 15

        # Draw background for name
        bg_rect = pygame.Rect(
            name_x - 5, name_y - 2, name_surf.get_width() + 10, name_surf.get_height() + 4)
        bg_surf = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surf.set_alpha(180)
        bg_surf.fill((0, 0, 0))
        surface.blit(bg_surf, bg_rect.topleft)

        surface.blit(name_surf, (name_x, name_y))


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
        self.run_speed = 3

        # Level and XP system
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 100
        self.total_xp = 0

        # Base stats that scale with level
        self.base_max_health = 100
        self.base_max_stamina = 100
        self.base_attack_damage = 20
        self.base_crit_chance = 0.25

        # Current stats (will be calculated based on level)
        self.max_health = self.base_max_health
        self.health = self.max_health
        self.max_stamina = self.base_max_stamina
        self.stamina = self.max_stamina
        self.attack_damage = self.base_attack_damage
        self.crit_chance = self.base_crit_chance

        self.stamina_regen = 0.3
        self.attack_cost = 25
        self.attack_range = 80
        self.attack_cooldown = 0
        self.crit_multiplier = 2.0
        self.state = State.IDLE
        self.hit_flash = 0

        self.animations = {'idle': [], 'walking': [],
                           'attacking': [], 'dying': []}
        self.current_direction = 'down'
        self.frame_index = 0
        self.animation_counter = 0.0
        self.animation_speed = 0.15
        self.attack_anim_timer = 0
        self.load_animations()

    def gain_xp(self, amount, game=None):
        """Gain XP and level up if threshold reached"""
        self.xp += amount
        self.total_xp += amount

        if game:
            game.floating_texts.append(FloatingText(
                self.pixel_x + self.tile_w // 2,
                self.pixel_y - 20,
                f"+{amount} XP",
                (255, 255, 0)
            ))

        # Check for level up
        while self.xp >= self.xp_to_next_level:
            self.level_up(game)

    def level_up(self, game=None):
        """Level up and increase stats"""
        self.xp -= self.xp_to_next_level
        self.level += 1

        # Calculate new XP requirement
        self.xp_to_next_level = int(100 * (1.5 ** (self.level - 1)))

        # Increase stats
        old_max_health = self.max_health
        old_max_stamina = self.max_stamina

        # Health increases by 15 per level
        self.max_health = self.base_max_health + (self.level - 1) * 15
        # Stamina increases by 10 per level
        self.max_stamina = self.base_max_stamina + (self.level - 1) * 10
        # Damage increases by 5 per level
        self.attack_damage = self.base_attack_damage + (self.level - 1) * 5
        # Crit chance increases by 2% per level
        self.crit_chance = min(
            0.75, self.base_crit_chance + (self.level - 1) * 0.02)

        # Heal to full on level up
        health_gained = self.max_health - old_max_health
        stamina_gained = self.max_stamina - old_max_stamina
        self.health = self.max_health
        self.stamina = self.max_stamina

        if game:
            game.message = f"LEVEL UP! Now Level {self.level}"
            game.message_timer = 120
            game.floating_texts.append(FloatingText(
                self.pixel_x + self.tile_w // 2,
                self.pixel_y - 40,
                f"LEVEL {self.level}!",
                (0, 255, 255)
            ))
            # Play level up sound if available
            game.play_sound('level_up')

        print(f"Level Up! Now Level {self.level}")
        print(f"  Max Health: {self.max_health} (+{health_gained})")
        print(f"  Max Stamina: {self.max_stamina} (+{stamina_gained})")
        print(f"  Attack Damage: {self.attack_damage}")
        print(f"  Crit Chance: {int(self.crit_chance * 100)}%")

    def load_animations(self):
        base = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'image')
        sizes = (max(1, self.render_w), max(1, self.render_h))

        def load_folder(name):
            path = os.path.join(base, name)
            frames = []
            try:
                if os.path.isdir(path):
                    files = sorted([f for f in os.listdir(
                        path) if f.lower().endswith(('.png', '.jpg', '.bmp'))])
                    for fn in files:
                        try:
                            img = pygame.image.load(
                                os.path.join(path, fn)).convert_alpha()
                            img = pygame.transform.scale(img, sizes)
                            frames.append(img)
                        except Exception:
                            pass
            except Exception:
                pass
            if not frames:
                placeholder = pygame.Surface(sizes, pygame.SRCALPHA)
                pygame.draw.rect(placeholder, (100, 150, 255),
                                 (0, 0, sizes[0], sizes[1]))
                frames = [placeholder]
            return frames

        self.animations['idle'] = load_folder('idle')
        self.animations['walking'] = load_folder('walking')
        self.animations['attacking'] = load_folder('attacking')
        self.animations['dying'] = load_folder('dying')

    def set_tile_size(self, tile_w, tile_h):
        self.tile_w = tile_w
        self.tile_h = tile_h
        self.render_w = int(tile_w * self.size_multiplier)
        self.render_h = int(tile_h * self.size_multiplier)
        self.load_animations()

    def shoot_projectile(self, target_x, target_y):
        if self.stamina >= self.attack_cost and self.attack_cooldown == 0 and self.state != State.DEAD:
            self.stamina -= self.attack_cost
            self.attack_cooldown = 30

            is_crit = random.random() < self.crit_chance
            damage = self.attack_damage * self.crit_multiplier if is_crit else self.attack_damage

            center_x = self.pixel_x + self.tile_w // 2
            center_y = self.pixel_y + self.tile_h // 2

            return Projectile(center_x, center_y, target_x, target_y, damage, is_enemy=False), is_crit
        return None, False

    def attack(self, enemies):
        if self.stamina >= self.attack_cost and self.attack_cooldown == 0 and self.state != State.DEAD:
            self.stamina -= self.attack_cost
            self.attack_cooldown = 30
            self.state = State.ATTACKING
            self.attack_anim_timer = len(
                self.animations.get('attacking', [])) * 6

            hit_any = False
            for enemy in enemies:
                if enemy.state != State.DEAD:
                    distance = ((self.pixel_x - enemy.pixel_x) **
                                2 + (self.pixel_y - enemy.pixel_y)**2)**0.5
                    if distance <= self.attack_range:
                        is_crit = random.random() < self.crit_chance
                        damage = self.attack_damage * self.crit_multiplier if is_crit else self.attack_damage
                        enemy.take_damage(damage, is_crit)
                        hit_any = True
            return hit_any
        return False

    def take_damage(self, damage):
        if self.state != State.DEAD:
            self.health -= damage
            self.hit_flash = 10
            if self.health <= 0:
                self.health = 0
                self.state = State.DEAD
                return True
            else:
                self.state = State.HURT
            return False

    def update_combat(self):
        if self.state != State.ATTACKING:
            self.stamina = min(
                self.max_stamina, self.stamina + self.stamina_regen)
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.hit_flash > 0:
            self.hit_flash -= 1
        if self.state == State.HURT and self.hit_flash == 0:
            self.state = State.IDLE
        if getattr(self, 'attack_anim_timer', 0) > 0:
            self.attack_anim_timer -= 1
            if self.attack_anim_timer <= 0:
                if self.state == State.ATTACKING:
                    self.state = State.IDLE

    def handle_input(self, keys, collision_rects, map_width, map_height):
        moving = False
        if self.state != State.DEAD:
            current_speed = self.run_speed if (
                keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) else self.speed
            dx = dy = 0

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

            if dx != 0 and dy != 0:
                dx *= 0.707
                dy *= 0.707

            new_rect = pygame.Rect(
                self.pixel_x+dx, self.pixel_y+dy, self.tile_w, self.tile_h)
            if not any(new_rect.colliderect(r) for r in collision_rects):
                if 0 <= new_rect.x <= map_width*self.tile_w - self.tile_w and 0 <= new_rect.y <= map_height*self.tile_h - self.tile_h:
                    self.pixel_x += dx
                    self.pixel_y += dy

        if self.state == State.DEAD:
            anim_key = 'dying'
        elif self.state == State.ATTACKING:
            anim_key = 'attacking'
        elif moving:
            anim_key = 'walking'
        else:
            anim_key = 'idle'

        if not hasattr(self, 'current_anim_key') or self.current_anim_key != anim_key:
            self.current_anim_key = anim_key
            self.frame_index = 0
            self.animation_counter = 0.0

        frames = self.animations.get(self.current_anim_key, [])
        if frames:
            if self.state == State.DEAD:
                if self.frame_index < len(frames) - 1:
                    self.animation_counter += self.animation_speed
                    if self.animation_counter >= 1.0:
                        self.animation_counter = 0.0
                        self.frame_index += 1
            else:
                self.animation_counter += self.animation_speed
                if self.animation_counter >= 1.0:
                    self.animation_counter = 0.0
                    self.frame_index = (self.frame_index + 1) % len(frames)
        else:
            self.frame_index = 0
            self.animation_counter = 0.0

    def draw(self, surface, camera_x, camera_y):
        anim_key = getattr(self, 'current_anim_key', 'idle')
        frames = self.animations.get(anim_key, [])
        if not frames:
            img = pygame.Surface(
                (self.render_w, self.render_h), pygame.SRCALPHA)
            pygame.draw.rect(img, (100, 150, 255),
                             (0, 0, self.render_w, self.render_h))
        else:
            idx = max(0, min(self.frame_index, len(frames)-1))
            img = frames[idx]

        if self.current_direction == 'left':
            img = pygame.transform.flip(img, True, False)

        if self.hit_flash > 0:
            flash_img = img.copy()
            flash_img.fill((255, 255, 255, 100),
                           special_flags=pygame.BLEND_RGB_ADD)
            surface.blit(flash_img, (self.pixel_x -
                         camera_x, self.pixel_y - camera_y))
        else:
            surface.blit(img, (self.pixel_x - camera_x,
                         self.pixel_y - camera_y))


class Slime:
    def __init__(self, x, y, tile_w, tile_h, slime_type='red_slime'):
        self.tile_w = tile_w
        self.tile_h = tile_h
        self.size_multiplier = 2.0
        self.render_w = int(tile_w * self.size_multiplier)
        self.render_h = int(tile_h * self.size_multiplier)
        self.pixel_x = x
        self.pixel_y = y
        self.slime_type = slime_type

        if slime_type == 'blue_slime':
            self.max_health = 50
            self.speed = 1.5
            self.attack_damage = 5
            self.attack_range = 60
        elif slime_type == 'yellow_slime':
            self.max_health = 60
            self.speed = 1.0
            self.attack_damage = 7
            self.attack_range = 70
        else:  # red_slime
            self.max_health = 55
            self.speed = 1.3
            self.attack_damage = 6
            self.attack_range = 65

        self.health = self.max_health
        self.attack_cooldown = 0
        self.state = State.IDLE
        self.hit_flash = 0
        self.detection_range = 200
        self.wander_timer = 0
        self.wander_direction = [0, 0]
        self.frame_index = 0
        self.animation_counter = 0.0
        self.animation_speed = 0.15

        self.load_animations()

    def load_animations(self):
        base = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'image')
        self.idle_frames = []
        self.attack_frames = []

        # Load idle frames
        for i in range(2):
            try:
                if i == 0:
                    path = os.path.join(base, f'{self.slime_type}_idle.png')
                else:
                    path = os.path.join(base, f'{self.slime_type}_idle{i}.png')
                if os.path.exists(path):
                    img = pygame.image.load(path).convert_alpha()
                    img = pygame.transform.scale(
                        img, (self.render_w, self.render_h))
                    self.idle_frames.append(img)
            except Exception as e:
                print(f"Could not load {path}: {e}")

        # Load attack frames
        for i in range(7):
            try:
                if i == 0:
                    path = os.path.join(base, f'{self.slime_type}_attack.png')
                else:
                    path = os.path.join(
                        base, f'{self.slime_type}_attack{i}.png')
                if os.path.exists(path):
                    img = pygame.image.load(path).convert_alpha()
                    img = pygame.transform.scale(
                        img, (self.render_w, self.render_h))
                    self.attack_frames.append(img)
            except Exception as e:
                print(f"Could not load {path}: {e}")

        # Fallback if no frames loaded
        if not self.idle_frames:
            placeholder = pygame.Surface(
                (self.render_w, self.render_h), pygame.SRCALPHA)
            if 'blue' in self.slime_type:
                pygame.draw.circle(placeholder, (100, 100, 255),
                                   (self.render_w//2, self.render_h//2), self.render_w//3)
            elif 'yellow' in self.slime_type:
                pygame.draw.circle(placeholder, (255, 255, 100),
                                   (self.render_w//2, self.render_h//2), self.render_w//3)
            else:
                pygame.draw.circle(placeholder, (255, 100, 100),
                                   (self.render_w//2, self.render_h//2), self.render_w//3)
            self.idle_frames = [placeholder]
            self.attack_frames = [placeholder]

    def take_damage(self, damage, is_crit=False):
        if self.state != State.DEAD:
            self.health -= damage
            self.hit_flash = 10
            self.is_crit = is_crit
            if self.health <= 0:
                self.health = 0
                self.state = State.DEAD
                # Grant XP on death
                xp_reward = 20 + (self.max_health // 10)  # More HP = more XP
                return True, xp_reward
            else:
                self.state = State.HURT
            return False, 0

    def update(self, player, collision_rects, map_width, map_height, game=None):
        if self.state == State.DEAD:
            return

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.hit_flash > 0:
            self.hit_flash -= 1
        if self.state == State.HURT and self.hit_flash == 0:
            self.state = State.IDLE

        distance = ((self.pixel_x - player.pixel_x)**2 +
                    (self.pixel_y - player.pixel_y)**2)**0.5

        if distance <= self.detection_range and player.state != State.DEAD:
            dx = player.pixel_x - self.pixel_x
            dy = player.pixel_y - self.pixel_y
            length = (dx**2 + dy**2)**0.5

            if length > 0:
                dx = (dx / length) * self.speed
                dy = (dy / length) * self.speed
                new_rect = pygame.Rect(
                    self.pixel_x + dx, self.pixel_y + dy, self.tile_w, self.tile_h)
                if not any(new_rect.colliderect(r) for r in collision_rects):
                    self.pixel_x += dx
                    self.pixel_y += dy

            if distance <= self.attack_range and self.attack_cooldown == 0:
                player.take_damage(self.attack_damage)
                if game:
                    game.play_sound('taking_damage')
                self.attack_cooldown = 60
                self.state = State.ATTACKING
        else:
            if self.wander_timer <= 0:
                self.wander_timer = random.randint(60, 180)
                self.wander_direction = [
                    random.uniform(-1, 1), random.uniform(-1, 1)]
            else:
                self.wander_timer -= 1
                dx = self.wander_direction[0] * self.speed * 0.5
                dy = self.wander_direction[1] * self.speed * 0.5
                new_rect = pygame.Rect(
                    self.pixel_x + dx, self.pixel_y + dy, self.tile_w, self.tile_h)
                if not any(new_rect.colliderect(r) for r in collision_rects):
                    if 0 <= new_rect.x <= map_width*self.tile_w and 0 <= new_rect.y <= map_height*self.tile_h:
                        self.pixel_x += dx
                        self.pixel_y += dy

        # Update animation
        frames = self.attack_frames if self.state == State.ATTACKING else self.idle_frames
        if frames:
            self.animation_counter += self.animation_speed
            if self.animation_counter >= 1.0:
                self.animation_counter = 0.0
                if self.state == State.ATTACKING:
                    self.frame_index += 1
                    if self.frame_index >= len(self.attack_frames):
                        self.frame_index = 0
                        self.state = State.IDLE
                else:
                    self.frame_index = (self.frame_index + 1) % len(frames)

    def draw(self, surface, camera_x, camera_y):
        frames = self.attack_frames if self.state == State.ATTACKING else self.idle_frames
        if frames:
            idx = max(0, min(self.frame_index, len(frames)-1))
            img = frames[idx].copy()
        else:
            img = pygame.Surface(
                (self.render_w, self.render_h), pygame.SRCALPHA)

        if self.hit_flash > 0:
            img.fill((255, 255, 255, 100), special_flags=pygame.BLEND_RGB_ADD)
        if self.state == State.DEAD:
            img.set_alpha(100)
        surface.blit(img, (self.pixel_x - camera_x, self.pixel_y - camera_y))

        if self.state != State.DEAD:
            bar_width = self.render_w
            bar_height = 5
            bar_x = self.pixel_x - camera_x
            bar_y = self.pixel_y - camera_y - 10
            pygame.draw.rect(surface, (100, 0, 0),
                             (bar_x, bar_y, bar_width, bar_height))
            health_width = int((self.health / self.max_health) * bar_width)
            pygame.draw.rect(surface, (0, 255, 0),
                             (bar_x, bar_y, health_width, bar_height))


class Tower:
    """Stationary tower that shoots projectiles from the top"""

    def __init__(self, x, y, tile_w, tile_h, tower_type='fire'):
        self.tile_w = tile_w
        self.tile_h = tile_h
        self.size_multiplier = 3.0
        self.render_w = int(tile_w * self.size_multiplier)
        self.render_h = int(tile_h * self.size_multiplier)
        self.pixel_x = x
        self.pixel_y = y
        self.tower_type = tower_type

        # Different tower types with different stats
        if tower_type == 'fire':
            self.max_health = 100
            self.attack_damage = 12
            self.shoot_interval = 90
            self.detection_range = 400
        elif tower_type == 'water':
            self.max_health = 120
            self.attack_damage = 10
            self.shoot_interval = 100
            self.detection_range = 450
        elif tower_type == 'void':
            self.max_health = 80
            self.attack_damage = 15
            self.shoot_interval = 80
            self.detection_range = 380
        elif tower_type == 'ice':
            self.max_health = 110
            self.attack_damage = 11
            self.shoot_interval = 95
            self.detection_range = 420
        elif tower_type == 'lightning':
            self.max_health = 90
            self.attack_damage = 14
            self.shoot_interval = 75
            self.detection_range = 400
        elif tower_type == 'holy':
            self.max_health = 130
            self.attack_damage = 13
            self.shoot_interval = 110
            self.detection_range = 500
        else:
            self.max_health = 100
            self.attack_damage = 10
            self.shoot_interval = 100
            self.detection_range = 400

        self.health = self.max_health
        self.state = State.IDLE
        self.hit_flash = 0
        self.shoot_cooldown = 0

        self.load_image()

    def load_image(self):
        try:
            img_path = os.path.join(os.path.dirname(os.path.abspath(
                __file__)), 'image', f'tower_{self.tower_type}.png')
            if os.path.exists(img_path):
                self.image = pygame.image.load(img_path).convert_alpha()
                self.image = pygame.transform.scale(
                    self.image, (self.render_w, self.render_h))
                print(f"Loaded tower image: tower_{self.tower_type}.png")
            else:
                # Fallback with color coding
                self.image = pygame.Surface(
                    (self.render_w, self.render_h), pygame.SRCALPHA)
                if self.tower_type == 'fire':
                    color = (255, 100, 0)
                elif self.tower_type == 'water':
                    color = (0, 100, 255)
                elif self.tower_type == 'void':
                    color = (100, 0, 150)
                elif self.tower_type == 'ice':
                    color = (150, 200, 255)
                elif self.tower_type == 'lightning':
                    color = (255, 255, 100)
                elif self.tower_type == 'holy':
                    color = (255, 255, 200)
                else:
                    color = (150, 150, 150)

                # Draw tower base
                pygame.draw.rect(
                    self.image, color, (10, self.render_h//2, self.render_w-20, self.render_h//2-10))
                # Draw tower top (cannon/turret)
                pygame.draw.circle(self.image, (200, 200, 200),
                                   (self.render_w//2, self.render_h//3), 15)
                # Draw tower detail
                pygame.draw.rect(self.image, (80, 80, 80),
                                 (self.render_w//2-5, self.render_h//3-20, 10, 20))
                print(f"Created fallback tower graphics for {self.tower_type}")
        except Exception as e:
            print(f"Error loading tower image: {e}")
            self.image = pygame.Surface(
                (self.render_w, self.render_h), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (150, 150, 150),
                             (10, 10, self.render_w-20, self.render_h-20))

    def take_damage(self, damage, is_crit=False):
        if self.state != State.DEAD:
            self.health -= damage
            self.hit_flash = 10
            self.is_crit = is_crit
            if self.health <= 0:
                self.health = 0
                self.state = State.DEAD
                # Boss gives more XP
                xp_reward = 100
                return True, xp_reward
            else:
                self.state = State.HURT
            return False, 0

    def update(self, player):
        if self.state == State.DEAD:
            return None

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.hit_flash > 0:
            self.hit_flash -= 1
        if self.state == State.HURT and self.hit_flash == 0:
            self.state = State.IDLE

        distance = ((self.pixel_x - player.pixel_x)**2 +
                    (self.pixel_y - player.pixel_y)**2)**0.5

        if distance <= self.detection_range and self.shoot_cooldown == 0 and player.state != State.DEAD:
            self.shoot_cooldown = self.shoot_interval
            # Shoot from the top center of the tower
            center_x = self.pixel_x + self.render_w // 2
            center_y = self.pixel_y + self.render_h // 4  # Shoot from top quarter of tower
            target_x = player.pixel_x + player.tile_w // 2
            target_y = player.pixel_y + player.tile_h // 2
            return Projectile(center_x, center_y, target_x, target_y, self.attack_damage,
                              is_enemy=True, projectile_type=self.tower_type)

        return None

    def draw(self, surface, camera_x, camera_y):
        img = self.image.copy()
        if self.hit_flash > 0:
            img.fill((255, 255, 255, 100), special_flags=pygame.BLEND_RGB_ADD)
        if self.state == State.DEAD:
            img.set_alpha(100)
        surface.blit(img, (self.pixel_x - camera_x, self.pixel_y - camera_y))

        if self.state != State.DEAD:
            bar_width = self.render_w
            bar_height = 6
            bar_x = self.pixel_x - camera_x
            bar_y = self.pixel_y - camera_y - 12
            pygame.draw.rect(surface, (100, 0, 0),
                             (bar_x, bar_y, bar_width, bar_height))
            health_width = int((self.health / self.max_health) * bar_width)
            pygame.draw.rect(surface, (255, 0, 0),
                             (bar_x, bar_y, health_width, bar_height))


class Boss:
    def __init__(self, x, y, tile_w, tile_h):
        self.tile_w = tile_w
        self.tile_h = tile_h
        self.size_multiplier = 4.0
        self.render_w = int(tile_w * self.size_multiplier)
        self.render_h = int(tile_h * self.size_multiplier)
        self.pixel_x = x
        self.pixel_y = y

        self.max_health = 200
        self.health = 200
        self.attack_damage = 15
        self.state = State.IDLE
        self.hit_flash = 0
        self.shoot_cooldown = 0
        self.shoot_interval = 120
        self.detection_range = 400

        self.load_image()

    def load_image(self):
        try:
            self.image = pygame.Surface(
                (self.render_w, self.render_h), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (150, 0, 150),
                             (0, 0, self.render_w, self.render_h))
            pygame.draw.circle(self.image, (200, 0, 200),
                               (self.render_w//2, self.render_h//2), 40)
        except:
            self.image = pygame.Surface(
                (self.render_w, self.render_h), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (150, 0, 150),
                             (0, 0, self.render_w, self.render_h))

    def take_damage(self, damage, is_crit=False):
        if self.state != State.DEAD:
            self.health -= damage
            self.hit_flash = 10
            self.is_crit = is_crit
            if self.health <= 0:
                self.health = 0
                self.state = State.DEAD
                # Tower gives XP
                xp_reward = 50
                return True, xp_reward
            else:
                self.state = State.HURT
            return False, 0

    def update(self, player):
        if self.state == State.DEAD:
            return None

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.hit_flash > 0:
            self.hit_flash -= 1
        if self.state == State.HURT and self.hit_flash == 0:
            self.state = State.IDLE

        distance = ((self.pixel_x - player.pixel_x)**2 +
                    (self.pixel_y - player.pixel_y)**2)**0.5

        if distance <= self.detection_range and self.shoot_cooldown == 0 and player.state != State.DEAD:
            self.shoot_cooldown = self.shoot_interval
            center_x = self.pixel_x + self.render_w // 2
            center_y = self.pixel_y + self.render_h // 2
            target_x = player.pixel_x + player.tile_w // 2
            target_y = player.pixel_y + player.tile_h // 2
            return Projectile(center_x, center_y, target_x, target_y, self.attack_damage,
                              is_enemy=True, projectile_type='void')

        return None

    def draw(self, surface, camera_x, camera_y):
        img = self.image.copy()
        if self.hit_flash > 0:
            img.fill((255, 255, 255, 100), special_flags=pygame.BLEND_RGB_ADD)
        if self.state == State.DEAD:
            img.set_alpha(100)
        surface.blit(img, (self.pixel_x - camera_x, self.pixel_y - camera_y))

        if self.state != State.DEAD:
            bar_width = self.render_w
            bar_height = 8
            bar_x = self.pixel_x - camera_x
            bar_y = self.pixel_y - camera_y - 15
            pygame.draw.rect(surface, (100, 0, 0),
                             (bar_x, bar_y, bar_width, bar_height))
            health_width = int((self.health / self.max_health) * bar_width)
            pygame.draw.rect(surface, (255, 0, 0),
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
        self.current_map_file = tmx_file  # Store for tower building
        try:
            self.tmx_data = load_pygame(tmx_file)
        except Exception as e:
            print(f"Error loading TMX file: {e}")
            print("Attempting to auto-fix tileset source paths...")

            import xml.etree.ElementTree as ET

            tmx_dir = os.path.dirname(os.path.abspath(tmx_file))
            tree = ET.parse(tmx_file)
            root = tree.getroot()
            changed = False

            for tileset in root.findall('tileset'):
                src = tileset.get('source')
                if src:
                    base = os.path.basename(src)
                    candidate = os.path.join(tmx_dir, base)
                    if os.path.exists(candidate):
                        tileset.set('source', candidate)
                        changed = True
                    else:
                        placeholder_tsx = candidate
                        placeholder_img = os.path.join(
                            tmx_dir, base.replace('.tsx', '.png'))
                        try:
                            if not os.path.exists(placeholder_img):
                                try:
                                    from PIL import Image
                                    Image.new('RGBA', (32, 32), (0, 0, 0, 0)).save(
                                        placeholder_img)
                                except Exception:
                                    with open(placeholder_img, 'wb') as f:
                                        f.write(b'\x89PNG\r\n\x1a\n')

                            with open(placeholder_tsx, 'w', encoding='utf-8') as f:
                                f.write(
                                    '<?xml version="1.0" encoding="UTF-8"?>\n')
                                f.write(
                                    f'<tileset version="1.10" tiledversion="1.11.2" name="{base.replace(".tsx", "")}" tilewidth="32" tileheight="32" tilecount="1" columns="1">\n')
                                f.write(
                                    f' <image source="{os.path.basename(placeholder_img)}" width="32" height="32"/>\n')
                                f.write('</tileset>\n')

                            tileset.set('source', placeholder_tsx)
                            changed = True
                            print(
                                f"Created placeholder tileset: {placeholder_tsx}")
                        except Exception:
                            pass

            for tileset in root.findall('tileset'):
                img_elem = tileset.find('image')
                if img_elem is not None:
                    img_src = img_elem.get('source')
                    if img_src:
                        img_base = os.path.basename(img_src)
                        img_candidate = os.path.join(tmx_dir, img_base)
                        if os.path.exists(img_candidate):
                            img_elem.set('source', img_candidate)
                            changed = True
                        else:
                            try:
                                placeholder_path = img_candidate
                                if not os.path.exists(placeholder_path):
                                    try:
                                        from PIL import Image
                                        Image.new('RGBA', (32, 32), (0, 0, 0, 0)).save(
                                            placeholder_path)
                                        print(
                                            f"Created placeholder image: {placeholder_path}")
                                    except Exception:
                                        with open(placeholder_path, 'wb') as f:
                                            f.write(b'\x89PNG\r\n\x1a\n')
                                img_elem.set('source', placeholder_path)
                                changed = True
                            except Exception:
                                pass

            if changed:
                fixed_path = os.path.join(tmx_dir, os.path.basename(
                    tmx_file).replace('.tmx', '_fixed.tmx'))
                tree.write(fixed_path, encoding='utf-8', xml_declaration=True)
                print(f"Wrote fixed TMX to: {fixed_path}")

                for tileset in root.findall('tileset'):
                    src = tileset.get('source')
                    if not src:
                        continue
                    tsx_path = src
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
                                if os.path.exists(img_candidate):
                                    img.set('source', img_candidate)
                                    ts_tree.write(
                                        tsx_path, encoding='utf-8', xml_declaration=True)
                                else:
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
                        pass

                try:
                    self.tmx_data = load_pygame(fixed_path)
                except Exception as load_err:
                    print("Auto-fix failed when loading the fixed TMX:", load_err)
                    raise
            else:
                print("No local tileset files found to fix the TMX.\nMake sure your .tsx files are next to the .tmx or adjust paths in the TMX.")
                raise

        self.tile_w = self.tmx_data.tilewidth
        self.tile_h = self.tmx_data.tileheight
        self.width = self.tmx_data.width
        self.height = self.tmx_data.height
        self.collision_rects = self.build_collision_rects()
        self.teleports = self.build_teleports()
        self.bosses = self.build_bosses()
        self.towers = self.build_towers()
        self.npcs = self.build_npcs()

    def build_collision_rects(self):
        rects = []
        layers = list(self.tmx_data.visible_layers)

        if layers:
            bottom_layer = layers[0]
            if isinstance(bottom_layer, pytmx.TiledTileLayer):
                if bottom_layer.properties.get("blocked") or bottom_layer.name.lower() == "collision":
                    for x, y, gid in bottom_layer.tiles():
                        if gid != 0:
                            rects.append(pygame.Rect(x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight,
                                                     self.tmx_data.tilewidth, self.tmx_data.tileheight))
                    return rects

        try:
            collision_layer = self.tmx_data.get_layer_by_name("collision")
            if collision_layer and collision_layer.properties.get("blocked"):
                for x, y, gid in collision_layer.tiles():
                    if gid != 0:
                        rects.append(pygame.Rect(x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight,
                                                 self.tmx_data.tilewidth, self.tmx_data.tileheight))
        except Exception as e:
            print(f"Warning: Could not load collision layer: {e}")

        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                if layer.properties.get("blocked"):
                    for x, y, gid in layer.tiles():
                        if gid != 0:
                            rects.append(pygame.Rect(x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight,
                                                     self.tmx_data.tilewidth, self.tmx_data.tileheight))
        return rects

    def build_teleports(self):
        teleports = []
        try:
            for obj in getattr(self.tmx_data, 'objects', []):
                obj_type = getattr(obj, 'type', '') or getattr(obj, 'name', '')
                if str(obj_type).lower() == 'teleport':
                    props = getattr(obj, 'properties', {}) or {}
                    dest = props.get('dest') or props.get(
                        'map') or props.get('destination')
                    dest_x = props.get('dest_x')
                    dest_y = props.get('dest_y')
                    rect = pygame.Rect(int(obj.x), int(obj.y), int(getattr(obj, 'width', 0) or 1),
                                       int(getattr(obj, 'height', 0) or 1))
                    teleports.append(
                        {'rect': rect, 'dest': dest, 'dest_x': dest_x, 'dest_y': dest_y, 'obj': obj})
        except Exception:
            pass
        return teleports

    def build_bosses(self):
        bosses = []
        try:
            for obj in getattr(self.tmx_data, 'objects', []):
                obj_type = getattr(obj, 'type', '') or getattr(obj, 'name', '')
                if str(obj_type).lower() == 'boss':
                    boss = Boss(int(obj.x), int(obj.y),
                                self.tile_w, self.tile_h)
                    bosses.append(boss)
                    print(f"Found boss at ({obj.x}, {obj.y})")
        except Exception as e:
            print(f"Error loading bosses: {e}")
        return bosses

    def build_towers(self):
        """Build towers by scanning for tower images in the image folder and placing them on the map"""
        towers = []
        image_dir = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'image')

        # Check what tower images are available
        available_towers = []
        tower_types = ['fire', 'water', 'void', 'ice', 'lightning', 'holy']

        for tower_type in tower_types:
            tower_img_path = os.path.join(image_dir, f'tower_{tower_type}.png')
            if os.path.exists(tower_img_path):
                available_towers.append(tower_type)
                print(f"Found tower image: tower_{tower_type}.png")

        # Get current map name to determine which towers to spawn
        try:
            # Scan the map for suitable tower locations (open spaces)
            # We'll place towers strategically around the map
            map_name = os.path.basename(
                getattr(self, 'current_map_file', '')).lower()

            # Different maps get different tower configurations
            if 'winter' in map_name or 'boss' in map_name:
                # Boss rooms get multiple towers
                tower_configs = [
                    {'x': 5, 'y': 5, 'type': 'ice'},
                    {'x': self.width - 8, 'y': 5, 'type': 'ice'},
                    {'x': 5, 'y': self.height - 8, 'type': 'water'},
                    {'x': self.width - 8, 'y': self.height - 8, 'type': 'water'},
                ]
            elif 'angel' in map_name:
                tower_configs = [
                    {'x': self.width // 2 - 3, 'y': 5, 'type': 'holy'},
                    {'x': 5, 'y': self.height // 2, 'type': 'holy'},
                    {'x': self.width - 8, 'y': self.height // 2, 'type': 'holy'},
                ]
            elif 'fire' in map_name or 'lava' in map_name:
                tower_configs = [
                    {'x': 7, 'y': 7, 'type': 'fire'},
                    {'x': self.width - 10, 'y': 7, 'type': 'fire'},
                    {'x': self.width // 2, 'y': self.height - 10, 'type': 'void'},
                ]
            else:
                # Default configuration for other maps
                tower_configs = [
                    {'x': 10, 'y': 10, 'type': 'fire'},
                    {'x': self.width - 13, 'y': 10, 'type': 'water'},
                ]

            # Create towers if the type is available
            for config in tower_configs:
                tower_type = config['type']
                if tower_type in available_towers or True:  # Always try to create towers
                    x_pixel = config['x'] * self.tile_w
                    y_pixel = config['y'] * self.tile_h

                    # Check if location is not in collision
                    test_rect = pygame.Rect(
                        x_pixel, y_pixel, self.tile_w * 3, self.tile_h * 3)
                    if not any(test_rect.colliderect(r) for r in self.collision_rects):
                        tower = Tower(x_pixel, y_pixel, self.tile_w,
                                      self.tile_h, tower_type)
                        towers.append(tower)
                        print(
                            f"Spawned {tower_type} tower at ({x_pixel}, {y_pixel})")

        except Exception as e:
            print(f"Error building towers: {e}")

        return towers

    def build_npcs(self):
        npcs = []
        try:
            for obj in getattr(self.tmx_data, 'objects', []):
                obj_type = getattr(obj, 'type', '') or getattr(obj, 'name', '')
                obj_type_lower = str(obj_type).lower()

                # Check if it's an NPC object
                if 'npc' in obj_type_lower or 'barman' in obj_type_lower or 'merchant' in obj_type_lower:
                    # Get custom dialogues from properties if available
                    props = getattr(obj, 'properties', {}) or {}
                    custom_dialogues = []

                    # Check for dialogue properties (dialogue1, dialogue2, etc.)
                    i = 1
                    while True:
                        dialogue_key = f'dialogue{i}'
                        if dialogue_key in props:
                            custom_dialogues.append(props[dialogue_key])
                            i += 1
                        else:
                            break

                    # Determine NPC name
                    npc_name = 'barman'  # default
                    if 'barman' in obj_type_lower:
                        npc_name = 'barman'
                    elif 'merchant' in obj_type_lower:
                        npc_name = 'merchant'
                    else:
                        npc_name = obj_type

                    npc = NPC(int(obj.x), int(obj.y), self.tile_w, self.tile_h,
                              npc_name, custom_dialogues if custom_dialogues else None)
                    npcs.append(npc)
                    print(f"Found NPC '{npc_name}' at ({obj.x}, {obj.y})")
        except Exception as e:
            print(f"Error loading NPCs: {e}")
        return npcs

    def draw(self, surface, camera_x, camera_y):
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, image in layer.tiles():
                    if image:
                        surface.blit(
                            image, (x*self.tile_w - camera_x, y*self.tile_h - camera_y))


def draw_ui_bar(surface, x, y, w, h, value, max_value, color, bg_color, label):
    font = pygame.font.Font(None, 20)
    label_surf = font.render(label, True, (255, 255, 255))
    surface.blit(label_surf, (x, y - 18))
    pygame.draw.rect(surface, bg_color, (x, y, w, h))
    fill_w = int((value / max_value) * w)
    pygame.draw.rect(surface, color, (x, y, fill_w, h))
    pygame.draw.rect(surface, (0, 0, 0), (x, y, w, h), 2)
    text = font.render(f"{int(value)}/{int(max_value)}", True, (255, 255, 255))
    text_rect = text.get_rect(center=(x + w//2, y + h//2))
    surface.blit(text, text_rect)


def spawn_slimes_randomly(map_obj, count=5):
    """Spawn slimes in random non-collision areas"""
    slimes = []
    collision_rects = map_obj.collision_rects

    for _ in range(count):
        slime_type = random.choice(['red_slime', 'blue_slime', 'yellow_slime'])
        max_attempts = 50

        for attempt in range(max_attempts):
            x = random.randint(5, map_obj.width - 5) * map_obj.tile_w
            y = random.randint(5, map_obj.height - 5) * map_obj.tile_h

            test_rect = pygame.Rect(
                x, y, map_obj.tile_w * 2, map_obj.tile_h * 2)
            if not any(test_rect.colliderect(r) for r in collision_rects):
                slime = Slime(x, y, map_obj.tile_w, map_obj.tile_h, slime_type)
                slimes.append(slime)
                break

    return slimes


class Game:
    def __init__(self, tmx_file, fullscreen=True):
        pygame.init()
        pygame.mixer.init()

        # Load sound effects
        self.sounds = {}
        self.load_sounds()

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

        pygame.display.set_caption(
            "Medieval RPG - Click to Shoot, SPACE to Attack/Continue, E to Interact")
        self.clock = pygame.time.Clock()
        self.running = True

        self.game_map = GameMap(tmx_file)
        self.current_map = tmx_file
        self.debug_draw_teleports = False

        self.player = Player(166, 57, self.game_map.tile_w,
                             self.game_map.tile_h)

        self.teleport_cooldown = 0
        self.teleport_marker_rect = None
        self.teleport_marker_timer = 0
        self.teleport_marker_duration = 300

        # Spawn slimes
        self.slimes = spawn_slimes_randomly(self.game_map, count=8)

        self.bosses = self.game_map.bosses
        self.towers = self.game_map.towers
        self.npcs = self.game_map.npcs

        self.projectiles = []
        self.floating_texts = []

        self.camera = Camera(self.screen_width, self.screen_height,
                             self.game_map.width * self.game_map.tile_w,
                             self.game_map.height * self.game_map.tile_h)

        self.font = pygame.font.Font(None, 24)
        self.message = ""
        self.message_timer = 0

        self.dialogue = DialogueSystem()

        self.current_music = None
        self.load_music(tmx_file)

        self.nearby_npc = None

        self.start_intro_dialogue()

    def start_intro_dialogue(self):
        intro_dialogues = [
            "Welcome, brave warrior! Your journey begins here.",
            "The realm is in great danger. Dark forces threaten our land.",
            "You must defeat the monsters and face the powerful bosses.",
            "Press SPACE to attack nearby enemies, or click to shoot projectiles.",
            "Press E to interact with NPCs and teleport.",
            "Collect your strength and prepare for battle!",
            "Good luck, hero. The fate of the realm rests in your hands."
        ]
        self.dialogue.start_dialogue(intro_dialogues)

    def load_sounds(self):
        """Load all sound effects"""
        sound_names = ['projectile', 'attacking',
                       'dying', 'taking_damage', 'level_up']
        sound_dir = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'sound')

        # Create sound directory if it doesn't exist
        if not os.path.exists(sound_dir):
            try:
                os.makedirs(sound_dir)
                print(f"Created sound directory: {sound_dir}")
            except Exception as e:
                print(f"Could not create sound directory: {e}")

        for sound_name in sound_names:
            try:
                sound_path = os.path.join(sound_dir, f'{sound_name}.wav')
                if os.path.exists(sound_path):
                    self.sounds[sound_name] = pygame.mixer.Sound(sound_path)
                    self.sounds[sound_name].set_volume(0.5)
                    print(f"Loaded sound: {sound_name}.wav")
                else:
                    # Try .ogg format
                    sound_path_ogg = os.path.join(
                        sound_dir, f'{sound_name}.ogg')
                    if os.path.exists(sound_path_ogg):
                        self.sounds[sound_name] = pygame.mixer.Sound(
                            sound_path_ogg)
                        self.sounds[sound_name].set_volume(0.5)
                        print(f"Loaded sound: {sound_name}.ogg")
                    else:
                        print(
                            f"Sound file not found: {sound_path} or {sound_path_ogg}")
                        self.sounds[sound_name] = None
            except Exception as e:
                print(f"Error loading sound {sound_name}: {e}")
                self.sounds[sound_name] = None

    def play_sound(self, sound_name):
        """Play a sound effect if it exists"""
        if sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].play()
            except Exception as e:
                print(f"Error playing sound {sound_name}: {e}")

    def load_music(self, tmx_file):
        try:
            map_name = os.path.basename(tmx_file).replace('.tmx', '')
            music_path = os.path.join(os.path.dirname(
                os.path.abspath(__file__)), 'music', f'{map_name}.mp3')

            if os.path.exists(music_path) and music_path != self.current_music:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)
                self.current_music = music_path
                print(f"Playing music: {music_path}")
            elif not os.path.exists(music_path):
                print(f"Music file not found: {music_path}")
                generic_music = os.path.join(os.path.dirname(
                    os.path.abspath(__file__)), 'music', 'background.mp3')
                if os.path.exists(generic_music) and generic_music != self.current_music:
                    pygame.mixer.music.load(generic_music)
                    pygame.mixer.music.set_volume(0.5)
                    pygame.mixer.music.play(-1)
                    self.current_music = generic_music
                    print(f"Playing generic music: {generic_music}")
        except Exception as e:
            print(f"Could not load music: {e}")

    def load_map(self, tmx_file, teleport_obj=None):
        try:
            new_map = GameMap(tmx_file)
        except Exception as e:
            self.message = f"Failed to load map: {os.path.basename(tmx_file)}"
            self.message_timer = 60
            print(f"load_map error: {e}")
            return

        self.game_map = new_map
        self.current_map = tmx_file

        try:
            self.player.set_tile_size(
                self.game_map.tile_w, self.game_map.tile_h)
        except Exception:
            pass

        if teleport_obj:
            teleports = getattr(self.game_map, 'teleports', [])
            src_rect = teleport_obj.get('rect')
            next_tp = None

            try:
                src_map = os.path.basename(
                    self.current_map).lower() if self.current_map else ''
            except Exception:
                src_map = ''

            dest_map_name = os.path.basename(tmx_file).lower()
            if src_map == 'home_inn_1.tmx' and dest_map_name == 'main_map.tmx' and len(teleports) >= 2:
                next_tp = teleports[1]
            else:
                if teleports and src_rect is not None:
                    found = None
                    for i, tp in enumerate(teleports):
                        r = tp.get('rect')
                        if r and r.x == src_rect.x and r.y == src_rect.y and r.width == src_rect.width and r.height == src_rect.height:
                            found = i
                            break
                    if found is not None:
                        next_index = (found + 1) % len(teleports)
                        next_tp = teleports[next_index]
                    else:
                        next_tp = teleports[0]
                elif teleports:
                    next_tp = teleports[0]

            if next_tp:
                r = next_tp.get('rect')
                if r:
                    try:
                        self.player.pixel_x = int(r.x)
                        self.player.pixel_y = int(r.y)
                    except Exception:
                        pass

        max_x = max(0, self.game_map.width *
                    self.game_map.tile_w - self.player.tile_w)
        max_y = max(0, self.game_map.height *
                    self.game_map.tile_h - self.player.tile_h)
        self.player.pixel_x = max(0, min(self.player.pixel_x, max_x))
        self.player.pixel_y = max(0, min(self.player.pixel_y, max_y))

        map_name = os.path.basename(tmx_file).lower()
        if map_name != "home_inn_1.tmx":
            self.slimes = spawn_slimes_randomly(self.game_map, count=8)
        else:
            self.slimes = []

        self.bosses = self.game_map.bosses
        self.towers = self.game_map.towers
        self.npcs = self.game_map.npcs

        if teleport_obj is not None:
            heal_amount = 20
            self.player.health = min(
                self.player.max_health, self.player.health + heal_amount)
            self.message = f"Teleported! Health +{heal_amount}"
            self.message_timer = 60

        try:
            self.camera.map_width = self.game_map.width * self.game_map.tile_w
            self.camera.map_height = self.game_map.height * self.game_map.tile_h
        except Exception:
            pass

        self.load_music(tmx_file)

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
        self.teleport_ready = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if not self.dialogue.active:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        world_x = mouse_x + self.camera.x
                        world_y = mouse_y + self.camera.y
                        projectile, is_crit = self.player.shoot_projectile(
                            world_x, world_y)
                        if projectile:
                            self.projectiles.append(projectile)
                            self.play_sound('projectile')
                            if is_crit:
                                self.floating_texts.append(FloatingText(
                                    self.player.pixel_x + self.player.tile_w // 2,
                                    self.player.pixel_y,
                                    "Critical!",
                                    (255, 0, 0)
                                ))
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    self.debug_draw_teleports = not getattr(
                        self, 'debug_draw_teleports', False)
                    print(f"Debug draw teleports: {self.debug_draw_teleports}")
                    return
                if event.key == pygame.K_F11 or (event.key == pygame.K_RETURN and (pygame.key.get_mods() & pygame.KMOD_ALT)):
                    self.toggle_fullscreen()
                elif event.key == pygame.K_ESCAPE:
                    if self.fullscreen:
                        self.toggle_fullscreen()
                    else:
                        self.running = False
                elif event.key == pygame.K_SPACE:
                    if self.dialogue.active:
                        self.dialogue.next()
                    else:
                        all_enemies = self.slimes + self.bosses + self.towers
                        if self.player.attack(all_enemies):
                            self.message = "Hit!"
                            self.message_timer = 30
                            self.play_sound('attacking')
                        else:
                            if self.player.stamina < self.player.attack_cost:
                                self.message = "Not enough stamina!"
                            elif self.player.attack_cooldown > 0:
                                self.message = "Attack on cooldown!"
                            else:
                                self.message = "No enemy in range!"
                            self.message_timer = 30
                elif event.key == pygame.K_e:
                    # Check for NPC interaction first
                    if self.nearby_npc and not self.dialogue.active:
                        self.dialogue.start_dialogue(self.nearby_npc.dialogues)
                        self.message = f"Talking to {self.nearby_npc.npc_name}..."
                        self.message_timer = 30
                    else:
                        # Check for teleport
                        p_rect = pygame.Rect(self.player.pixel_x, self.player.pixel_y,
                                             self.player.tile_w, self.player.tile_h)
                        for tp in getattr(self.game_map, 'teleports', []):
                            if tp.get('rect') and p_rect.colliderect(tp['rect']):
                                dest = tp.get('dest')
                                if dest:
                                    base_dir = os.path.dirname(os.path.abspath(
                                        self.current_map)) if self.current_map else os.path.dirname(os.path.abspath(__file__))
                                    dest_path = dest if os.path.isabs(
                                        dest) else os.path.join(base_dir, dest)
                                    if not os.path.exists(dest_path):
                                        alt = os.path.join(os.path.dirname(
                                            os.path.abspath(__file__)), 'map', dest)
                                        if os.path.exists(alt):
                                            dest_path = alt
                                    if os.path.exists(dest_path):
                                        self.load_map(dest_path, tp)
                                        self.teleport_cooldown = 30
                                        break

    def update(self):
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys, self.game_map.collision_rects,
                                 self.game_map.width, self.game_map.height)

        self.player.update_combat()

        for slime in self.slimes:
            slime.update(self.player, self.game_map.collision_rects,
                         self.game_map.width, self.game_map.height, self)

        for boss in self.bosses:
            projectile = boss.update(self.player)
            if projectile:
                self.projectiles.append(projectile)

        for tower in self.towers:
            projectile = tower.update(self.player)
            if projectile:
                self.projectiles.append(projectile)

        # Check for nearby NPCs
        self.nearby_npc = None
        for npc in self.npcs:
            if npc.can_interact(self.player):
                self.nearby_npc = npc
                break

        for proj in self.projectiles[:]:
            proj.update()

            if proj.is_enemy:
                player_rect = pygame.Rect(self.player.pixel_x, self.player.pixel_y,
                                          self.player.tile_w, self.player.tile_h)
                if proj.rect.colliderect(player_rect) and self.player.state != State.DEAD:
                    self.player.take_damage(proj.damage)
                    self.play_sound('taking_damage')
                    proj.active = False
            else:
                for slime in self.slimes:
                    if slime.state != State.DEAD:
                        slime_rect = pygame.Rect(slime.pixel_x, slime.pixel_y,
                                                 slime.tile_w, slime.tile_h)
                        if proj.rect.colliderect(slime_rect):
                            is_crit = random.random() < self.player.crit_chance
                            damage = proj.damage * self.player.crit_multiplier if is_crit else proj.damage
                            died, xp_reward = slime.take_damage(
                                damage, is_crit)
                            if died:
                                self.player.gain_xp(xp_reward, self)
                            if is_crit:
                                self.floating_texts.append(FloatingText(
                                    slime.pixel_x + slime.tile_w // 2,
                                    slime.pixel_y,
                                    "Critical!",
                                    (255, 0, 0)
                                ))
                            proj.active = False
                            break

                for boss in self.bosses:
                    if boss.state != State.DEAD:
                        boss_rect = pygame.Rect(boss.pixel_x, boss.pixel_y,
                                                boss.render_w, boss.render_h)
                        if proj.rect.colliderect(boss_rect):
                            is_crit = random.random() < self.player.crit_chance
                            damage = proj.damage * self.player.crit_multiplier if is_crit else proj.damage
                            died, xp_reward = boss.take_damage(damage, is_crit)
                            if died:
                                self.player.gain_xp(xp_reward, self)
                            if is_crit:
                                self.floating_texts.append(FloatingText(
                                    boss.pixel_x + boss.render_w // 2,
                                    boss.pixel_y,
                                    "Critical!",
                                    (255, 0, 0)
                                ))
                            proj.active = False
                            break

                for tower in self.towers:
                    if tower.state != State.DEAD:
                        tower_rect = pygame.Rect(tower.pixel_x, tower.pixel_y,
                                                 tower.render_w, tower.render_h)
                        if proj.rect.colliderect(tower_rect):
                            is_crit = random.random() < self.player.crit_chance
                            damage = proj.damage * self.player.crit_multiplier if is_crit else proj.damage
                            died, xp_reward = tower.take_damage(
                                damage, is_crit)
                            if died:
                                self.player.gain_xp(xp_reward, self)
                            if is_crit:
                                self.floating_texts.append(FloatingText(
                                    tower.pixel_x + tower.render_w // 2,
                                    tower.pixel_y,
                                    "Critical!",
                                    (255, 0, 0)
                                ))
                            proj.active = False
                            break

            if not proj.active or proj.x < 0 or proj.x > self.game_map.width * self.game_map.tile_w or \
               proj.y < 0 or proj.y > self.game_map.height * self.game_map.tile_h:
                self.projectiles.remove(proj)

        for text in self.floating_texts[:]:
            text.update()
            if not text.is_alive():
                self.floating_texts.remove(text)

        self.camera.update(self.player.pixel_x, self.player.pixel_y,
                           self.player.tile_w, self.player.tile_h)

        self.teleport_ready = None
        if getattr(self, 'teleport_cooldown', 0) > 0:
            self.teleport_cooldown -= 1
        else:
            p_rect = pygame.Rect(self.player.pixel_x, self.player.pixel_y,
                                 self.player.tile_w, self.player.tile_h)
            for tp in getattr(self.game_map, 'teleports', []):
                if tp.get('rect') and p_rect.colliderect(tp['rect']):
                    self.teleport_ready = tp
                    break

        if self.message_timer > 0:
            self.message_timer -= 1

        all_dead = all(s.state == State.DEAD for s in self.slimes) and \
            all(b.state == State.DEAD for b in self.bosses) and \
            all(t.state == State.DEAD for t in self.towers)

        if all_dead and len(self.slimes + self.bosses + self.towers) > 0 and self.teleport_marker_timer == 0:
            tps = getattr(self.game_map, 'teleports', [])
            if tps:
                tp = tps[0]
                self.teleport_marker_rect = tp.get('rect')
                self.teleport_marker_timer = self.teleport_marker_duration

        if self.teleport_marker_timer > 0:
            self.teleport_marker_timer -= 1
            if self.teleport_marker_timer == 0:
                self.teleport_marker_rect = None

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.game_map.draw(self.screen, self.camera.x, self.camera.y)

        for npc in self.npcs:
            npc.draw(self.screen, self.camera.x, self.camera.y)

        for slime in self.slimes:
            slime.draw(self.screen, self.camera.x, self.camera.y)

        for boss in self.bosses:
            boss.draw(self.screen, self.camera.x, self.camera.y)

        for tower in self.towers:
            tower.draw(self.screen, self.camera.x, self.camera.y)

        self.player.draw(self.screen, self.camera.x, self.camera.y)

        for proj in self.projectiles:
            proj.draw(self.screen, self.camera.x, self.camera.y)

        for text in self.floating_texts:
            text.draw(self.screen, self.camera.x, self.camera.y)

        if getattr(self, 'debug_draw_teleports', False):
            for tp in getattr(self.game_map, 'teleports', []):
                try:
                    r = tp.get('rect')
                    if r:
                        sx = r.x - self.camera.x
                        sy = r.y - self.camera.y
                        pygame.draw.rect(
                            self.screen, (0, 255, 255), (sx, sy, r.width, r.height), 2)
                        lbl = self.font.render(
                            str(tp.get('dest')), True, (0, 255, 255))
                        self.screen.blit(lbl, (sx, sy - 18))
                except Exception:
                    pass

        if getattr(self, 'teleport_marker_rect', None) and getattr(self, 'teleport_marker_timer', 0) > 0:
            try:
                tp = self.teleport_marker_rect
                sx = int(tp.centerx - self.camera.x)
                sy = int(tp.top - self.camera.y) - 24
                pulse = 1.0 + 0.2 * \
                    (1 + math.sin(self.teleport_marker_timer * 0.2))
                arrow_h = int(16 * pulse)
                arrow_w = int(12 * pulse)
                points = [(sx, sy), (sx - arrow_w, sy + arrow_h),
                          (sx + arrow_w, sy + arrow_h)]
                pygame.draw.polygon(self.screen, (255, 215, 0), points)
                label = self.font.render("TELEPORT", True, (255, 215, 0))
                self.screen.blit(label, (sx - label.get_width() // 2, sy - 18))
            except Exception:
                pass

        draw_ui_bar(self.screen, 10, 10, 200, 25, self.player.health,
                    self.player.max_health, (46, 204, 113), (34, 139, 34), "Health")
        draw_ui_bar(self.screen, 10, 50, 200, 20, self.player.stamina,
                    self.player.max_stamina, (241, 196, 15), (150, 100, 0), "Stamina")

        # Draw XP bar
        draw_ui_bar(self.screen, 10, 85, 200, 15, self.player.xp,
                    self.player.xp_to_next_level, (138, 43, 226), (75, 0, 130), "XP")

        # Draw level indicator
        level_font = pygame.font.Font(None, 28)
        level_text = level_font.render(
            f"Level {self.player.level}", True, (255, 255, 255))
        level_bg = pygame.Surface(
            (level_text.get_width() + 10, level_text.get_height() + 4))
        level_bg.set_alpha(180)
        level_bg.fill((0, 0, 0))
        self.screen.blit(level_bg, (220, 10))
        self.screen.blit(level_text, (225, 12))

        # Draw stats info
        stats_font = pygame.font.Font(None, 20)
        stats_y = 40
        stats_info = [
            f"DMG: {int(self.player.attack_damage)}",
            f"CRIT: {int(self.player.crit_chance * 100)}%"
        ]
        for stat_text in stats_info:
            stat_surf = stats_font.render(stat_text, True, (200, 200, 200))
            self.screen.blit(stat_surf, (225, stats_y))
            stats_y += 20

        controls = self.font.render(
            "WASD: Move | SHIFT: Run | SPACE: Attack | LMB: Shoot | E: Interact/Teleport", True, (255, 255, 255))
        self.screen.blit(controls, (10, self.screen_height - 30))

        if getattr(self, 'teleport_ready', None):
            prompt = self.font.render(
                "Press E to teleport", True, (0, 255, 255))
            self.screen.blit(prompt, (self.screen_width //
                             2 - prompt.get_width() // 2, 70))

        if self.nearby_npc and not self.dialogue.active:
            prompt = self.font.render(
                f"Press E to talk to {self.nearby_npc.npc_name}", True, (255, 255, 100))
            self.screen.blit(prompt, (self.screen_width //
                             2 - prompt.get_width() // 2, 90))

        if self.message_timer > 0:
            msg_surf = self.font.render(self.message, True, (255, 255, 0))
            self.screen.blit(msg_surf, (self.screen_width //
                             2 - msg_surf.get_width() // 2, 100))

        if self.player.state == State.DEAD:
            game_over_font = pygame.font.Font(None, 72)
            game_over_surf = game_over_font.render(
                "YOU DIED!", True, (255, 0, 0))
            self.screen.blit(game_over_surf, (self.screen_width // 2 - game_over_surf.get_width() // 2,
                                              self.screen_height // 2))

        self.dialogue.draw(self.screen, self.screen_width, self.screen_height)

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(100)
        pygame.quit()


def find_tmx_file():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cwd = os.getcwd()

    search_dirs = [script_dir]
    if cwd != script_dir:
        search_dirs.append(cwd)

    possible_paths = []

    for d in search_dirs:
        map_dir = os.path.join(d, "map")
        if os.path.exists(map_dir) and os.path.isdir(map_dir):
            print(f"Contents of 'map' folder ({map_dir}):")
            for file in os.listdir(map_dir):
                if file.endswith('.tmx'):
                    print(f"  - {file}")
                    possible_paths.append(os.path.join(map_dir, file))
        else:
            print(f"'map' folder not found at: {map_dir}")

    for d in search_dirs:
        print(f"\nTMX files in directory: {d}")
        try:
            for file in os.listdir(d):
                if file.endswith('.tmx'):
                    print(f"  - {file}")
                    possible_paths.append(os.path.join(d, file))
        except Exception:
            pass

    for name in ["winter_boss_room.tmx", "boss_room_angel.tmx"]:
        for d in search_dirs:
            possible_paths.append(os.path.join(d, name))

    seen = set()
    cleaned = []
    for p in possible_paths:
        if p not in seen:
            seen.add(p)
            cleaned.append(p)

    for path in cleaned:
        if os.path.exists(path):
            print(f"\nUsing map file: {path}")
            return path

    print("\nERROR: No TMX file found!")
    print("Please ensure you have a .tmx file in either:")
    print("  - The 'map' folder next to the script or in the current directory")
    print("  - The current directory")
    return None


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_map_path = os.path.join(script_dir, "map", "main_map.tmx")
    if not os.path.exists(main_map_path):
        print("main_map.tmx not found in the map folder!")
        sys.exit(1)

    start_fullscreen = False
    if len(sys.argv) > 1 and sys.argv[1].lower() in ['fullscreen', '-f', '--fullscreen']:
        start_fullscreen = True

    try:
        game = Game(main_map_path, fullscreen=start_fullscreen)
        game.run()
    except Exception as e:
        print(f"\nError starting game: {e}")
        sys.exit(1)