<a id="chapter-7"></a>

# 7.1 Common launch procedure

[简体中文](../../zh/launchers/common.md)

[Contents](../../DOCUMENTATION_EN.md) · [Previous: 6.4 BaseRunnable](../reference/base-runnable.md) · [Next: 7.2 UniAD](uniad.md)

On this page

- [Control-input server for Latent TransFuser](#latent-control-server)
- [NuRec trajectory server for Alpamayo](#alpamayo-trajectory-server)

[policy_launcher.launch](../../../policy_launcher/launch.py) loads the model's NativeAgent before connecting to the server through GrpcClientEnv. It loops over reset, observation unpacking, predict_action, and step to run the server's scene queue. Model-loading failures occur before gRPC connection or scene reset.

Use one terminal for the [simulation environment](../getting-started/installation.md#section-1-1) and another for the model environment. Run both from the StreetWorld root. Model environments require Python 3.10 or later; Alpamayo requires 3.12. Shared client dependencies are NumPy, Gymnasium, grpcio, Protobuf, SciPy, and Pillow; install model dependencies separately.

Install the shared dependencies in the model environment:

```bash
python -m pip install numpy gymnasium grpcio protobuf scipy pillow
```

The shared CLI selects models with --model. It does not provide --checkpoint, --config, or --model-root; change file paths in the corresponding NativeAgent constructor settings.

```bash
python -m policy_launcher.launch --help
python -m policy_launcher.launch \
  --model vad --host 127.0.0.1 --port 50052 \
  --device cuda --timeout 360 --max-steps 1000
```

| Parameters | Default | Purpose and actual behavior |
| --- | --- | --- |
| --model | Required | One of the 17 entries in the [model list](../../DOCUMENTATION_EN.md#chapter-7) |
| --host | 127.0.0.1 | StreetWorld gRPC host |
| --port | 50052 | StreetWorld gRPC port |
| --device | cuda | Passed to most model constructors; the four OpenEMMA entries do not accept it |
| --timeout | 360 s | Step RPC timeout; reset uses twice this value, 720 s by default |
| --max-steps | 1000 | Client loop limit per scene; the environment may end earlier |
| --scene-name | None | Exits after the first scene when supplied; does not filter scenes by name. The server's scene_ids select scenes |

`--model` selects the model loaded by the client. Use `--ad-policy-config` to select the corresponding model configuration on the server.

| Launcher | Server configuration | Action and timing |
| --- | --- | --- |
| uniad, vad, genad, momad, stp3, opendrivevla, diffusiondrive, sparsedrive | default | Trajectory input; trajectory_dt, control_dt, and decision period all default to 0.5 s |
| autovla | autovla | 0.5 s trajectory; 4 expert warmup steps |
| epona | epona | 0.1 s trajectory, 0.5 s control and decision period; 10 expert warmup steps |
| openemma_* | openemma | 0.5 s trajectory; 10 expert warmup steps |
| latent_transfuser | `latent_transfuser` | `[steering, throttle_brake]`: steering and throttle/brake |
| alpamayo1, alpamayo1.5 | `alpamayo`; select a NuRec scene | Trajectory points spaced 0.1 s apart |

unpack_ad_observation reads gaussian, states, navigation, and surrounding, converts microsecond timestamps to seconds, and adds fields such as scene_token, cam_params, route_waypoints, and target_waypoint. Command values are right=0, left=1, straight=2. Each model's dataparser then processes images, transforms coordinates, and moves tensors to the model device.

The server runs synchronously by default, advancing one environment step after each inference. With async_mode, simulation continues during inference and step can return cached results; see [Synchronous and asynchronous execution](../guides/architecture.md#section-2-6). The client switches scenes at max_steps. If the environment has not reported termination, that scene is not included in ScenarioEnv's completed metrics.

<a id="latent-control-server"></a>

## Control-input server for Latent TransFuser

Run this command in the simulation environment, then select scenes by category. The server uses `EnvInputPolicy` to receive the model's steering and throttle/brake commands:

```bash
python -m streetworld.examples.env_server \
  --ad-policy-config latent_transfuser \
  --host 127.0.0.1 --port 50052 --web-port 18080
```

<a id="alpamayo-trajectory-server"></a>

## NuRec trajectory server for Alpamayo

Start the [NuRec rendering service](../guides/rendering-backends.md#nurec), then run this command in the simulation environment and select a NuRec scene. The `alpamayo` configuration uses iLQR to track trajectories, with both waypoint spacing and the control period set to `0.1 s`:

```bash
python -m streetworld.examples.env_server \
  --ad-policy-config alpamayo \
  --nurec-grpc-host 127.0.0.1 --nurec-grpc-port 8080 \
  --host 127.0.0.1 --port 50052 --web-port 18080
```

---

[Contents](../../DOCUMENTATION_EN.md) · [Previous: 6.4 BaseRunnable](../reference/base-runnable.md) · [Next: 7.2 UniAD](uniad.md)
