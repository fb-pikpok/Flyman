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


    player_x_pos = 80
    player_y_pos = 250
    player_gravity = 0
    player_surf = pygame.image.load("game/assets/graphics/player.png").convert_alpha()
    player_rect = player_surf.get_rect(center = (player_x_pos, player_y_pos))





    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            
            # Player logic
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    player_gravity = -14

        # Background
        screen.blit(sky_surface, (0, 0))
        screen.blit(pixel_font.render("Flyman", True, 'black'), (50, 50))


        # Player
        player_gravity += 0.5
        player_y_pos += player_gravity
        screen.blit(player_surf, player_rect)
        
        player_rect.y = player_y_pos
        if player_rect.bottom >= 500:
            player_rect.bottom = 500
            player_gravity = 0

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            print("UP")


        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)  # yield to browser each frame
    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
    