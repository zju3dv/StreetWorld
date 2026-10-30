AUTOVLA_CONFIG = dict(
    actor_config=dict(warmup_step=4),
)

# Keep the original two seconds of expert warmup at a 0.1s control period.
AUTOVLA_CONFIG_0_1S = dict(actor_config=dict(warmup_step=20))
