import argparse
import math
import os

import numpy as np
from isaacgym import gymapi


def build_parser():
    parser = argparse.ArgumentParser(description="URDF viewer + joint angle diagnostics")
    parser.add_argument("--asset-root", type=str, required=True, help="Directory containing the URDF and meshes")
    parser.add_argument("--asset-file", type=str, required=True, help="URDF file name, e.g. robot.urdf")
    parser.add_argument("--fix-base", action="store_true", help="Fix robot base link")
    parser.add_argument("--print-every", type=int, default=120, help="Print joint angles every N sim steps")
    parser.add_argument("--move", action="store_true", help="Apply sinusoidal position targets to joints")
    parser.add_argument("--amp", type=float, default=0.25, help="Sin motion amplitude in rad")
    parser.add_argument("--freq", type=float, default=0.5, help="Sin motion frequency in Hz")
    return parser


def main():
    args = build_parser().parse_args()

    gym = gymapi.acquire_gym()

    sim_params = gymapi.SimParams()
    sim_params.dt = 1.0 / 60.0
    sim_params.substeps = 4
    sim_params.up_axis = gymapi.UP_AXIS_Z
    sim_params.gravity = gymapi.Vec3(0.0, 0.0, -9.8)
    sim_params.use_gpu_pipeline = False
    sim_params.physx.use_gpu = True
    sim_params.physx.solver_type = 1
    sim_params.physx.num_position_iterations = 6
    sim_params.physx.num_velocity_iterations = 0
    sim_params.physx.bounce_threshold_velocity = 0.2
    sim_params.physx.max_depenetration_velocity = 100.0
    sim_params.physx.contact_offset = 0.01
    sim_params.physx.rest_offset = 0.0

    sim = gym.create_sim(0, 0, gymapi.SIM_PHYSX, sim_params)
    if sim is None:
        raise RuntimeError("Failed to create sim")

    plane_params = gymapi.PlaneParams()
    plane_params.normal = gymapi.Vec3(0, 0, 1)
    plane_params.distance = 0.0
    plane_params.static_friction = 1.0
    plane_params.dynamic_friction = 1.0
    plane_params.restitution = 0.0
    gym.add_ground(sim, plane_params)

    asset_options = gymapi.AssetOptions()
    asset_options.fix_base_link = args.fix_base
    asset_options.armature = 0.01
    asset_options.flip_visual_attachments = False
    asset_options.use_mesh_materials = True
    asset_options.replace_cylinder_with_capsule = False

    if not os.path.isdir(args.asset_root):
        raise FileNotFoundError(f"asset_root not found: {args.asset_root}")

    asset = gym.load_asset(sim, args.asset_root, args.asset_file, asset_options)
    if asset is None:
        raise RuntimeError(f"Failed to load asset: root={args.asset_root}, file={args.asset_file}")

    env = gym.create_env(sim, gymapi.Vec3(-1.0, 0.0, -1.0), gymapi.Vec3(1.0, 1.0, 1.0), 1)
    pose = gymapi.Transform()
    pose.p = gymapi.Vec3(0.0, 0.0, 0.5)
    actor = gym.create_actor(env, asset, pose, "Robot", 0, 1)

    dof_names = gym.get_actor_dof_names(env, actor)
    num_dof = len(dof_names)
    dof_props = gym.get_actor_dof_properties(env, actor)

    # Position-control for all joints so we can command targets.
    dof_props["driveMode"].fill(gymapi.DOF_MODE_POS)
    dof_props["stiffness"].fill(40.0)
    dof_props["damping"].fill(1.0)
    gym.set_actor_dof_properties(env, actor, dof_props)

    lower = dof_props["lower"].copy()
    upper = dof_props["upper"].copy()
    home = np.clip(np.zeros(num_dof, dtype=np.float32), lower, upper)

    gym.set_actor_dof_position_targets(env, actor, home)

    print("=" * 90)
    print(f"Loaded: {os.path.join(args.asset_root, args.asset_file)}")
    print(f"num_dof={num_dof}")
    print("Joint limits (rad):")
    for i, name in enumerate(dof_names):
        print(f"  {name:<20} [{lower[i]:+.3f}, {upper[i]:+.3f}]")
    print("=" * 90)

    viewer = gym.create_viewer(sim, gymapi.CameraProperties())
    if viewer is None:
        raise RuntimeError("Failed to create viewer")
    gym.viewer_camera_look_at(viewer, None, gymapi.Vec3(2.0, 2.0, 1.5), gymapi.Vec3(0.0, 0.0, 0.6))

    gym.prepare_sim(sim)

    dof_state_tensor = gym.acquire_dof_state_tensor(sim)

    step = 0
    while not gym.query_viewer_has_closed(viewer):
        if args.move:
            t = step * sim_params.dt
            target = home + args.amp * np.sin(2.0 * math.pi * args.freq * t)
            target = np.clip(target, lower + 1e-3, upper - 1e-3)
            gym.set_actor_dof_position_targets(env, actor, target.astype(np.float32))

        gym.simulate(sim)
        gym.fetch_results(sim, True)
        gym.refresh_dof_state_tensor(sim)

        if step % args.print_every == 0:
            dof_state = np.array(dof_state_tensor, copy=False).reshape(-1, 2)
            q = dof_state[:num_dof, 0]
            q_deg = np.degrees(q)
            print(f"\nstep={step}")
            for i, name in enumerate(dof_names):
                print(f"  {name:<20} q={q[i]:+7.3f} rad ({q_deg[i]:+7.2f} deg)")

        gym.step_graphics(sim)
        gym.draw_viewer(viewer, sim, True)
        gym.sync_frame_time(sim)
        step += 1

    gym.destroy_viewer(viewer)
    gym.destroy_sim(sim)


if __name__ == "__main__":
    main()
