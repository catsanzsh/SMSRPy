'''
test.py – Super Mario Star Road: Browser & Playable World Viewer

A complete Ursina-powered application to browse, select, and "enter" every course from Super Mario Star Road.
Selecting a course now launches a procedurally generated 3D environment unique to that course, running at 60 FPS.

Controls (Main Menu):
    UP/DOWN  : Scroll course list
    TAB      : Cycle category (Main/Secret/Boss/Overworld)
    ENTER    : Enter selected course (launches 3D world)
    ESC      : Quit

Controls (In Course):
    WASD     : Move
    MOUSE    : Look (hold right mouse)
    SPACE    : Jump
    Q        : Back to browser
    R        : Reload course
    F11      : Toggle fullscreen
    ESC      : Quit
'''
from ursina import *
from dataclasses import dataclass
from typing import List
import random  # Added for procedural generation

# -----------------------------------------------------------------------------
# Data Classes and Static Data
# -----------------------------------------------------------------------------
@dataclass
class Course:
    name: str
    stars: int
    requirement: str
    acts: int | None = None
    coins: int | None = None

    def to_row(self) -> str:
        acts_str = self.acts if self.acts is not None else "–"
        coins_str = self.coins if self.coins is not None else "–"
        return f"{self.name:<26}  ⭐ {self.stars:<2}  Req: {self.requirement:<9}  Acts: {acts_str:<3}  Coins: {coins_str}"

main_courses: List[Course] = [
    Course("Bob‑omb Islands",           7, "0",      acts=None, coins=147),
    Course("Sky Land Resort",           7, "–",      acts=None, coins=156),
    Course("Piranha Plant Pond",        7, "–",      acts=None, coins=151),
    Course("Chuckya Harbor",            7, "8",      acts=None, coins=202),
    Course("Gloomy Garden",             7, "8",      acts=None, coins=139),
    Course("Colorful Coral Caverns",    7, "20",     acts=None, coins=137),
    Course("Koopa Canyon",              7, "30",     acts=None, coins=152),
    Course("Large Leaf Forest",         7, "20",     acts=None, coins=132),
    Course("Mad Musical Mess",          7, "30",     acts=None, coins=154),
    Course("Melting Snow Peaks",        7, "20",     acts=None, coins=184),
    Course("Colossal Candy Clutter",    7, "40",     acts=None, coins=211),
    Course("Cloudrail Station",         7, "–",      acts=None, coins=205),
    Course("Fatal Flame Falls",         7, "–",      acts=None, coins=152),
    Course("Bob‑omb Battle Factory",    7, "65",     acts=None, coins=165),
    Course("Starlight Runway",          7, "–",      acts=None, coins=169),
]
secret_courses: List[Course] = [
    Course("Mushroom Mountain Town", 3, "0", coins=68),
    Course("Creepy Cap Cave",        2, "8", coins=37),
    Course("Puzzle of the Vanish Cap", 1, "SR", coins=28),
    Course("Sandy Slide Secret",     3, "20", coins=85),
    Course("Windy Wing Cap Well",    2, "40", coins=70),
    Course("Hidden Palace Finale",   1, "120", coins=20),
]
boss_worlds: List[Course] = [
    Course("Bowser's Slippery Swamp",  1, "20 Stars", coins=90),
    Course("Bowser's Retro Remix Castle", 1, "40 Stars", coins=51),
    Course("Bowser's Rainbow Rumble", 1, "80 Stars", coins=56),
]
overworlds: List[Course] = [
    Course("Star Leap Tower Grounds",      2, "0", coins=4),
    Course("Star Leap Tower Interior",     0, "20 Stars", coins=2),
    Course("Flowpipe Sewers",              1, "–", coins=19),
    Course("Star Leap Tower First Floor",  0, "40 Stars", coins=0),
    Course("Star Road",                    1, "65 Stars", coins=28),
    Course("Star Leap Tower Grounds (Night)", 0, "80 Stars", coins=0),
    Course("0‑Life Area (DEATH)",          0, "–", coins=0),
]
categories = {
    "Main Courses": main_courses,
    "Secret Courses": secret_courses,
    "Boss Worlds": boss_worlds,
    "Overworlds": overworlds,
}

