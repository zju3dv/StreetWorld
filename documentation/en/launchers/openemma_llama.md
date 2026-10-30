<a id="launcher-openemma_llama"></a>

# 7.18 OpenEMMA Llama

[简体中文](../../zh/launchers/openemma_llama.md)

[Contents](../../DOCUMENTATION_EN.md) · [Previous: 7.17 OpenEMMA LLaVA](openemma_llava.md) · [Next: Contents](../../DOCUMENTATION_EN.md)

<a id="launcher-openemma_llama-environment-and-resources"></a>

## Environment and resources

Install PyTorch, Transformers with MllamaForConditionalGeneration, Accelerate, and Pillow. The loader uses `bfloat16` and `device_map="sequential"` to place model layers in GPU order. For each visible GPU, `max_memory` is its current free memory minus `4 GiB`, reserving memory for vision inference and simulation on the same machine.

| Item | Value or path | Purpose |
| --- | --- | --- |
| Launcher implementation | policy_launcher/openemma/native_agent.py | Shared OpenEMMANativeAgent; subclasses select the backend |
| Backend implementation | policy_launcher/openemma/backbone.py | Model loading and generation |
| Default model name | meta-llama/Llama-3.2-11B-Vision-Instruct | Default model_id in code; not changed through the shared CLI |
| Dependency guide | [OpenEMMA requirements](https://github.com/taco-group/openemma/blob/8403ea636696c5c10e8fdeca566410de0a07e449/requirements.txt) | Backend dependency list |

Prepare a complete Llama 3.2 Vision model and obtain access to it. The loader uses AutoProcessor and MllamaForConditionalGeneration.from_pretrained with the model name in the table.

Implementation: [openemma/native_agent.py](../../../policy_launcher/openemma/native_agent.py).

<a id="launcher-openemma_llama-server-configuration"></a>

## Server configuration

Run this command in the simulation terminal, then select scenes:

```bash
python -m streetworld.examples.env_server \
  --host 127.0.0.1 --port 50052 --web-port 18080 \
  --ad-policy-config openemma
```

<a id="launcher-openemma_llama-launch-command"></a>

## Launch command

Open another terminal, activate the model environment, and run from the StreetWorld root:

```bash
python -m policy_launcher.launch \
  --model openemma_llama --host 127.0.0.1 --port 50052 \
  --device cuda --timeout 360 --max-steps 1000
```

<a id="launcher-openemma_llama-input-output-and-limits"></a>

## Inputs, outputs, and limitations

| Item | Requirements |
| --- | --- |
| Input | FRONT image, ego motion state, and navigation hints; buffers 10 frames with motion_dt=0.5 s; stationary segments use zero curvature. `predict_action()` returns `None` until 10 history frames are available; the default server uses ExpertILQRPolicy for warmup driving during this period |
| Output | Parses future speed/curvature and integrates at prediction_dt=0.5 s into a vehicle-coordinate (N, 2) trajectory. The prompt asks for 10 points; the parser requires at least 2 |
| Notes | Only the latest image is used; the prompt includes ten motion frames. --device is not passed to this backend, so the loader selects devices. The openemma preset uses warmup_step=10. Invalid replies are retried; if parsing fails (including fewer than two future points) and a previous trajectory exists, it is reused. |

---

[Contents](../../DOCUMENTATION_EN.md) · [Previous: 7.17 OpenEMMA LLaVA](openemma_llava.md) · [Next: Contents](../../DOCUMENTATION_EN.md)
