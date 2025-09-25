# game/main.py
import asyncio, pygame

WIDTH, HEIGHT = 1200, 500

from dataclasses import dataclass
import pygame

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

        # constants
        self.GRAVITY = 0.5
        self.MOVE_SPEED = 4
        self.JUMP = -13

        # simple FSM state (expand later: 'airborne', 'grounded', 'gliding', …)
        self.movement_state = "airborne"

    def handle_input(self, keys):
        # horizontal input (continuous)
        if keys[pygame.K_a]:
            self.vel_x = -self.MOVE_SPEED
        elif keys[pygame.K_d]:
            self.vel_x = self.MOVE_SPEED
        else:
            self.vel_x = 0.0

    def try_jump(self):
        if self.movement_state == "grounded":
            self.vel_y = self.JUMP
            self.movement_state = "airborne"

    def start_glide(self):
        if self.movement_state == "airborne":
            self.movement_state = "gliding"

    def spacebar_event(self):
        if self.movement_state == "grounded":
            self.try_jump()
        elif self.movement_state == "airborne":
            self.start_glide()



    def apply_gravity(self):
        self.vel_y += self.GRAVITY

    def move_and_collide(self, platforms):
        contacts = ContactInfo()
        half_width = self.rect.width / 2
        half_height = self.rect.height / 2

        # we can’t rely on Rect.colliderect here: it only fires with >=1px overlap,
        # but our float physics / int rect rounding lets the player “touch” a platform
        # without overlapping. So we detect crossings using last-frame float edges.
        prev_center_y = self.pos_y
        prev_bottom = prev_center_y + half_height
        prev_top = prev_center_y - half_height

        self.apply_gravity()
        self.pos_y += self.vel_y
        vertical_velocity = self.vel_y
        self.rect.centery = round(self.pos_y)

        landing_plat = None
        head_plat = None

        for plat in platforms:
            if self.rect.right <= plat.left or self.rect.left >= plat.right:
                continue

            if vertical_velocity >= 0 and prev_bottom <= plat.top and self.rect.bottom >= plat.top: # Falling? AND Player was above the platform AND bottom has reached or passed platform top
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

        # --- horizontal: similar crossing checks ---
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
        player.handle_input(keys = keys)

        space_now = keys[pygame.K_SPACE]
        if space_now and not space_was_down:
            player.spacebar_event()
        space_was_down = space_now


        contacts = player.move_and_collide(platforms= platforms)


        # --- draw ---
        screen.fill(SKY_COLOR)
        screen.blit(text_surface, (50, 50))

        state_color = {
            "grounded": GROUNDED_COLOR,
            "airborne": PLAYER_COLOR,
            "gliding": GLIDE_COLOR,
        }.get(player.movement_state, PLAYER_COLOR)

        pygame.draw.circle(screen, state_color, player.rect.center, RADIUS)

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