# -----------------------------------------------------------------------------
# UI – Browser Panel
# -----------------------------------------------------------------------------
class CourseBrowser(Entity):
    def __init__(self, courses: List[Course], **kwargs):
        super().__init__(parent=camera.ui, **kwargs)
        self.courses = courses
        self.items: List[Text] = []
        self.scroll_index = 0
        self.selected = 0
        self.visible_rows = 10
        self.row_height = 0.05
        self._refresh()

    def set_courses(self, courses: List[Course]):
        self.courses = courses
        self.scroll_index = 0
        self.selected = 0
        self._refresh()

    def scroll(self, amount: int):
        self.selected = clamp(self.selected + amount, 0, len(self.courses) - 1)
        if self.selected < self.scroll_index:
            self.scroll_index = self.selected
        elif self.selected >= self.scroll_index + self.visible_rows:
            self.scroll_index = self.selected - self.visible_rows + 1
        self._refresh()

    def _refresh(self):
        for item in self.items:
            destroy(item)
        self.items.clear()
        start = self.scroll_index
        end = start + self.visible_rows
        slice_ = self.courses[start:end]
        for i, course in enumerate(slice_):
            y = 0.4 - i * self.row_height
            color_sel = color.yellow if (start + i) == self.selected else color.white
            t = Text(course.to_row(), parent=self, origin=(-0.5, 0), position=(-0.47, y), scale=0.85, color=color_sel)
            self.items.append(t)

    def get_selected_course(self) -> Course:
        return self.courses[self.selected]

# -----------------------------------------------------------------------------
# Simple Playable Course World (3D sandbox w/ Mario)
# -----------------------------------------------------------------------------
class SimpleMarioWorld(Entity):
    def __init__(self, course_name, on_quit, **kwargs):
        super().__init__(**kwargs)
        self.on_quit = on_quit
        self.course_name = course_name
        camera.parent = self
        camera.position = (0, 2, -8)
        camera.rotation = (10, 0, 0)
        self._setup_world()
        self.info = Text(f"{course_name}  |  Q: Back  R: Reload  F11: Fullscreen  ESC: Quit", origin=(0,0), position=(0,0.44), scale=0.8, color=color.azure, parent=camera.ui)
        mouse.locked = False
        self.mario = Entity(model='cube', color=color.red, scale=(1,2,1), collider='box', position=(0,1,0))
        self.grounded = False
        self.vel = Vec3(0)
        self.speed = 7
        self.jump_power = 12
        self.gravity = 32
        self.y_velocity = 0

    def _setup_world(self):
        # Seed random with course name for consistent level generation
        random.seed(hash(self.course_name))

        # Define grid parameters
        grid_size = 20
        cell_size = 2
        p_empty = 0.7
        p_platform = 0.2
        p_obstacle = 0.1

        # Guarantee a platform at the starting position (0, 0)
        Entity(model='cube', color=color.green, scale=(cell_size, 1, cell_size), position=(0, 0, 0), collider='box')

        # Generate the level grid
        for x in range(grid_size):
            for z in range(grid_size):
                if x == 0 and z == 0:
                    continue  # Skip starting position (already placed)
                r = random.random()
                pos = (x * cell_size, 0, z * cell_size)
                if r < p_empty:
                    continue
                elif r < p_empty + p_platform:
                    # Place a platform
                    Entity(model='cube', color=color.green, scale=(cell_size, 1, cell_size), position=pos, collider='box')
                else:
                    # Place an obstacle (sphere)
                    Entity(model='sphere', color=color.red, scale=1, position=(pos[0], 1, pos[2]), collider='sphere')

        # Add a skybox for ambiance
        Entity(model='sphere', scale=(80,80,80), color=color.cyan.tint(-0.5), double_sided=True, position=(0,20,0), shader=None)

    def input(self, key):
        if key == 'q':
            self.quit()
        elif key == 'r':
            self._reset_mario()
        elif key == 'f11':
            window.fullscreen = not window.fullscreen
        elif key == 'escape':
            application.quit()

    def update(self):
        dt = time.dt
        move = Vec3(0)
        if held_keys['w']:
            move.z -= 1
        if held_keys['s']:
            move.z += 1
        if held_keys['a']:
            move.x -= 1
        if held_keys['d']:
            move.x += 1
        move = move.normalized() * self.speed * dt
        self.mario.position += self.mario.right * move.x + self.mario.forward * move.z
        # Simple gravity
        self.y_velocity -= self.gravity * dt
        self.mario.y += self.y_velocity * dt
        # Basic ground collision
        if self.mario.y <= 1:
            self.mario.y = 1
            self.grounded = True
            self.y_velocity = 0
        else:
            self.grounded = False
        if held_keys['space'] and self.grounded:
            self.y_velocity = self.jump_power
        # Mouse look (hold right mouse)
        if held_keys['right mouse']:
            camera.rotation_y += mouse.velocity[0] * 45
            camera.rotation_x -= mouse.velocity[1] * 30
            camera.rotation_x = clamp(camera.rotation_x, -60, 60)

    def _reset_mario(self):
        self.mario.position = (0,1,0)
        self.y_velocity = 0
        camera.position = (0, 2, -8)
        camera.rotation = (10, 0, 0)

    def quit(self):
        destroy(self.info)
        destroy(self.mario)
        camera.parent = None
        camera.position = (0,0,0)
        camera.rotation = (0,0,0)
        self.on_quit()
        destroy(self)

