from constants import *

class Animator(object):
    """Handles frame-by-frame animations with speed and looping control.

    The `Animator` class allows you to manage frame animations by advancing 
    frames based on a given speed (frames per second). It also supports looping 
    of the animation once it completes.

    Attributes:
        frames (list): A list of frames representing the animation.
        current_frame (int): The index of the current frame being displayed.
        speed (int): The speed of the animation in frames per second.
        loop (bool): Whether the animation should loop when it reaches the end.
        dt (float): Time since the last frame was rendered
        finished (bool): Flag indicating whether the animation has completed 
    """

    def __init__(self, frames=None, speed=20, loop=True):
        if frames is None:
            frames = []
        self.frames = frames
        self.current_frame = 0
        self.speed = speed
        self.loop = loop
        self.dt = 0
        self.finished = False

    def reset(self):
        self.current_frame = 0
        self.finished = False

    def update(self, dt):
        if not self.finished:
            self.nextFrame(dt)
        if self.current_frame == len(self.frames):
            if self.loop:
                self.current_frame = 0
            else:
                self.finished = True
                self.current_frame -= 1

        return self.frames[self.current_frame]

    def nextFrame(self, dt):
        self.dt += dt
        if self.dt >= (1.0 / self.speed):
            self.current_frame += 1
            self.dt = 0
