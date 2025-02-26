import arcade


PLAYER_MOVEMENT_SPEED : int = 5
"""Lateral speed of the player, in pixels per frame."""

PLAYER_GRAVITY = 1
"""Gravity applied to the player, in pixels per frame²."""

PLAYER_JUMP_SPEED = 18
"""Instant vertical speed for jumping, in pixels per frame."""

class GameView(arcade.View):
    """Main in-game view."""
    player_sprite: arcade.Sprite
    player_sprite_list: arcade.SpriteList[arcade.Sprite]
    wall_list: arcade.SpriteList[arcade.Sprite]
    coin_list: arcade.SpriteList[arcade.Sprite]
    physics_engine: arcade.PhysicsEnginePlatformer
    coin_sound: arcade.Sound
    jump_sound: arcade.Sound
    camera: arcade.camera.Camera2D

    def __init__(self) -> None:
        # Magical incantion: initialize the Arcade view
        super().__init__()

        # Choose a nice comfy background color
        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

        # Setup our game
        self.setup()

    def setup(self) -> None:
        """Set up the game here."""
        self.player_sprite = arcade.Sprite(
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png",
            center_x=64,
            center_y=128
        )
        self.player_sprite_list = arcade.SpriteList()
        self.player_sprite_list.append(self.player_sprite)
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.coin_list = arcade.SpriteList(use_spatial_hash=True)
        self.coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")

        for i in range(0, 1186, 64):
            self.wall_list.append(arcade.Sprite(
                ":resources:images/tiles/grassMid.png",
                center_x=i,
                center_y=32,
                scale=0.5
            ))
        
        for i in [256,512,769]:
            self.wall_list.append(arcade.Sprite(
                ":resources:images/tiles/boxCrate_double.png",
                center_x=i,
                center_y=96,
                scale=0.5
            ))

        
        for i in range(128, 1250, 256):
            self.coin_list.append(arcade.Sprite(
                ":resources:images/items/coinGold.png",
                center_x=i,
                center_y=96,
                scale=0.5
            ))

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            walls=self.wall_list,
            gravity_constant=PLAYER_GRAVITY
        )
        self.physics_engine.disable_multi_jump()
        self.camera = arcade.camera.Camera2D()


    def on_draw(self) -> None:
        """Render the screen."""
        self.clear() # always start with self.clear()   
        with self.camera.activate():
          self.wall_list.draw()
          self.coin_list.draw()
          self.player_sprite_list.draw()
          #self.wall_list.draw_hit_boxes()
          #self.coin_list.draw_hit_boxes()
          #self.player_sprite_list.draw_hit_boxes()
        

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Called when the user presses a key on the keyboard."""
        match key:
            case arcade.key.RIGHT:
                # start moving to the right
                self.player_sprite.change_x += PLAYER_MOVEMENT_SPEED
            case arcade.key.LEFT:
                # start moving to the left
                self.player_sprite.change_x -= PLAYER_MOVEMENT_SPEED
            case arcade.key.UP:
                if self.physics_engine.can_jump():
                    # jump by giving an initial vertical speed
                    self.player_sprite.change_y = PLAYER_JUMP_SPEED
                    arcade.play_sound(self.jump_sound)
            case arcade.key.ESCAPE:
                self.setup()

    def on_key_release(self, key: int, modifiers: int) -> None:
        """Called when the user releases a key on the keyboard."""
        match key:
            case arcade.key.RIGHT:
                # stop lateral movement
                self.player_sprite.change_x -= PLAYER_MOVEMENT_SPEED
            case arcade.key.LEFT:
                # stop lateral movement
                self.player_sprite.change_x += PLAYER_MOVEMENT_SPEED
    
    def on_update(self, delta_time: float) -> None:
        """Called once per frame, before drawing.

        This is where in-world time "advances", or "ticks".
        """
        self.physics_engine.update()
        self.camera.position = self.player_sprite.position # type: ignore

        for coin in arcade.check_for_collision_with_list(self.player_sprite, self.coin_list):
            arcade.play_sound(self.coin_sound)
            coin.remove_from_sprite_lists()