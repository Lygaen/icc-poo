import math
import arcade

class BetterCamera(arcade.Camera2D):
    """Better (aka. smooth) camera for arcade.
    """

    target: arcade.types.Point2
    """The target that the camera follows, in
    screen coordinates.
    """

    free_space: arcade.Rect
    """The free space rectangle in screen coordinates,
    that forces the camera to move when the player goes
    out of bounds of the said rect.
    """

    __lerp_time: float
    """The time for the last lerp. Used only internally.
    """
    
    __LERP_SMOOTH = 15
    """How smooth the camera should be when moving. Higher the smoother / slower.
    """
    __FREEZONE_FACTOR = 10
    """The scale factor of the freezone, higher the smaller the size
    relative to the window (2 -> 1/2 of the screen, 3 -> 1/3 ...)
    """

    def __init__(self) -> None:
        """Initializes the camera, pretty self-explainatory
        """

        super().__init__()

        self.__lerp_time = 0
        self.target = (0,0)
        self.free_space = arcade.types.XYRR(0, 0, 0, 0)
    
    def update(self, delta_time: float, target: arcade.types.Point2) -> None:
        """Updates the camera for the current frame, moving to the target
        if needed, interpolated for the current delta_time.

        Args:
            delta_time (float): The time between the last frame and this one
            target (arcade.types.Point2): the target of the camera in coordinates
        """
        self.target = self.project(target)

        self.free_space = arcade.types.XYRR(self._window.rect.center.x, self._window.rect.center_left.y,
                                             self._window.size[0] // self.__FREEZONE_FACTOR,
                                             -self._window.size[1] // self.__FREEZONE_FACTOR)

        # Could be using target parameter directly
        # but the advantage of unprojecting the target
        # is that it will be correctly project onto the world.
        # It allows us to implement later additional tweakings
        # more easily
        target_world = self.unproject(self.target)

        is_outside_x = (self.free_space.right < self.target.x) or (self.target.x < self.free_space.left)
        is_outside_y = (self.free_space.top > self.target.y) or (self.free_space.bottom < self.target.y)

        if is_outside_x or is_outside_y:
            self.__lerp_time += delta_time * (1/self.__LERP_SMOOTH)
            
            # Uses a sin for interpolation for better ~smoothness~
            self.position = self.position.lerp(arcade.Vec2(target_world.x, target_world.y), math.sin(self.__lerp_time))
        else:
            # We're inside, reset lerping
            self.__lerp_time = 0