# -----------------------------------------------------------------------------
# Main App Logic – Browser & Transitions
# -----------------------------------------------------------------------------
app = Ursina(title='SM Star Road: Browser & World Viewer', size=(960, 720), borderless=False, vsync=True)
window.color = color.black
window.fps_counter.enabled = True
window.icon = 'icon'  # (ignored if icon not present)

current_category_index = 0
category_names = list(categories.keys())

# Title text
browser_title = Text(category_names[current_category_index], parent=camera.ui, origin=(0, 0), position=(0, 0.48), scale=1.2, color=color.azure)

# Browser widget
browser = CourseBrowser(categories[category_names[current_category_index]])

# Prompt
prompt = Text("UP/DOWN: Scroll   TAB: Change Category   ENTER: Enter   ESC: Quit", parent=camera.ui, origin=(0, 0), position=(0, -0.45), scale=0.7, color=color.light_gray)

# State
state = {'mode': 'browser', 'world': None}

def show_browser():
    state['mode'] = 'browser'
    browser.enabled = True
    browser_title.enabled = True
    prompt.enabled = True
    if state['world']:
        destroy(state['world'])
        state['world'] = None

def enter_course():
    course = browser.get_selected_course()
    browser.enabled = False
    browser_title.enabled = False
    prompt.enabled = False
    state['mode'] = 'world'
    state['world'] = SimpleMarioWorld(course.name, show_browser)

# Input
def input(key):
    if state['mode'] == 'browser':
        global current_category_index
        if key == 'up arrow':
            browser.scroll(-1)
        elif key == 'down arrow':
            browser.scroll(1)
        elif key == 'tab':
            current_category_index = (current_category_index + 1) % len(category_names)
            cat_name = category_names[current_category_index]
            browser_title.text = cat_name
            browser.set_courses(categories[cat_name])
        elif key == 'enter':
            enter_course()
        elif key == 'escape':
            application.quit()
    elif state['mode'] == 'world':
        if state['world']:
            state['world'].input(key)

if __name__ == '__main__':
    app.run()
