<a id="section-1-3"></a>

# 1.3 Start the Environment Server

[简体中文](../../zh/getting-started/environment-server.md)

[Contents](../../DOCUMENTATION_EN.md) · [Previous: 1.2 Drive in the browser](web-controller.md) · [Next: 1.4 Run Expert iLQR](expert-ilqr.md)

AD policies and StreetWorld often require incompatible dependencies. Run them in separate Python environments and connect the simulation and inference processes through inter-process communication.
To control StreetWorld with your own AD policy, start the simulation as an Environment Server. The server loads scenes, renders camera images, and runs vehicle dynamics. The AD policy runs in another process, receives observations through gRPC, and submits its predicted trajectory.

[env_server.py](../../../streetworld/examples/env_server.py) provides a terminal interface for selecting scenes by category. To run a fixed scene list, use [env_server_scene_config.py](#scene-list-server) below.

## Start the server

From the repository root, run this command in the environment where StreetWorld is installed:

```bash
conda activate streetworld
python -m streetworld.examples.env_server \
  --host 127.0.0.1 --port 50052 \
  --web-host 127.0.0.1 --web-port 18080
```

Select nuScenes in the terminal, then choose scene conditions by categories such as road area, traffic density, time, and weather. Move with the up and down arrows, press Enter to select or deselect an item, and choose at least one option in each category. Move to Continue and press Enter to proceed to the next page. The server runs the matching scenes after all categories have been selected.

The server listens on `127.0.0.1:50052` for client requests. Synchronous mode is the default: simulation advances one environment step for each `step()` request.

## Connect a client

Check the connection with the following client. This example assumes a nuScenes or Waymo server using the default trajectory configuration. Run it from the StreetWorld root in another terminal:

```bash
conda activate streetworld
python - <<'PY'
import numpy as np
from streetworld.envs.grpc_client_env import GrpcClientEnv

env = GrpcClientEnv("127.0.0.1", 50052, timeout_sec=360.0)
try:
    observation, info = env.reset()
    # Six forward target points, with the current vehicle position as the origin.
    trajectory = np.array([[0.5 * i, 0.0] for i in range(1, 7)], dtype=np.float32)
    observation, reward, terminated, truncated, info = env.step(trajectory)
    print(info["scene_name"], reward, terminated, truncated)
finally:
    env.close()
PY
```

The client loads a scene with `reset()`, submits a manually constructed trajectory, and prints the scene name, reward, and termination flags. The default server interprets the six points as future positions spaced `0.5 s` apart and advances simulation by 0.5 s.

To connect a model, replace `trajectory` with the `trajectory` predicted from `observation` and call `step()` in a loop. After a scene ends, call `reset()` to load the next one. See the [Policy Launcher appendix](../launchers/common.md) for supported models, dependencies, weights, and commands.

## During a run

Open `http://127.0.0.1:18080` to view camera images and vehicle state. At startup, the page shows `Waiting for policy reset/step...`; images appear after the client's first `step()` call. Videos are saved in videos/.

Clients connect to the gRPC address; the browser uses the web address. The server continues waiting for requests after this client exits. Press `Ctrl-C` in the server terminal to close it.

## env_server.py arguments

| Parameters | Default | Purpose |
| --- | --- | --- |
| `--host`, `--port` | `127.0.0.1`, `50052` | StreetWorld gRPC address used by the client |
| `--web-host`, `--web-port` | `127.0.0.1`, `18080` | Web address for viewing simulation images |
| `--ad-policy-config` | `default` | Model configuration; use `latent_transfuser` for Latent TransFuser and `alpamayo` for Alpamayo |
| `--video-output-dir` | `videos` | Video output directory |
| `--async-mode` | Disabled | Advances simulation during model inference; see [Synchronous and asynchronous execution](../guides/architecture.md#section-2-6) |
| `--nurec-grpc-host`, `--nurec-grpc-port` | `127.0.0.1`, `8080` | NuRec rendering service address when NuRec is selected |
| `--nurec-grpc-timeout` | `600.0 s` | Timeout for NuRec rendering requests |

<a id="scene-list-server"></a>

## Specify a scene list

Use [env_server_scene_config.py](../../../streetworld/examples/env_server_scene_config.py) to run scenes in a fixed order. The repository includes a nuScenes scene list, [nuscene_list.txt](../../../streetworld/examples/nuscene_list.txt):

```bash
python -m streetworld.examples.env_server_scene_config \
  --scene-config streetworld/examples/nuscene_list.txt --dataset nuscenes \
  --host 127.0.0.1 --port 50052 \
  --web-host 127.0.0.1 --web-port 18080
```

`env_server_scene_config.py` accepts these arguments:

| Parameters | Default | Purpose |
| --- | --- | --- |
| `--scene-config` / `-c` | Required | Scene list text file with one scene ID per line |
| `--dataset` | Required | `nuscenes`, `waymo`, or `nurec` |
| `--host`, `--port` | `127.0.0.1`, `50052` | StreetWorld gRPC address used by the client |
| `--web-host`, `--web-port` | `127.0.0.1`, `18080` | Web address for viewing simulation images |
| `--ad-policy-config` | `default` | Model configuration; use `latent_transfuser` for Latent TransFuser and `alpamayo` for Alpamayo |
| `--video-output-dir` | `videos` | Video output directory |
| `--async-mode` | Disabled | Advances simulation during model inference; see [Synchronous and asynchronous execution](../guides/architecture.md#section-2-6) |
| `--nurec-grpc-host`, `--nurec-grpc-port` | `127.0.0.1`, `8080` | NuRec rendering service address when NuRec is selected |
| `--nurec-grpc-timeout` | `600.0 s` | Timeout for NuRec rendering requests |

nuScenes and Waymo use the default ST Renderer. NuRec requires a separate rendering service; see [NuRec setup](../guides/rendering-backends.md#nurec).

---

[Contents](../../DOCUMENTATION_EN.md) · [Previous: 1.2 Drive in the browser](web-controller.md) · [Next: 1.4 Run Expert iLQR](expert-ilqr.md)
