import asyncio
from dataclasses import dataclass

import pygame

WIDTH, HEIGHT = 1200, 500


@dataclass
class ContactInfo:
    on_ground: bool = False
    hit_head: bool = False
    hit_left: bool = False
    hit_right: bool = False


class Player:
    def __init__(self, x, y, radius):
        d = radius * 2
        self.rect = pygame.Rect(0, 0, d, d)
        self.rect.center = (x, y)

        # float physics
        self.pos_x = float(self.rect.centerx)
        self.pos_y = float(self.rect.centery)
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.input_horizontal = 0

        # constants
        self.GRAVITY = 0.5
        self.MOVE_SPEED = 4
        self.JUMP = -13

        # Gliding motion tuning
        self.GLIDE_GRAVITY = 0.33
        self.GLIDE_LIFT_FACTOR = 0.04
        self.GLIDE_MAX_DESCENT_SPEED = 4.8
        self.GLIDE_UPWARD_CAP = -2.5
        self.GLIDE_ACCEL = 0.55
        self.GLIDE_DRAG_ACTIVE = 0.992
        self.GLIDE_DRAG_IDLE = 0.82
        self.GLIDE_MAX_SPEED = 5.5
        self.GLIDE_MIN_ENTRY_SPEED = 3.2
        self.GLIDE_ENTRY_DESCENT_CEILING = 2.6
        self.GLIDE_REVERSE_DAMP = 0.9

        self.facing = pygame.Vector2(0, 1)

        # simple FSM state (expand later: 'airborne', 'grounded', 'gliding', ...)
        self.movement_state = "airborne"

    def handle_input(self, keys):
        horizontal = 0
        if keys[pygame.K_a]:
            horizontal -= 1
        if keys[pygame.K_d]:
            horizontal += 1

        self.input_horizontal = horizontal

        if self.movement_state != "gliding":
            self.vel_x = horizontal * self.MOVE_SPEED

    def try_jump(self):
        if self.movement_state == "grounded":
            self.vel_y = self.JUMP
            self.movement_state = "airborne"

    def start_glide(self):
        if self.movement_state != "airborne":
            return

        direction = 1
        if abs(self.vel_x) >= 0.1:
            direction = 1 if self.vel_x > 0 else -1
        elif self.input_horizontal != 0:
            direction = self.input_horizontal
        elif abs(self.facing.x) >= 0.1:
            direction = 1 if self.facing.x > 0 else -1

        horizontal_speed = abs(self.vel_x)
        carry_from_drop = max(self.vel_y, 0.0) * 0.15
        target_speed = max(self.GLIDE_MIN_ENTRY_SPEED, horizontal_speed + carry_from_drop)
        self.vel_x = direction * min(target_speed, self.GLIDE_MAX_SPEED)

        self.vel_y = max(min(self.vel_y, self.GLIDE_ENTRY_DESCENT_CEILING), self.GLIDE_UPWARD_CAP)

        self.movement_state = "gliding"
        self.update_facing()

    def spacebar_event(self):
        if self.movement_state == "grounded":
            self.try_jump()
        elif self.movement_state == "airborne":
            self.start_glide()

    def apply_forces(self):
        was_gliding = self.movement_state == "gliding"
        if was_gliding:
            accel = self.input_horizontal * self.GLIDE_ACCEL
            if self.input_horizontal and self.vel_x * self.input_horizontal < 0:
                self.vel_x *= self.GLIDE_REVERSE_DAMP
            self.vel_x += accel

            drag = self.GLIDE_DRAG_ACTIVE if self.input_horizontal else self.GLIDE_DRAG_IDLE
            self.vel_x *= drag
            self.vel_x = max(-self.GLIDE_MAX_SPEED, min(self.vel_x, self.GLIDE_MAX_SPEED))

            self.vel_y += self.GLIDE_GRAVITY
            lift = abs(self.vel_x) * self.GLIDE_LIFT_FACTOR
            self.vel_y -= lift
            if self.vel_y > self.GLIDE_MAX_DESCENT_SPEED:
                self.vel_y = self.GLIDE_MAX_DESCENT_SPEED
            if self.vel_y < self.GLIDE_UPWARD_CAP:
                self.vel_y = self.GLIDE_UPWARD_CAP

            if self.input_horizontal == 0 and abs(self.vel_x) < 0.25:
                self.movement_state = "airborne"

        if self.movement_state != "gliding":
            self.vel_y += self.GRAVITY

    def update_facing(self):
        velocity = pygame.Vector2(self.vel_x, self.vel_y)
        if velocity.length_squared() >= 1e-4:
            self.facing = velocity.normalize()

    def move_and_collide(self, platforms):
        contacts = ContactInfo()
        half_width = self.rect.width / 2
        half_height = self.rect.height / 2

        # pygame.Rect.colliderect requires >=1px overlap, so track float edges to catch crossings.
        prev_center_y = self.pos_y
        prev_bottom = prev_center_y + half_height
        prev_top = prev_center_y - half_height

        self.apply_forces()
        self.pos_y += self.vel_y
        vertical_velocity = self.vel_y
        self.rect.centery = round(self.pos_y)

        landing_plat = None
        head_plat = None

        for plat in platforms:
            if self.rect.right <= plat.left or self.rect.left >= plat.right:
                continue

            if vertical_velocity >= 0 and prev_bottom <= plat.top and self.rect.bottom >= plat.top:
                if landing_plat is None or plat.top < landing_plat.top:
                    landing_plat = plat

            if vertical_velocity < 0 and prev_top >= plat.bottom and self.rect.top <= plat.bottom:
                if head_plat is None or plat.bottom > head_plat.bottom:
                    head_plat = plat

        if landing_plat:
            self.rect.bottom = landing_plat.top
            self.pos_y = float(self.rect.centery)
            self.vel_y = 0.0
            contacts.on_ground = True
        elif head_plat:
            self.rect.top = head_plat.bottom
            self.pos_y = float(self.rect.centery)
            self.vel_y = 0.0
            contacts.hit_head = True

        prev_center_x = self.pos_x
        prev_left = prev_center_x - half_width
        prev_right = prev_center_x + half_width

        self.pos_x += self.vel_x
        horizontal_velocity = self.vel_x
        self.rect.centerx = round(self.pos_x)

        hit_right_plat = None
        hit_left_plat = None

        for plat in platforms:
            if self.rect.bottom <= plat.top or self.rect.top >= plat.bottom:
                continue

            if horizontal_velocity > 0 and prev_right <= plat.left and self.rect.right >= plat.left:
                if hit_right_plat is None or plat.left < hit_right_plat.left:
                    hit_right_plat = plat

            if horizontal_velocity < 0 and prev_left >= plat.right and self.rect.left <= plat.right:
                if hit_left_plat is None or plat.right > hit_left_plat.right:
                    hit_left_plat = plat

        if hit_right_plat:
            self.rect.right = hit_right_plat.left
            self.pos_x = float(self.rect.centerx)
            self.vel_x = 0.0
            contacts.hit_right = True
        elif hit_left_plat:
            self.rect.left = hit_left_plat.right
            self.pos_x = float(self.rect.centerx)
            self.vel_x = 0.0
            contacts.hit_left = True

        if contacts.on_ground:
            self.movement_state = "grounded"
        elif self.movement_state != "gliding":
            self.movement_state = "airborne"

        self.update_facing()

        return contacts


