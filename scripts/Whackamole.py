import random
import asyncio
import ipywidgets as widgets
from IPython.display import display, clear_output

# -------------------------
# GLOBALS
# -------------------------
GRID_SIZE = 5
BUTTON_SIZE = "100px"
MOLE_MIN_TIME = 0.4
MOLE_MAX_TIME = 1.4
MAX_SIMULTANEOUS_MOLES = 2

running = False
active_moles = {}
score = 0

ai_enabled = False
tasks = []

AI_MIN_REACTION = 0.25
AI_MAX_REACTION = 0.75
AI_MIN_ACCURACY = 0.3
AI_MAX_ACCURACY = 1.0

# -------------------------
# SCORE LABEL
# -------------------------
score_label = widgets.Label(value="Score: 0", style={'font_size': '20px'})

# -------------------------
# CREATE BUTTON GRID
# -------------------------
buttons = []   # actual buttons

def make_handler(i, j):
    def handler(_btn):
        global score, active_moles
        if (i, j) in active_moles:
            del active_moles[(i, j)]
            buttons[i][j].description = ""
            buttons[i][j].style.button_color = "#cccccc"
            score += 1
            score_label.value = f"Score: {score}"
    return handler

for i in range(GRID_SIZE):
    row = []
    for j in range(GRID_SIZE):
        b = widgets.Button(
            description="",
            layout=widgets.Layout(width=BUTTON_SIZE, height=BUTTON_SIZE),
            style={"button_color": "#cccccc"}
        )
        b.on_click(make_handler(i, j))
        row.append(b)
    buttons.append(row)

# -------------------------
# START / STOP BUTTONS
# -------------------------
def start_game(_b):
    global running, score, active_moles, tasks
    stop_game(None)

    score = 0
    score_label.value = "Score: 0"
    active_moles = {}
    running = True

    # Clear board
    for row in buttons:
        for b in row:
            b.description = ""
            b.style.button_color = "#cccccc"

    # Start async tasks
    tasks = [
        asyncio.create_task(mole_loop()),
        asyncio.create_task(ai_loop())
    ]

start_button = widgets.Button(description="Start Game", button_style='success')
start_button.on_click(start_game)

def stop_game(_b):
    global running, tasks, active_moles
    running = False
    for t in tasks:
        t.cancel()
    tasks = []

    active_moles = {}
    for row in buttons:
        for b in row:
            b.description = ""
            b.style.button_color = "#cccccc"

stop_button = widgets.Button(description="Stop Game", button_style='danger')
stop_button.on_click(stop_game)

# -------------------------
# AI CONTROLS
# -------------------------
def toggle_ai(btn):
    global ai_enabled
    ai_enabled = not ai_enabled
    btn.description = "AI Helper: ON" if ai_enabled else "AI Helper: OFF"

ai_button = widgets.Button(
    description="AI Helper: OFF",
    layout=widgets.Layout(width="150px")
)
ai_button.on_click(toggle_ai)

ai_strength = widgets.FloatSlider(
    description="AI Strength:",
    min=0, max=100, value=50,
    layout=widgets.Layout(width="300px")
)

# -------------------------
# DISPLAY UI
# -------------------------
# Create the grid layout
grid = widgets.VBox([widgets.HBox(row) for row in buttons])

# Consolidate all UI elements
game_ui_container = widgets.VBox([
    widgets.HBox([start_button, stop_button]),
    score_label,
    grid,
    widgets.HBox([ai_button, ai_strength])
])

# Display the game UI
display(game_ui_container)

# -------------------------
# MOLE LOOP
# -------------------------
async def mole_loop():
    global running

    while running:
        # ensure up to 2 moles at once
        if len(active_moles) < MAX_SIMULTANEOUS_MOLES:

            i = random.randint(0, GRID_SIZE - 1)
            j = random.randint(0, GRID_SIZE - 1)

            if (i, j) not in active_moles:
                active_moles[(i, j)] = True
                buttons[i][j].description = "M"
                buttons[i][j].style.button_color = "#ff6b6b"

                # schedule removal
                lifetime = random.uniform(MOLE_MIN_TIME, MOLE_MAX_TIME)
                asyncio.create_task(remove_mole_after(i, j, lifetime))

        await asyncio.sleep(0.25)

async def remove_mole_after(i, j, delay):
    await asyncio.sleep(delay)
    if running and (i, j) in active_moles:
        del active_moles[(i, j)]
        buttons[i][j].description = ""
        buttons[i][j].style.button_color = "#cccccc"

# -------------------------
# AI LOOP
# -------------------------
async def ai_loop():
    global running

    while running:

        # disabled when slider = 0
        if not ai_enabled or ai_strength.value == 0:
            await asyncio.sleep(0.1)
            continue

        strength = ai_strength.value / 100.0

        reaction = AI_MAX_REACTION - strength * (AI_MAX_REACTION - AI_MIN_REACTION)
        accuracy = AI_MIN_ACCURACY + strength * (AI_MAX_ACCURACY - AI_MIN_ACCURACY)

        await asyncio.sleep(reaction)

        # attempt to hit each mole
        for (i, j) in list(active_moles.keys()):
            if random.random() < accuracy:
                buttons[i][j].click()

        await asyncio.sleep(0.05)