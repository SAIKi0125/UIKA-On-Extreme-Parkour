import isaacgym  # noqa: F401
import torch

from legged_gym.envs import *  # noqa: F401,F403
from legged_gym.utils import get_args, task_registry


def main():
    args = get_args()
    if not args.task:
        args.task = "uika"

    env_cfg, _ = task_registry.get_cfgs(name=args.task)

    env_cfg.env.num_envs = 1 if args.num_envs is None else args.num_envs
    env_cfg.terrain.mesh_type = "trimesh"
    env_cfg.terrain.num_rows = 5 if args.rows is None else args.rows
    env_cfg.terrain.num_cols = 5 if args.cols is None else args.cols
    env_cfg.terrain.curriculum = False
    env_cfg.terrain.max_init_terrain_level = 0
    if hasattr(env_cfg.terrain, "terrain_dict") and "parkour_flat" in env_cfg.terrain.terrain_dict:
        env_cfg.terrain.terrain_dict = {k: 0.0 for k in env_cfg.terrain.terrain_dict}
        env_cfg.terrain.terrain_dict["parkour_flat"] = 1.0
        env_cfg.terrain.terrain_proportions = list(env_cfg.terrain.terrain_dict.values())
    env_cfg.terrain.max_init_terrain_level = min(
        env_cfg.terrain.max_init_terrain_level, env_cfg.terrain.num_rows - 1
    )

    env_cfg.depth.use_camera = False
    env_cfg.domain_rand.push_robots = False
    env_cfg.domain_rand.randomize_friction = True
    env_cfg.domain_rand.randomize_base_mass = False
    env_cfg.domain_rand.randomize_base_com = False
    env_cfg.domain_rand.randomize_motor = False
    env_cfg.terrain.height = [0.0, 0.0]

    print("=" * 80)
    print(f"Creating env for task={args.task}")
    print(f"terrain mesh_type={env_cfg.terrain.mesh_type}")
    print(f"num_envs={env_cfg.env.num_envs}, rows={env_cfg.terrain.num_rows}, cols={env_cfg.terrain.num_cols}")
    print(f"urdf={env_cfg.asset.file}")
    print("=" * 80)

    env, _ = task_registry.make_env(name=args.task, args=args, env_cfg=env_cfg)

    print(f"num_dof={env.num_dof}, num_bodies={env.num_bodies}")
    print("dof names:", env.dof_names)

    body_names = env.gym.get_actor_rigid_body_names(env.envs[0], env.actor_handles[0])
    feet_names = [name for name in body_names if "foot" in name]
    print("feet bodies:", feet_names)
    feet_index_to_name = {int(idx): body_names[int(idx)] for idx in env.feet_indices.tolist()}
    print("feet index -> body name:", feet_index_to_name)
    print("feet_indices tensor:", env.feet_indices.tolist())

    steps = 50000 if not args.headless else 200
    print(f"Stepping {steps} frames with zero actions...")
    feet_fz_sum = torch.zeros(len(env.feet_indices), device=env.device)
    feet_contact_count = torch.zeros(len(env.feet_indices), device=env.device)

    for i in range(steps):
        actions = torch.zeros(env.num_envs, env.num_actions, device=env.device)
        env.step(actions)

        fz = env.contact_forces[:, env.feet_indices, 2]
        feet_fz_sum += fz.mean(dim=0)
        feet_contact_count += (fz > 10.0).float().mean(dim=0)

        if (i + 1) % 100 == 0:
            print(f"step {i + 1}/{steps}")
            avg_fz = (feet_fz_sum / (i + 1)).detach().cpu().tolist()
            contact_ratio = (feet_contact_count / (i + 1)).detach().cpu().tolist()
            print("avg foot Fz so far:", {feet_names[k]: round(avg_fz[k], 3) for k in range(len(feet_names))})
            print("foot contact ratio so far:", {feet_names[k]: round(contact_ratio[k], 3) for k in range(len(feet_names))})

            jid = env.lookat_id
            q_rad = env.dof_pos[jid].detach().cpu()
            q_deg = torch.rad2deg(q_rad)
            print("joint(rad):", {n: round(v.item(), 3) for n, v in zip(env.dof_names, q_rad)})
            print("joint(deg):", {n: round(v.item(), 1) for n, v in zip(env.dof_names, q_deg)})

    print("URDF load + env step smoke test passed.")


if __name__ == "__main__":
    main()
