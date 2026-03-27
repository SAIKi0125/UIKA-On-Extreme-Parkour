import os

import isaacgym  # noqa: F401
import wandb

from legged_gym import LEGGED_GYM_ENVS_DIR, LEGGED_GYM_ROOT_DIR
from legged_gym.envs import *  # noqa: F401,F403
from legged_gym.utils import get_args, task_registry


def train(args):
    args.headless = True
    log_pth = LEGGED_GYM_ROOT_DIR + "/logs/{}/".format(args.proj_name) + args.exptid
    os.makedirs(log_pth, exist_ok=True)

    if args.debug:
        mode = "disabled"
        args.rows = 10
        args.cols = 8
        args.num_envs = 64
    else:
        mode = "online"

    if args.no_wandb:
        mode = "disabled"

    wandb.init(
        project=args.proj_name,
        name=args.exptid,
        entity="saiki050125-e",
        group=args.exptid[:3],
        mode=mode,
        dir="../../logs",
    )
    wandb.save(LEGGED_GYM_ENVS_DIR + "/base/legged_robot_config.py", policy="now")
    wandb.save(LEGGED_GYM_ENVS_DIR + "/base/legged_robot.py", policy="now")

    env_cfg, _ = task_registry.get_cfgs(name=args.task)

    # Flat-ground training setup: keep parkour terrain pipeline (goals/reward path)
    # but only sample the flat parkour type and remove roughness amplitude.
    env_cfg.terrain.mesh_type = "trimesh"
    env_cfg.terrain.curriculum = False
    env_cfg.terrain.max_init_terrain_level = 0
    if args.rows is not None:
        env_cfg.terrain.num_rows = args.rows
    if args.cols is not None:
        env_cfg.terrain.num_cols = args.cols
    if args.num_envs is not None:
        env_cfg.env.num_envs = args.num_envs

    if hasattr(env_cfg.terrain, "terrain_dict") and "parkour_flat" in env_cfg.terrain.terrain_dict:
        env_cfg.terrain.terrain_dict = {k: 0.0 for k in env_cfg.terrain.terrain_dict}
        env_cfg.terrain.terrain_dict["parkour_flat"] = 1.0
        env_cfg.terrain.terrain_proportions = list(env_cfg.terrain.terrain_dict.values())

    env_cfg.terrain.height = [0.0, 0.0]

    env, _ = task_registry.make_env(name=args.task, args=args, env_cfg=env_cfg)
    ppo_runner, train_cfg = task_registry.make_alg_runner(
        log_root=log_pth,
        env=env,
        name=args.task,
        args=args,
    )
    ppo_runner.learn(num_learning_iterations=train_cfg.runner.max_iterations, init_at_random_ep_len=True)


if __name__ == "__main__":
    args = get_args()
    train(args)
