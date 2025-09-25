# game/main.py
import asyncio, pygame

WIDTH, HEIGHT = 900, 500
GROUND_Y = HEIGHT  # ground plane at the bottom edge

async def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    pygame.display.set_caption("Flyman")

    # Colors
    SKY_COLOR = pygame.Color('skyblue')
    PLAYER_COLOR = pygame.Color('red')
    COLLISION_COLOR = pygame.Color('green')

    # Player (physics uses a Rect; rendering uses a circle at rect.center)
    RADIUS = 11
    player_rect = pygame.Rect(0, 0, RADIUS * 2, RADIUS * 2)
    player_rect.left = 80
    player_rect.centery = 250

    vel_y = 0.0
    GRAVITY = 0.5
    JUMP_VELOCITY = -14
    running = True

    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                # Only allow jumping when on ground
                if e.key == pygame.K_SPACE and player_rect.bottom >= GROUND_Y:
                    vel_y = JUMP_VELOCITY

        # Physics
        vel_y += GRAVITY
        player_rect.y += int(vel_y)

        # Ground collision: clamp to ground and zero velocity
        if player_rect.bottom >= GROUND_Y:
            player_rect.bottom = GROUND_Y
            vel_y = 0.0

        # Background
        screen.fill(SKY_COLOR)

        player_color = COLLISION_COLOR if player_rect.bottom >= GROUND_Y else PLAYER_COLOR

        # Draw the player as a circle at the rect center
        pygame.draw.circle(screen, player_color, player_rect.center, RADIUS)


        # Drawings for debugging
        # pygame.draw.rect(screen, "black", player_rect, 1)   # Outline of player rect
        # screen.set_at((player_rect.left, player_rect.centery), pygame.Color("black")) # Center left pixel
        # screen.set_at(player_rect.center, pygame.Color("black")) # Center pixel
        # pygame.draw.line(screen, (0,0,0), (0, GROUND_Y-1), (WIDTH, GROUND_Y-1)) # Ground line


        # Prints for debugging
        print("Velocity: " + str(vel_y))


        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
