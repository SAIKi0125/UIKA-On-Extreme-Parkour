from legged_gym.envs.base.legged_robot_config import LeggedRobotCfg, LeggedRobotCfgPPO


class UIKAParkourCfg(LeggedRobotCfg):
    class init_state(LeggedRobotCfg.init_state):
        pos = [-0.8, 0.5, 0.35]  # x,y,z [m]
        default_joint_angles = {
            'FL_hip_joint': -0.7,
            'FL_thigh_joint': 0.2,
            'FL_calf_joint': 0.7,
            'FR_hip_joint': 0.7,
            'FR_thigh_joint': -0.2,
            'FR_calf_joint': -0.7,
            'RL_hip_joint': 0.7,
            'RL_thigh_joint': 0.2,
            'RL_calf_joint': 0.7,
            'RR_hip_joint': -0.7,
            'RR_thigh_joint': -0.2,
            'RR_calf_joint': -0.7,

            # 'FL_hip_joint': -0.76,
            # 'FL_thigh_joint': 0.14,
            # 'FL_calf_joint': 0.4,
            # 'FR_hip_joint': 0.76,
            # 'FR_thigh_joint': -0.14,
            # 'FR_calf_joint': -0.4,
            # 'RL_hip_joint': 0.68,
            # 'RL_thigh_joint': 0.2,
            # 'RL_calf_joint': 0.4,
            # 'RR_hip_joint': -0.68,
            # 'RR_thigh_joint': -0.2,
            # 'RR_calf_joint': -0.4,
        }

    class control(LeggedRobotCfg.control):
        control_type = 'P'
        stiffness = {'joint': 20.0}
        damping = {'joint': 0.5}
        action_scale = 0.25
        decimation = 4

    class asset(LeggedRobotCfg.asset):
        file = '{LEGGED_GYM_ROOT_DIR}/resources/robots/uika/urdf/uika.urdf'
        foot_name = 'foot'
        penalize_contacts_on = ['thigh', 'calf', 'base']
        terminate_after_contacts_on = ['base']
        self_collisions = 1
        collapse_fixed_joints = False

    class domain_rand(LeggedRobotCfg.domain_rand):
        randomize_motor = False
        motor_strength_range = [1.0, 1.0]

    class rewards(LeggedRobotCfg.rewards):
        soft_dof_pos_limit = 1.0
        base_height_target = 0.25


class UIKAParkourCfgPPO(LeggedRobotCfgPPO):
    class algorithm(LeggedRobotCfgPPO.algorithm):
        entropy_coef = 0.01

    class runner(LeggedRobotCfgPPO.runner):
        run_name = ''
        experiment_name = 'parkour_uika'
