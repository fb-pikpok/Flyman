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
        self.JUMP = -14

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

    def apply_gravity(self):
        self.vel_y += self.GRAVITY

    def move_and_collide(self, platforms):
        contacts = ContactInfo()

        # --- vertical ---
        prev_top = self.rect.top
        prev_bottom = self.rect.bottom

        self.apply_gravity()
        self.pos_y += self.vel_y
        self.rect.centery = round(self.pos_y)

        for plat in platforms:
            if not self.rect.colliderect(plat):
                continue
            if self.vel_y > 0 and prev_bottom <= plat.top:
                # landing from above
                self.rect.bottom = plat.top
                self.pos_y = self.rect.centery
                self.vel_y = 0.0
                contacts.on_ground = True
            elif self.vel_y < 0 and prev_top >= plat.bottom:
                # head bump
                self.rect.top = plat.bottom
                self.pos_y = self.rect.centery
                self.vel_y = 0.0
                contacts.hit_head = True


        # --- horizontal ---
        prev_left = self.rect.left
        prev_right = self.rect.right

        self.pos_x += self.vel_x
        self.rect.centerx = round(self.pos_x)

        for plat in platforms:
            if not self.rect.colliderect(plat):
                continue
            if self.vel_x > 0 and prev_right <= plat.left:
                self.rect.right = plat.left
                self.pos_x = self.rect.centerx
                contacts.hit_right = True
            elif self.vel_x < 0 and prev_left >= plat.right:
                self.rect.left = plat.right
                self.pos_x = self.rect.centerx
                contacts.hit_left = True

        # Update movement_state from contacts (tiny FSM)
        if contacts.on_ground:
            self.movement_state = "grounded"
        else:
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
    PLATFORM_COLOR = pygame.Color('darkgreen')

    # Player (physics: keep float pos, render/collide via Rect)
    RADIUS = 11
    player = Player(80, 250, RADIUS)

    # Platforms
    platforms = [
        pygame.Rect(0, HEIGHT-10, WIDTH, 10),       # ground platform
        pygame.Rect(200, HEIGHT-150, 150, 10),
        pygame.Rect(420, 270, 10, 190),
        pygame.Rect(430, 271, 10, 189)      # NOTE Oszillation platform? 
    ]

    running = True
    while running:
        # --- events: discrete actions (jump, quit) ---
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        player.handle_input(keys = keys)
        if keys[pygame.K_SPACE]:
            player.try_jump()

        contacts = player.move_and_collide(platforms= platforms)


        # --- draw ---
        screen.fill(SKY_COLOR)
        screen.blit(text_surface, (50, 50))

        pygame.draw.circle(screen, PLAYER_COLOR if contacts.on_ground else GROUNDED_COLOR, player.rect.center, 11)
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
