from gym.envs.registration import register

register(id="SwingUp-v0",
        entry_point="QuadSwingUp.envs:env")
