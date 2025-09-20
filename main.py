# game/main.py
import asyncio, pygame

async def main():
    pygame.init()
    screen = pygame.display.set_mode((900, 500))
    clock = pygame.time.Clock()
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
        # ... update & draw ...
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)  # yield to browser each frame
    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
    