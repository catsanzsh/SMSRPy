from ursina import *  # Import Ursina engine classes and utilities
from ursina import curve, invoke, application

# Initialize Ursina app
app = Ursina()  
# (Optional: configure window if needed, e.g., window.title or window.size)

# Story narrative lines (list of strings). Index 0 is the first line.
story_lines = [
    "Mario finds himself in a strange new world, seeking Power Stars.",
    "A towering fortress stands before him under the twilight sky.",
    "Enemies lurk around, but Mario presses on with determination.",
    "He navigates treacherous paths and narrow ledges with skill.",
    "At the fortress summit, a fierce Goomba King challenges Mario!",
    "Defeated, the Goomba King drops a shining Power Star at Mario's feet.",
    "With a cheer, Mario claims the Power Star, feeling stronger.",
    "A distant gate opens, revealing a new area for Mario to explore.",
    "Mario gathers 8 Red Coins hidden around the fortress grounds.",
    "The Red Coins' energy forms a Power Star above an ancient pedestal.",
    "Mario leaps high and secures the newly formed Power Star in triumph.",
    "A rumble shakes the world – Bowser's laugh echoes in the distance.",
    "Mario races through the opened gate toward Bowser's looming castle.",
    "In the grand hall, Bowser confronts Mario for a final showdown.",
    "With courage and agility, Mario overcomes Bowser's tricks and traps.",
    "Bowser yields, and the final Grand Star appears for Mario to grab."
]
# Ensure we have the expected number of lines (0-15 indices for this narrative)

# Initialize counters and indices
story_index = 0                  # current index in story_lines being displayed
star_count = 0                   # number of stars collected

# Indices at which to increment star_count
star_trigger_indices = {5, 8, 9, 15}

# Create UI elements
# Narrative text: center of screen, showing the current line of story
narrative_text = Text(
    text=story_lines[0],
    parent=camera.ui,
    origin=(0, 0),       # center alignment
    position=(0, 0.2),   # slightly above center
    scale=1.2,           # make text a bit larger for readability
    color=color.white
)
# Prompt text: instructs the player to press SPACE, appears below narrative
prompt_text = Text(
    text="(Press SPACE to continue)",
    parent=camera.ui,
    origin=(0, 0),      # center alignment
    position=(0, -0.3), # below center
    scale=0.8,
    color=color.light_gray
)
# Star counter text: shows collected stars, positioned at top-left of screen
star_text = Text(
    text="★: 0",        # star symbol and count
    parent=camera.ui,
    origin=(-0.5, 0.5), # top-left alignment
    position=(-0.5, 0.45),
    scale=1.2,
    color=color.yellow
)
# (If an actual star icon image were available, it could be an Entity icon with a Text for the number.
# Here we use a star symbol for simplicity.)

def progress_story():
    """Advance the story by one line, update UI, and handle star collection."""
    global story_index, star_count
    # Only progress if not already at the final line
    if story_index < len(story_lines) - 1:
        story_index += 1
        narrative_text.text = story_lines[story_index]
        # Check if this index triggers a star collection event
        if story_index in star_trigger_indices:
            star_count += 1
            # Update star counter display
            star_text.text = f"★: {star_count}"
            # Animate the star counter text to give feedback (grow then shrink)
            star_text.scale = 1.0  # reset scale in case of leftover scaling
            star_text.animate_scale(1.5, duration=0.2, curve=curve.out_quad)
            # Use invoke to schedule scaling back to normal after a short delay:contentReference[oaicite:5]{index=5}
            invoke(star_text.animate_scale, 1.0, delay=0.25, duration=0.2, curve=curve.in_quad)
        # If we've reached the final line of the story, disable the prompt text
        if story_index == len(story_lines) - 1:
            prompt_text.enabled = False
    else:
        # Already at final line: no further progression
        pass

def input(key):
    """Global input handler for key presses."""
    if key == 'space':
        progress_story()
    if key == 'escape':
        application.quit()  # Cleanly exit the application:contentReference[oaicite:6]{index=6}

# Run the app (if this script is executed directly)
if __name__ == '__main__':
    app.run()
