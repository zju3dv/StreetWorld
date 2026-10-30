<a id="section-1-4"></a>

# 1.4 Run Expert iLQR

[简体中文](../../zh/getting-started/expert-ilqr.md)

[Contents](../../DOCUMENTATION_EN.md) · [Previous: 1.3 Start the Environment Server](environment-server.md) · [Next: 2. Architecture](../guides/architecture.md)

[drive_expert_ilqr.py](../../../streetworld/examples/drive_expert_ilqr.py) shows vehicle simulation while following the expert trajectory. It takes the recorded ego trajectory from a scene and uses iLQR to compute steering and throttle/brake commands that track it.

## Run

Complete the installation and data download in [1.1](installation.md), then run from the StreetWorld root using the provided nuScenes scene list, [nuscene_list.txt](../../../streetworld/examples/nuscene_list.txt):

```bash
conda activate streetworld
python -m streetworld.examples.drive_expert_ilqr \
  --scene-config streetworld/examples/nuscene_list.txt \
  --dataset nuscenes \
  --max-steps 1000
```

Each line contains a scene ID. For example, `0001` corresponds to `data/benchmark/nuscenes/0001.npz`, with maps loaded from `map_cache.npz` in the same directory. Scenes run in list order. Custom scene lists should also use UTF-8 with no blank lines or comments.

## During a run

The vehicle starts driving automatically. Open `http://127.0.0.1:8080` to view camera images and vehicle state; videos are saved in `videos/`. The terminal prints each scene name and trajectory parameters. Normal termination or truncation also prints the step count, timestamp, and termination reason.

The script proceeds to the next scene and closes the environment after the final one. Each scene executes at most `--max-steps` calls to `step()`; reaching the destination, a collision, or the environment step limit may end it earlier. Press `Ctrl-C` to exit early.

The expert Policy takes up to 30 future trajectory points per update. Both trajectory sampling and control use a `0.1 s` interval. On `env.step(None)`, ExpertILQRPolicy generates a target trajectory from the recording and iLQR tracks it.

## Arguments

| Parameters | Default | Purpose |
| --- | --- | --- |
| `--scene-config` / `-c` | Required | Scene list text file; one ID per line, processed in file order |
| `--dataset` | Required | `nuscenes` or `waymo` |
| `--max-steps` | `1000` | Maximum `step()` calls per scene in this script; the environment's own step limit still applies |
| `--warmup-step` | `None` | Number of initial environment steps controlled by ExpertILQRPolicy |
| `--gui` / `--no-gui` | Enabled | Inactive; this argument does not disable the web page, terminal UI, or video recording |
| `--gui-image-key` | `FRONT` | Inactive; this argument does not change the cameras displayed on the web page |

---

[Contents](../../DOCUMENTATION_EN.md) · [Previous: 1.3 Start the Environment Server](environment-server.md) · [Next: 2. Architecture](../guides/architecture.md)
