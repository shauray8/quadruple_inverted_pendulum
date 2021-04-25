import gym
import numpy as np
import math
from gym import spaces
from gym.utils import seeding 

class QuadSwingUp(gym.Env):
    """
    Description:
        A pole is attached by a joint to a cart with a series of 3 more
        attached to it with 3 other joints which moves along
        a frictionless track. The pendulum starts at rest facing down, and the goal is to
        make the thing go upright which is an angle 0 degree (starts at 180 degree from the goal)
        and prevent it from falling over by increasing and reducing the cart's
        velocity.

    Observation:
        Type: Box(4)
        Num     Observation                 Min                     Max
        0       Cart Position               -4.8                    4.8
        1       Cart Velocity               -Inf                    Inf
        2       Pole 1 Angle                -0.418 rad (-24 deg)    0.418 rad (24 deg)
        3       Pole 1 Angular Velocity     -Inf                    Inf
        2       Pole 2 Angle                -0.418 rad (-24 deg)    0.418 rad (24 deg)
        4       Pole 2 Angular Velocity     -Inf                    Inf
        5       Pole 3 Angle                -0.418 rad (-24 deg)    0.418 rad (24 deg)
        7       Pole 3 Angular Velocity     -Inf                    Inf
        8       Pole 4 Angle                -0.418 rad (-24 deg)    0.418 rad (24 deg)
        9       Pole 4 Angular Velocity     -Inf                    Inf

    Actions:
        Type: Discrete(2)
        Num   Action
        0     Push cart to the left
        1     Push cart to the right
        Note: The amount the velocity that is reduced or increased is not
        fixed; it depends on the angle the pole is pointing. This is because
        the center of gravity of the pole increases the amount of energy needed
        to move the cart underneath it
    Reward:
        Reward is 1 for every step taken between angle [0,12] including the termination step
    Starting State:
        All observations are assigned a uniform random value in [-0.05..0.05]
    Episode Termination:
        Pole angle is less than 12 degrees for more than 5 sec
        Cart Position is more than 2.4 (center of the cart reaches the edge of
        the display).
        Episode length is greater than 200.
        Solved Requirements:
        Considered solved when the average return is greater than or equal to
        195.0 over 100 consecutive trials.
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

        high = np.array([self.x_threshold * 2,
            np.finfo(np.float32).max,
            self.theta_threshold_radians * 2,
            np.finfo(np.float32).max],
            dtype = np.float32)

        self.action_space = spaces.Discrete(2)
        self.observation_space = spaces.Box(-high, high, dtype=np.float32)

        self.seed()
        self.viewer = None
        self.state = None

        self.steps_beyond_done = None

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def step(self, action):
        err_msg = "%r (%s) invalid" % (action, type(action))
        assert self.action_space.contains(action), err_msg

        x, x_dot, theta, theta_dot = self.state

        force = self.force_mag if action == 1 else -self.force_mag
        costheta = math.cos(theta)
        sintheta = math.sin(theta)

        temp = (force + self.polemass_length * theta_dot ** 2 * sintheta) / self.total_mass
        thetaacc = (self.gravity * sintheta - costheta * temp) / (self.length  *(4.0 / 3.0 - self.masspole * costheta ** 2 / self.total_mass))
        xacc = temp - self.polemass_length * thetaacc * costheta / self.total_mass  


    def reset(self):
        self.state = self.np_random.uniform(low=-0.05, high=0.05, size=(4,))
        self.steps_beyond_done = None
        return np.array(self.state)

    def render(self, mode="human"):
        pass

    def close(self):
        if self.viewer:
            self.viewer.close()
            self.viewer = None
    






