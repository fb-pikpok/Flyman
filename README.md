# One-Key Glider (pygame + pygbag on GitHub Pages)

A tiny, skill-based **one-key flight** game written in **Python** with **pygame-ce**, packaged for the web via **pygbag**.  
Tap **Space** to jump. **Hold Space** to glide (dip → rise → fade). Touch the ceiling or the floor and it’s game over. The page includes a simple **top bar** with a **level selector** and a **local high score**.

> Built entirely in Python; exported as static HTML/JS/WASM for GitHub Pages.

---

## 🎯 Goals
- **Python-first workflow** (no React/Tailwind required).
- **Static hosting** on **GitHub Pages** (serves HTML/JS/WASM files).
- Clean, minimal code that’s easy to discuss in interviews.
- Simple DOM UI around the canvas (top bar) and **local high scores**.

---

## 🕹️ How to Play
- **Space (tap):** quick jump upward  
- **Space (hold):** timed glide (dip → rise → fade), moves right  
- **Space (tap during glide):** cancel + small upward nudge (air-brake)  
- **R:** restart  
- **Fail:** hit ceiling or floor  
- **Score:** distance traveled (+ optional rings passed)

---

## 🧰 Tech Stack
- **Python** + **pygame-ce** for game logic, sprites, and animation.
- **pygbag** to package and run pygame in the browser (WebAssembly).
- Optional simple **HTML/CSS** wrapper for a **top bar** (level select / high score).
- **localStorage** for high scores (accessed from Python via pygbag’s JS bridge).

---

## 🗂️ Project Structure
```
one-key-glider/
├─ game/
│  ├─ main.py              # pygame-ce entry point (async loop)
│  ├─ assets/              # sprite sheets, sounds (optional)
│  └─ ui/                  # optional: template/styles for custom page
├─ web-template/           # (advanced) custom index template for pygbag
├─ .github/workflows/deploy.yml
└─ README.md
```

---

## ▶️ Dev Setup

1) **Install deps (in a virtual environment recommended)**

```bash
pip install pygame-ce pygbag
```

2) **Entry point requirements**

- Name your entry script: `main.py`  
- Use an async-aware main loop for browsers, e.g.:

```python
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
```

3) **Run locally (serves and creates web build artifacts)**

```bash
pygbag game
# serves at http://localhost:8000 and produces game/build/web/
```

---

## 🌐 Build for the Web (static files)

If you only want the build artifacts:

```bash
pygbag game
```

Upload the contents of `game/build/web` to any static host (including **GitHub Pages**).

---

## 🧱 Page UI (Top Bar) & High Scores

- **Top bar (level select / high score):**  
  Use a simple HTML template to wrap the canvas (e.g., a header with a `<select>` for levels and a score span). pygbag supports using a custom template for index generation (advanced).

- **High scores (localStorage):**  
  In pygbag, access the browser’s `localStorage` via the JS namespace from Python (e.g., get/set JSON strings). Minimal pattern:

```python
import json, platform
js = platform.window  # browser window
def save_score(best):
    js.localStorage.setItem("best", json.dumps({"best": best}))
def load_score():
    data = js.localStorage.getItem("best")
    return json.loads(data)["best"] if data else 0
```

---

## 🚀 Deploy to GitHub Pages (GitHub Actions)

This workflow **builds with pygbag on CI** and publishes `game/build/web` to Pages.

```yaml
# .github/workflows/deploy.yml
name: Deploy (pygbag → GitHub Pages)

on:
  push:
    branches: [main]

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: python -m pip install --upgrade pip
      - run: pip install pygame-ce pygbag
      - run: pygbag game
      - uses: actions/upload-pages-artifact@v3
        with: { path: 'game/build/web' }

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

Then in **Settings → Pages**, set **Source** to **GitHub Actions**.

---

## 📱 Browser Notes
- Works in modern desktop browsers.
- First load is larger due to the cached Python/pygame runtime.
- On iOS, use recent iOS for compatible WASM runtime.

---

## 🛠️ Troubleshooting
- **Black screen / freeze:** Ensure your main loop is `async` and includes `await asyncio.sleep(0)` each frame; avoid blocking loops.
- **Game doesn’t start:** Confirm entry file is `main.py` and you ran `pygbag` from the parent directory (e.g., `pygbag game`).
- **Custom layout needs:** Use pygbag’s template feature to customize the generated `index.html` around the canvas (advanced).

---

## 📜 License
MIT

---

## 📚 References
- pygbag (package & run Python/pygame-ce in browsers): https://pypi.org/project/pygbag/
- pygame-ce (Community Edition): https://pypi.org/project/pygame-ce/ and https://pyga.me/docs/
- Async main loop guidance & `await asyncio.sleep(0)`: pygbag discussions/issues and community posts
- localStorage from Python via pygbag JS bridge: pygbag Discussions / wiki
- WASM apps on GitHub Pages: see Microsoft’s Blazor WebAssembly on Pages guide
