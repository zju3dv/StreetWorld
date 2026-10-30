<a id="chapter-1"></a>

<a id="section-1-1"></a>

# 1.1 Installation

[简体中文](../../zh/getting-started/installation.md)

[Contents](../../DOCUMENTATION_EN.md) · [Previous: Contents](../../DOCUMENTATION_EN.md) · [Next: 1.2 Drive in the browser](web-controller.md)

## Requirements

Linux, Python 3.11, and CUDA 12.1 are recommended.

## Install

```bash
git clone --recursive https://github.com/Project-Street/StreetWorld.git
cd StreetWorld

conda create -n streetworld python=3.11 'pip>=25.1' -y
conda activate streetworld

python -m pip install --group build
python -m pip install torch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1 --index-url https://download.pytorch.org/whl/cu121
python -m pip install -e . --no-build-isolation
```

`pyproject.toml` installs `fast_gauss`, `st-renderer`, and `trajdata`, pinning them to the Git commits recorded by the StreetWorld submodules. Their local sources are in `submodules/fast-gauss-paral`, `submodules/st-renderer`, and `submodules/trajdata`, respectively.

After updating an existing checkout, synchronize its submodules and reinstall dependencies from the StreetWorld root:

```bash
git submodule update --init --recursive
python -m pip install -e . --no-build-isolation
```

<a id="download-scenes"></a>

## Download StreetWorld assets

Download the StreetWorld benchmark assets from [Hugging Face](https://huggingface.co/datasets/lvchangfu/streetworld-benchmark) and place them in `data/benchmark`. Run from the StreetWorld directory:

```bash
python -m pip install huggingface_hub
python - <<'PY'
from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="lvchangfu/streetworld-benchmark",
    repo_type="dataset",
    local_dir="data/benchmark",
)
PY
```

---

[Contents](../../DOCUMENTATION_EN.md) · [Previous: Contents](../../DOCUMENTATION_EN.md) · [Next: 1.2 Drive in the browser](web-controller.md)
