import os
import faulthandler

import isaacgym  # noqa: F401
import torch

from legged_gym.envs import *  # noqa: F401,F403
from legged_gym.utils import get_args, task_registry
from legged_gym.utils import webviewer


def get_load_path(root, checkpoint=-1, model_name_include="model"):
    if checkpoint == -1:
        models = [file for file in os.listdir(root) if model_name_include in file]
        models.sort(key=lambda m: "{0:0>15}".format(m))
        model = models[-1]
        checkpoint = model.split("_")[-1].split(".")[0]
    else:
        model = f"model_{checkpoint}.pt"
    return model, checkpoint


def play(args):
    if args.web:
        web_viewer = webviewer.WebViewer()

    faulthandler.enable()
    log_pth = "../../logs/{}/".format(args.proj_name) + args.exptid

    env_cfg, train_cfg = task_registry.get_cfgs(name=args.task)

    if args.nodelay:
        env_cfg.domain_rand.action_delay_view = 0

    env_cfg.env.num_envs = args.num_envs if args.num_envs is not None else (4 if not args.save else 64)
    env_cfg.env.episode_length_s = 60
    env_cfg.commands.resampling_time = 60

    # Force flat-terrain play while keeping parkour pipeline valid.
    env_cfg.terrain.mesh_type = "trimesh"
    env_cfg.terrain.curriculum = False
    env_cfg.terrain.max_init_terrain_level = 0
    env_cfg.terrain.num_rows = args.rows if args.rows is not None else 5
    env_cfg.terrain.num_cols = args.cols if args.cols is not None else 5
    env_cfg.terrain.height = [0.0, 0.0]

    if hasattr(env_cfg.terrain, "terrain_dict"):
        env_cfg.terrain.terrain_dict = {k: 0.0 for k in env_cfg.terrain.terrain_dict}
        if "parkour_flat" in env_cfg.terrain.terrain_dict:
            env_cfg.terrain.terrain_dict["parkour_flat"] = 1.0
        elif "smooth flat" in env_cfg.terrain.terrain_dict:
            env_cfg.terrain.terrain_dict["smooth flat"] = 1.0
        else:
            first_key = next(iter(env_cfg.terrain.terrain_dict.keys()))
            env_cfg.terrain.terrain_dict[first_key] = 1.0
        env_cfg.terrain.terrain_proportions = list(env_cfg.terrain.terrain_dict.values())

    env_cfg.depth.angle = [0, 1]
    env_cfg.noise.add_noise = True
    env_cfg.domain_rand.randomize_friction = True
    env_cfg.domain_rand.push_robots = False
    env_cfg.domain_rand.randomize_base_mass = False
    env_cfg.domain_rand.randomize_base_com = False

    env, _ = task_registry.make_env(name=args.task, args=args, env_cfg=env_cfg)
    obs = env.get_observations()

    if args.web:
        web_viewer.setup(env)

    train_cfg.runner.resume = True
    ppo_runner, train_cfg, log_pth = task_registry.make_alg_runner(
        log_root=log_pth,
        env=env,
        name=args.task,
        args=args,
        train_cfg=train_cfg,
        return_log_dir=True,
    )

    if args.use_jit:
        path = os.path.join(log_pth, "traced")
        model, checkpoint = get_load_path(root=path, checkpoint=args.checkpoint)
        path = os.path.join(path, model)
        print("Loading jit for policy:", path)
        policy_jit = torch.jit.load(path, map_location=env.device)
    else:
        policy = ppo_runner.get_inference_policy(device=env.device)

    infos = {}
    infos["depth"] = env.depth_buffer.clone().to(ppo_runner.device)[:, -1] if ppo_runner.if_depth else None

    for _ in range(10 * int(env.max_episode_length)):
        if args.use_jit:
            obs_jit = torch.cat(
                (
                    obs.detach()[:, : env_cfg.env.n_proprio + env_cfg.env.n_priv],
                    obs.detach()[:, -env_cfg.env.history_len * env_cfg.env.n_proprio :],
                ),
                dim=1,
            )
            actions = policy_jit(obs_jit)
        else:
            actions = policy(obs.detach(), hist_encoding=True, scandots_latent=None)

        obs, _, _, _, infos = env.step(actions.detach())

        if args.web:
            web_viewer.render(
                fetch_results=True,
                step_graphics=True,
                render_all_camera_sensors=True,
                wait_for_page_load=True,
            )

        print(
            "time:",
            env.episode_length_buf[env.lookat_id].item() / 50,
            "cmd vx",
            env.commands[env.lookat_id, 0].item(),
            "actual vx",
            env.base_lin_vel[env.lookat_id, 0].item(),
        )


if __name__ == "__main__":
    args = get_args()
    play(args)
