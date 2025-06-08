# 1.py
# Super Mario Star Road: A Narrative Fangame
# To run: pip install ursina

from ursina import *

# The story text based on the Super Mario Star Road plot
story_text = [
    "Yoshi: Mario! Bowser has found the secret to get to the Star Road, the kingdom of the Star Spirits!",
    "Yoshi: Using the power of the Power Stars, he's transporting his troops all over the Mushroom Kingdom!",
    "Yoshi: You must collect enough Power Stars to break the seal and reach the Star Road!",
    "~ You begin your adventure, leaping through paintings and pipes into new worlds... ~",
    "~ After a perilous journey through a swamp, you face... the Pernicious Piranha Plant! ~",
    "~ You defeat the foul flower! You've collected 40 Stars! ~",
    "~ Your adventure continues into a nostalgic and challenging castle in the sky... ~",
    "~ Atop the castle, you challenge the Blueberry Bully and send him flying! ~",
    "~ Victory! You've collected 80 Stars! The seal to the Star Road is weakening... ~",
    "~ With 120 Stars collected, a celestial path opens before you... ~",
    "~ You've reached the Star Road! Bowser's Sky Base floats menacingly ahead. ~",
    "~ The final battle! You face Bowser himself in a chaotic showdown among the stars... ~",
    "~ You've defeated Bowser! The Star Road is safe once more! ~",
    "Princess Peach: Oh, Mario! Thank you! You've saved the Mushroom Kingdom and the Star Spirits!",
    "Princess Peach: For your bravery, please accept this special Power Star! ~",
    "~ YOU GOT A STAR! Total Stars: 121 ~",
    "Narrator: A new challenge has appeared! A Star Replica is now hidden in each secret course...",
    "Narrator: Can you find all 130 Stars? The adventure continues! (Thanks for playing!)"
]

class StarRoadGame(Ursina):
    def __init__(self):
        # Initialize the Ursina application
        super().__init__(
            title='Super Mario Star Road: The Fan Game',
            window_title='Super Mario Star Road',
            borderless=False,
            fullscreen=False,
            size=(600, 400),
            vsync=True # VSync is a better way to cap FPS to monitor refresh rate
        )
        
        # Game state variables
        self.story_index = 0
        self.star_count = 0

        # Set up the simple scene
        window.color = color.black
        Sky(texture='sky_sunset') # Use a built-in sky for atmosphere
        
        self.player = Entity(model='cube', color=color.red, position=(0, 0.5, 0), scale=(0.5, 1, 0.5))
        self.ground = Entity(model='plane', scale=(20, 1, 10), color=color.lime, texture='white_cube', texture_scale=(20,10))
        
        # Set up the camera
        camera.position = (0, 3, -10)
        camera.rotation_x = 10
        
        # Hide default buttons
        window.exit_button.enabled = False
        window.cog_menu.enabled = False # More robust than disabling just the cog

        # UI Elements for the story
        self.narrative_text = Text(
            text=story_text[self.story_index],
            origin=(0, 0),
            scale=1.5,
            position=(0, 0.2),
            background=True,
            color=color.white
        )

        self.prompt_text = Text(
            text="<Press SPACE to Continue>",
            origin=(0, 0),
            scale=1.2,
            position=(0, -0.3),
            color=color.white
        )

        self.star_display = Text(
            text=f"Stars: {self.star_count}",
            origin=(-0.5, 0.5),
            scale=1.5,
            position=(-0.45 * window.aspect_ratio, 0.45),
            color=color.white
        )
        
        # Enable FPS counter to verify performance
        window.fps_counter.enabled = True

    def update_star_count(self, new_count):
        self.star_count = new_count
        self.star_display.color = color.rgba(255, 255, 255, 0)
        self.star_display.text = f"Stars: {self.star_count}"
        self.star_display.animate_color(color.white, duration=0.2)

    def advance_story(self):
        """Moves to the next line of the story and updates text with fade-in effect."""
        self.story_index += 1
        if self.story_index < len(story_text):
            # Update the story text with fade-in
            self.narrative_text.color = color.rgba(255, 255, 255, 0)
            self.narrative_text.text = story_text[self.story_index]
            self.narrative_text.animate_color(color.white, duration=0.5)

            # Trigger simple animations and star updates based on the story index
            self.player.animate_y(1, duration=0.1, curve=curve.out_quad)
            self.player.animate_y(0.5, duration=0.1, delay=0.1, curve=curve.in_quad)

            if self.story_index == 5: # Defeated Piranha Plant
                self.update_star_count(40)
            elif self.story_index == 8: # Defeated Blueberry Bully
                self.update_star_count(80)
            elif self.story_index == 9: # Got 120 stars
                self.update_star_count(120)
                self.ground.animate_color(color.blue, duration=1)
            elif self.story_index == 15: # Got Peach's star
                self.update_star_count(121)
                self.ground.animate_color(color.gold, duration=1)
                
        else:
            # End of the story with fade-in
            self.narrative_text.color = color.rgba(255, 255, 255, 0)
            self.narrative_text.text = "The End. ROM Hack by Skelux, Fan Game by You!"
            self.narrative_text.animate_color(color.white, duration=0.5)
            self.prompt_text.enabled = False

    def input(self, key):
        """Handle user input."""
        if key == 'space':
            self.advance_story()
        if key == 'escape':
            application.quit()

if __name__ == '__main__':
    # Run the game
    game = StarRoadGame()
    game.run()
