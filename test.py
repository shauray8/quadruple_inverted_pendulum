import gym_foo
import gym
import time

env = gym.make("gym_foo:foo-v0")
env.reset()

done = False
if not done:
    action = 1
    a,b,done,j = env.step(action)
    print(a,b,done,j)
    env.render()
    time.sleep(10)
