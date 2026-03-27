import isaacgym  # noqa: F401
import torch

from legged_gym.envs import *  # noqa: F401,F403
from legged_gym.utils import get_args, task_registry


def _focus_joint_indices(dof_names):
    focus_prefix = ("FR_", "RR_")
    return [i for i, n in enumerate(dof_names) if n.startswith(focus_prefix)]


def play_test(args):
    env_cfg, train_cfg = task_registry.get_cfgs(name=args.task)

    env_cfg.env.num_envs = 1
    env_cfg.terrain.num_rows = 5
    env_cfg.terrain.num_cols = 5
    env_cfg.terrain.curriculum = False
    env_cfg.terrain.max_init_terrain_level = min(env_cfg.terrain.max_init_terrain_level, env_cfg.terrain.num_rows - 1)

    env_cfg.domain_rand.push_robots = False
    env_cfg.domain_rand.randomize_friction = True
    env_cfg.domain_rand.randomize_base_mass = False
    env_cfg.domain_rand.randomize_base_com = False
    env_cfg.domain_rand.randomize_motor = False

    env, _ = task_registry.make_env(name=args.task, args=args, env_cfg=env_cfg)
    obs = env.get_observations()

    train_cfg.runner.resume = True
    log_root = f"../../logs/{args.proj_name}/{args.exptid}"
    ppo_runner, train_cfg, log_dir = task_registry.make_alg_runner(
        log_root=log_root,
        env=env,
        name=args.task,
        args=args,
        train_cfg=train_cfg,
        return_log_dir=True,
    )
    print(f"Loaded run dir: {log_dir}")

    if hasattr(ppo_runner.alg, "depth_actor"):
        policy_fn = lambda x: ppo_runner.alg.depth_actor(x.detach(), hist_encoding=True, scandots_latent=None)
    else:
        policy = ppo_runner.get_inference_policy(device=env.device)
        policy_fn = lambda x: policy(x.detach(), hist_encoding=True, scandots_latent=None)

    focus_idx = _focus_joint_indices(env.dof_names)
    if not focus_idx:
        focus_idx = list(range(env.num_dof))

    print("=" * 100)
    print("Focus joints:", [env.dof_names[i] for i in focus_idx])
    print("Soft position limits used by training:")
    for i in focus_idx:
        lo = env.dof_pos_limits[i, 0].item()
        hi = env.dof_pos_limits[i, 1].item()
        tq = env.torque_limits[i].item()
        print(f"  {env.dof_names[i]:<14} pos[{lo:+.3f}, {hi:+.3f}]  torque_limit={tq:.3f}")
    print("=" * 100)

    body_names = env.gym.get_actor_rigid_body_names(env.envs[0], env.actor_handles[0])
    foot_map = {int(i): body_names[int(i)] for i in env.feet_indices.tolist()}
    print("feet index -> name:", foot_map)

    steps = 2000 if args.headless else 10000
    print_interval = 50
    limit_margin = 0.05

    for step in range(steps):
        actions = policy_fn(obs)
        obs, _, _, _, _ = env.step(actions.detach())

        if (step + 1) % print_interval != 0:
            continue

        env_id = env.lookat_id
        pos = env.dof_pos[env_id, focus_idx].detach().cpu()
        vel = env.dof_vel[env_id, focus_idx].detach().cpu()
        tor = env.torques[env_id, focus_idx].detach().cpu()
        act = actions[env_id, focus_idx].detach().cpu()
        lo = env.dof_pos_limits[focus_idx, 0].detach().cpu()
        hi = env.dof_pos_limits[focus_idx, 1].detach().cpu()
        tl = env.torque_limits[focus_idx].detach().cpu()

        fz = env.contact_forces[env_id, env.feet_indices, 2].detach().cpu()
        fz_dict = {foot_map[int(env.feet_indices[i].item())]: round(fz[i].item(), 3) for i in range(len(env.feet_indices))}

        print(f"\nstep {step + 1}/{steps}")
        print("foot Fz:", fz_dict)
        for k, j in enumerate(focus_idx):
            near_lo = (pos[k] - lo[k]).item() < limit_margin
            near_hi = (hi[k] - pos[k]).item() < limit_margin
            clipped = abs(tor[k].item()) > 0.98 * tl[k].item()
            print(
                f"{env.dof_names[j]:<14} "
                f"a={act[k].item():+6.3f} "
                f"q={pos[k].item():+7.3f} "
                f"dq={vel[k].item():+7.3f} "
                f"tau={tor[k].item():+7.3f}/{tl[k].item():.2f} "
                f"near_lo={int(near_lo)} near_hi={int(near_hi)} clip={int(clipped)}"
            )

    print("play_test finished.")


if __name__ == "__main__":
    args = get_args()
    if not args.task:
        args.task = "uika"
    play_test(args)
