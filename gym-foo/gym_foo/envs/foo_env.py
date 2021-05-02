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
        self.masspole1 = 0.1
        self.masspole2 = 0.1
        self.masspole3 = 0.1
        self.masspole4 = 0.1
        self.masspole = self.masspole1 + self.masspole2 + self.masspole3 + self.masspole4 
        self.total_mass = (self.masspole+ self.masscart)
        self.length = 0.5  # actually half the pole's length
        self.polemass_length = (self.masspole * self.length)
        self.force_mag = 10.0
        self.tau = 0.02  # seconds between state updates
        self.kinematics_integrator = 'euler'

        # Angle at which to fail the episode
        self.theta_threshold_radians = 12 * 2 * math.pi / 360
        self.x_threshold = 2.4

        # Angle limit set to 2 * theta_threshold_radians so failing observation
        # is still within bounds.
        high = np.array([self.x_threshold * 2,
                         np.finfo(np.float32).max,
                         self.theta_threshold_radians * 2,
                         np.finfo(np.float32).max],
                        dtype=np.float32)

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

        x, x_dot, theta1, theta1_dot, theta2, theta2_dot, theta3, theta3_dot, theta4, theta4_dot= self.state

        force = self.force_mag if action == 1 else -self.force_mag
        costheta = math.cos(theta1)
        sintheta = math.sin(theta1)

        # equations to derive 
        temp = (force + self.polemass_length * theta1_dot ** 2 * sintheta) / self.total_mass
        thetaacc = (self.gravity * sintheta - costheta * temp) / (self.length  *(4.0 / 3.0 - self.masspole * costheta ** 2 / self.total_mass))
        xacc = temp - self.polemass_length * thetaacc * costheta / self.total_mass  

        if self.kinematics_integrator == "euler":
            x = x + self.tau * x_dot
            x_dot = x_dot + self.tau * xacc
            theta1 = theta1 + self.tau * theta1_dot
            theta2 = theta2 + self.tau * theta2_dot
            theta3 = theta3 + self.tau * theta3_dot
            theta4 = theta4 + self.tau * theta4_dot
            theta1_dot = theta1_dot + self.tau * thetaacc
            theta2_dot = theta2_dot + self.tau * thetaacc
            theta3_dot = theta3_dot + self.tau * thetaacc
            theta4_dot = theta4_dot + self.tau * thetaacc

        else:  
            x_dot = x_dot + self.tau * xacc
            x = x + self.tau * x_dot
            theta1_dot = theta1_dot + self.tau * thetaacc
            theta1 = theta1 + self.tau * theta_dot

        self.state = (x, x_dot, theta1, theta1_dot, theta2, theta2_dot, theta3, theta3_dot, theta4, theta4_dot)
    
        done = bool(
            x < - self.x_threshold
            or x > self.x_threshold
            or theta1 < - self.theta_threshold_radians
            or theta1 > self.theta_threshold_radians
            )

        if not done:
            reward = 1.0
        elif self.steps_beyond_done is None:
            # Pole just fell!
            self.steps_beyond_done = 0
            reward = 1.0
        else:
            if self.steps_beyond_done == 0:
                print(
                    "You are calling 'step()' even though this "
                    "environment has already returned done = True. You "
                    "should always call 'reset()' once you receive 'done = "
                    "True' -- any further steps are undefined behavior."
                )
            self.steps_beyond_done += 1
            reward = 0.0



        return np.array(self.state), reward, done, {}    

    def reset(self):
        self.state = self.np_random.uniform(low=-0.05, high=0.05, size=(10,))
        self.steps_beyond_done = None
        return np.array(self.state)

    def render(self, mode='human'):
        screen_width = 1000
        screen_height = 600

        world_width = self.x_threshold * 2
        scale = screen_width/world_width
        carty = 100  # TOP OF CART
        polewidth = 10.0
        polelen = scale * (2 * self.length)
        cartwidth = 50.0
        cartheight = 30.0

        if self.viewer is None:
            from gym.envs.classic_control import rendering
            self.viewer = rendering.Viewer(screen_width, screen_height)
            l, r, t, b = -cartwidth / 2, cartwidth / 2, cartheight / 2, -cartheight / 2
            axleoffset = cartheight / 4.0
            cart = rendering.FilledPolygon([(l, b), (l, t), (r, t), (r, b)])
            self.carttrans = rendering.Transform()
            cart.add_attr(self.carttrans)
            self.viewer.add_geom(cart)
            l, r, t, b = -polewidth / 2, polewidth / 2, polelen - polewidth / 2, -polewidth / 2
            pole1 = rendering.FilledPolygon([(l, b), (l, t), (r, t), (r, b)])
            pole2 = rendering.FilledPolygon([(l, 2*b), (l, 2*t), (r, 2*t), (r, 2*b)])
            pole3 = rendering.FilledPolygon([(l, 3*b), (l, 3*t), (r, 3*t), (r, 3*b)])
            pole4 = rendering.FilledPolygon([(l, 4*b), (l, 4*t), (r, 4*t), (r, 4*b)])
            pole1.set_color(.8, .6, .3)
            pole2.set_color(.7, .5, .5)
            pole3.set_color(.6, .4, .6)
            pole4.set_color(.5, .3, .8)
            self.poletrans = rendering.Transform(translation=(0, axleoffset))
            pole1.add_attr(self.poletrans)
            pole1.add_attr(self.carttrans)
            pole2.add_attr(self.poletrans)
            pole3.add_attr(self.poletrans)
            pole4.add_attr(self.poletrans)
            pole2.add_attr(self.carttrans)
            pole3.add_attr(self.carttrans)
            pole4.add_attr(self.carttrans)
            self.viewer.add_geom(pole1)
            self.viewer.add_geom(pole2)
            self.viewer.add_geom(pole3)
            self.viewer.add_geom(pole4)
            self.axle = rendering.make_circle(polewidth/2)
            self.axle.add_attr(self.poletrans)
            self.axle.add_attr(self.carttrans)
            self.axle.set_color(.5, .5, .8)
            self.viewer.add_geom(self.axle)
            self.track = rendering.Line((0, carty), (screen_width, carty))
            self.track.set_color(0, 0, 0)
            self.viewer.add_geom(self.track)

            self._pole_geom = pole1

        if self.state is None:
            return None

        # Edit the pole polygon vertex
        pole = self._pole_geom
        l, r, t, b = -polewidth / 2, polewidth / 2, polelen - polewidth / 2, -polewidth / 2
        pole1.v = [(l, b), (l, t), (r, t), (r, b)]

        x = self.state
        cartx = x[0] * scale + screen_width / 2.0  # MIDDLE OF CART
        self.carttrans.set_translation(cartx, carty)
        self.poletrans.set_rotation(-x[2])

        return self.viewer.render(return_rgb_array=mode == 'rgb_array')

       

    def close(self):
        if self.viewer:
            self.viewer.close()
            self.viewer = None
    