async def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    pygame.display.set_caption("Flyman")

    # UI
    game_font = pygame.font.Font('game/assets/fonts/pixeltype.ttf', 50)
    text_surface = game_font.render('Flyman', False, pygame.Color('black'))

    # Colors
    SKY_COLOR = pygame.Color('skyblue')
    PLAYER_COLOR = pygame.Color('red')
    GROUNDED_COLOR = pygame.Color('green')
    GLIDE_COLOR = pygame.Color('gold')
    PLATFORM_COLOR = pygame.Color('darkgreen')

    # Player (physics: keep float pos, render/collide via Rect)
    RADIUS = 11
    player = Player(80, 250, RADIUS)

    # Platforms
    platforms = [
        pygame.Rect(0, HEIGHT-10, WIDTH, 10),       # ground platform
        pygame.Rect(200, HEIGHT-250, 150, 10),
        pygame.Rect(200, HEIGHT-150, 150, 10),
        pygame.Rect(420, 270, 10, 190),
        pygame.Rect(430, 271, 50, 189)      # NOTE Oszillation platform?
    ]

    running = True
    space_was_down = False
    while running:
        # --- events: discrete actions (jump, quit) ---
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        player.handle_input(keys=keys)

        space_now = keys[pygame.K_SPACE]
        if space_now and not space_was_down:
            player.spacebar_event()
        space_was_down = space_now

        contacts = player.move_and_collide(platforms=platforms)

        # --- draw ---
        screen.fill(SKY_COLOR)
        screen.blit(text_surface, (50, 50))

        state_color = {
            "grounded": GROUNDED_COLOR,
            "airborne": PLAYER_COLOR,
            "gliding": GLIDE_COLOR,
        }.get(player.movement_state, PLAYER_COLOR)

        pygame.draw.circle(screen, state_color, player.rect.center, RADIUS)

        nose_dir = pygame.Vector2(player.facing)
        if nose_dir.length_squared() < 1e-4:
            nose_dir = pygame.Vector2(0, 1)
        nose_length = RADIUS + 12
        nose_base_offset = RADIUS * 0.3
        nose_half_width = 4
        center_vec = pygame.Vector2(player.rect.center)
        tip = center_vec + nose_dir * nose_length
        base_center = center_vec + nose_dir * nose_base_offset
        right_vec = pygame.Vector2(-nose_dir.y, nose_dir.x)
        nose_points = [
            tip.xy,
            (base_center + right_vec * nose_half_width).xy,
            (base_center - right_vec * nose_half_width).xy,
        ]
        pygame.draw.polygon(screen, state_color, nose_points)

        for plat in platforms:
            pygame.draw.rect(screen, PLATFORM_COLOR, plat)

        print(f"Player pos: ({player.pos_x:.2f}, {player.pos_y:.2f}) Vel: ({player.vel_x:.2f}, {player.vel_y:.2f}) State: {player.movement_state} Contacts: {contacts}")
        # Debug helpers (uncomment if needed)
        # pygame.draw.rect(screen, "black", player_rect, 1)
        # screen.set_at((player_rect.left, player_rect.centery), pygame.Color("black"))
        # screen.set_at(player_rect.center, pygame.Color("black"))
        # pygame.draw.line(screen, (0,0,0), (0, HEIGHT-1), (WIDTH, HEIGHT-1))

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
