import gym
import numpy as np
import math
from gym import spaces
from gym.utils import seeding 

class QuadSwingUp(gym.Env):
    """
    features and stuff of the environment goes here !
    """
    metadata = {
            "render.modes": ["human", "rgb_array"],
            "video.frames_per_second": 50
            }

    def __init__(self):
        self.gravity = 9.8
        self.masscart = 1.0
        self.masspole = .1
        self.total_mass = (self.masspole + self.masscart)
        self.legth = .5   #pole's half length
        self.polemass_length = (self.masspole * self.length)
        self.force_mag = 10.0
        self.tau = 0.02   #seconnd between state update
        self.kinematics_integrator = 'euler'

        # Angle at which to fail the episode
        self.theta_threshold_radians = 12 * 2 * math.pi / 360
        self.x_threshold = 2.4


