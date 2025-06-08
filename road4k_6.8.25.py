'''test.py – Super Mario Star Road Course Browser

An interactive Ursina application that lets players browse all courses,
secret courses, boss worlds, and overworld areas from *Super Mario Star Road*.

Keys
----
UP / DOWN : Scroll list
TAB        : Cycle course categories (Main → Secret → Boss → Overworld)
ESC        : Quit
'''
from ursina import *
from dataclasses import dataclass
from typing import List

# -----------------------------------------------------------------------------
#  Data Classes
# -----------------------------------------------------------------------------
@dataclass
class Course:
    name: str
    stars: int
    requirement: str  # textual requirement (e.g. "0", "20 Stars")
    acts: int | None = None
    coins: int | None = None

    def to_row(self) -> str:
        """Return a formatted row for UI display."""
        acts_str = self.acts if self.acts is not None else "–"
        coins_str = self.coins if self.coins is not None else "–"
        return f"{self.name:<26}  ⭐ {self.stars:<2}  Req: {self.requirement:<9}  Acts: {acts_str:<3}  Coins: {coins_str}"

# -----------------------------------------------------------------------------
#  Static Course Data (extracted from user table)
# -----------------------------------------------------------------------------
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
#  Ursina UI Helpers
# -----------------------------------------------------------------------------
class CourseBrowser(Entity):
    """Scrollable list widget that displays courses for the current category."""

    def __init__(self, courses: List[Course], **kwargs):
        super().__init__(parent=camera.ui, **kwargs)
        self.courses = courses
        self.items: List[Text] = []
        self.scroll_index = 0
        self.visible_rows = 10  # rows visible at a time
        self.row_height = 0.05  # vertical spacing
        self._refresh()

    # ---------------------------------------------------------------------
    #  Public API
    # ---------------------------------------------------------------------
    def set_courses(self, courses: List[Course]):
        self.courses = courses
        self.scroll_index = 0
        self._refresh()

    def scroll(self, amount: int):
        self.scroll_index = clamp(self.scroll_index + amount, 0, max(0, len(self.courses) - self.visible_rows))
        self._refresh()

    # ---------------------------------------------------------------------
    #  Internal helpers
    # ---------------------------------------------------------------------
    def _refresh(self):
        # Destroy existing Text entities
        for item in self.items:
            destroy(item)
        self.items.clear()
        # Re‑create visible slice
        start = self.scroll_index
        end = start + self.visible_rows
        slice_ = self.courses[start:end]
        for i, course in enumerate(slice_):
            y = 0.4 - i * self.row_height  # start near top of screen
            t = Text(course.to_row(), parent=self, origin=(-0.5, 0), position=(-0.47, y), scale=0.8, color=color.white)
            self.items.append(t)

# -----------------------------------------------------------------------------
#  Application Setup
# -----------------------------------------------------------------------------
app = Ursina(title='SM Star Road Course Browser', size=(800, 600), borderless=False, vsync=True)
window.color = color.black

current_category_index = 0
category_names = list(categories.keys())

# Title text
title_text = Text(category_names[current_category_index], parent=camera.ui, origin=(0, 0), position=(0, 0.48), scale=1.2, color=color.azure)

# Browser widget instance
browser = CourseBrowser(categories[category_names[current_category_index]])

# Prompt text
prompt = Text("UP/DOWN: Scroll   TAB: Change Category   ESC: Quit", parent=camera.ui, origin=(0, 0), position=(0, -0.45), scale=0.7, color=color.light_gray)

# -----------------------------------------------------------------------------
#  Input Handling
# -----------------------------------------------------------------------------

def input(key):
    global current_category_index
    if key == 'up arrow':
        browser.scroll(-1)
    elif key == 'down arrow':
        browser.scroll(1)
    elif key == 'tab':
        # Cycle categories
        current_category_index = (current_category_index + 1) % len(category_names)
        cat_name = category_names[current_category_index]
        title_text.text = cat_name
        browser.set_courses(categories[cat_name])
    elif key == 'escape':
        application.quit()

# -----------------------------------------------------------------------------
#  Run Application
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    app.run()
