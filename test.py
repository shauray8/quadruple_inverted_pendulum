import gym_foo
import gym

env = gym.make("gym_foo:foo-v0")
env.reset()

done = False
if not done:
    action = 1
    env.step(action)
    env.render()
