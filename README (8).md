# 🎮 Snake Galaxy Adventure

A space-themed take on the classic Snake game, built entirely with **Python Turtle Graphics** —
no game engine, no external libraries.

Guide your snake through a star field, collect glowing food, dodge drifting meteors, grab
power-ups, and climb through levels as the galaxy backdrop changes around you.

نسخة فضائية من لعبة الثعبان الكلاسيكية، مبنية بالكامل بمكتبة Turtle في بايثون — بدون أي محرك ألعاب أو مكتبات خارجية.

---

## Features

### Gameplay

- **Classic snake mechanics** — eat, grow, avoid your own tail
- **Level progression** — the game speeds up and the space backdrop changes as you advance
- **Meteor obstacles** — drifting hazards that move independently of the snake
- **Decorative planets** — randomly coloured and placed each run
- **Combo scoring** — chain quick catches inside the combo window for bonus points

### Power-ups

Three collectible power-ups spawn during play, each colour-coded:

| Power-up | Colour | Effect |
|---|---|---|
| **Double** | Gold | Doubles the points scored |
| **Slow** | Deep sky blue | Slows the snake down for easier control |
| **Magnet** | Violet | Pulls food toward the snake |

### Progress and persistence

- **Save and resume** — press `P` to save mid-run, `L` from the menu to pick it back up
- **High score** — kept between sessions
- **Statistics screen** — total games played, best score, and average playtime
- **Live HUD** — current score, high score, elapsed time, level, and active power-ups

### Presentation

- Animated splash screen
- Menu, stats, and game-over screens
- Glowing, colour-cycling food
- Sound effects for movement, eating, level-up, and game over

---

## Controls

| Key | Action |
|---|---|
| `W` `A` `S` `D` or Arrow keys | Move the snake |
| `ENTER` | Start the game / restart after game over |
| `P` | Save the current game |
| `L` | Resume a saved game (from the menu) |
| `T` | Open the statistics screen |
| `M` | Return to the menu |
| `Q` | Quit |

---

## Requirements

- **Python 3.13** or newer
- `turtle` and `tkinter` — both ship with the standard Python installer

No `pip install` step is needed.

> On Linux you may need tkinter separately: `sudo apt install python3-tk`

---

## Running the game

```bash
git clone https://github.com/lolo67fa/snake-Galaxy-Adventure.git
cd snake-Galaxy-Adventure

python prosnake.py
```

### Building a Windows executable

The repository includes a PyInstaller spec file:

```bash
pip install pyinstaller
pyinstaller prosnake.spec
```

The build lands in `dist/`.

---

## Project structure

```
snake-Galaxy-Adventure/
│
├── prosnake.py          # Game source
├── prosnake.spec        # PyInstaller build configuration
│
├── space_bg.gif         # Level 1 background
├── space2.gif           # Level 2 background
├── space3.gif           # Level 3 background
│
├── move.wav             # Movement sound
├── eat.wav              # Food collected
├── start.wav            # Game start
├── levelup.wav          # Level advanced
└── over.wav             # Game over
```

Three files are created at runtime and are not part of the source:

| File | Holds |
|---|---|
| `score.txt` | Highest score achieved |
| `stats.txt` | Games played, total playtime, best score |
| `savegame.txt` | A saved run, written when you press `P` |

---

## Notes

**Sound is Windows-only.** Audio uses the `winsound` module from the standard library, which
exists only on Windows. On macOS and Linux the game runs normally, just silently — every sound
call is guarded by a file-existence check, so a missing `.wav` never crashes the game.

---

## Roadmap

- [ ] **Cross-platform audio** — replace `winsound` with `playsound` or `pygame.mixer`
- [ ] **Difficulty settings** — easy, normal, and hard starting speeds
- [ ] **More levels** — additional backgrounds and obstacle patterns
- [ ] **Leaderboard** — keep the top ten scores instead of one
- [ ] **Pause** — a proper pause key mid-run
- [ ] **Configurable controls** — let the player rebind keys

---

## Author

**Ghala Alshreef** — *Ghala Studios*

- GitHub: [@lolo67fa](https://github.com/lolo67fa)
- LinkedIn: [ghala-a-670a62380](https://linkedin.com/in/ghala-a-670a62380)
- Portfolio: [try.ka.nz/ai/ghalaalshreef](https://try.ka.nz/ai/ghalaalshreef)

---

## License

Released under the MIT License.
