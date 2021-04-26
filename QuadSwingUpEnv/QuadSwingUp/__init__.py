from gym.envs.registration import register

register(id="QuadSwingUp-v0",
        entry_point="QuadSwingUp.envs:env")
