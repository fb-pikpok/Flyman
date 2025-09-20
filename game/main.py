# game/main.py
import asyncio, pygame

async def main():
    pygame.init()
    screen = pygame.display.set_mode((900, 500))
    clock = pygame.time.Clock()
    pygame.display.set_caption("Flyman")
    running = True

    pixel_font = pygame.font.Font("game/assets/fonts/pixeltype.ttf", 50)
    sky_surface = pygame.image.load("game/assets/graphics/sky.png").convert()

    # Player for now is just a circle
    player_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
    pygame.draw.circle(player_surface, 'blue', (25, 25), 10)
    player_x_pos = 600


    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
        # ... update & draw ...

        screen.blit(sky_surface, (0, 0))
        screen.blit(pixel_font.render("Flyman", True, 'black'), (50, 50))


        player_x_pos += 4
        if player_x_pos > 870:
            player_x_pos = -30
        screen.blit(player_surface, (player_x_pos, 250))


        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)  # yield to browser each frame
    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
    