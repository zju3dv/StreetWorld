from streetworld.policy.env_input_ilqr_policy import EnvInputILQRPolicy


ALPAMAYO_CONFIG = dict(
    decision_repeat=5,
    project_trajectory_on_camera="camera_front_wide_120fov",
    actor_config=dict(
        policy=EnvInputILQRPolicy,
        policy_config=dict(
            trajectory_dt=0.1,
            control_dt=0.1,
            smooth=False,
            max_acceleration=3.0,
        ),
    ),
)
