#!/usr/bin/env python3

import gymnasium
from gymnasium.utils.env_checker import check_env
import numpy as np
import stable_baselines3
import torch

import redcap_xapp_sdk
import redcap_drl


class SmokeEnv(gymnasium.Env):
    observation_space = gymnasium.spaces.Box(low=0.0, high=1.0, shape=(1,), dtype=np.float32)
    action_space = gymnasium.spaces.Discrete(1)

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        return np.array([0.0], dtype=np.float32), {}

    def step(self, action):
        assert self.action_space.contains(action)
        return np.array([0.0], dtype=np.float32), 0.0, True, False, {}


def main() -> None:
    environment = SmokeEnv()
    check_env(environment)
    assert torch.__version__.split("+")[0] == "2.13.0"
    assert gymnasium.__version__ == "1.3.0"
    assert stable_baselines3.__version__ == "2.9.0"
    assert redcap_xapp_sdk.SM_RC_ID == 3
    assert redcap_drl.Client
    print("RUNTIME_SMOKE PASS")


if __name__ == "__main__":
    main()
