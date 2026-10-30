<a id="chapter-1"></a>

<a id="section-1-1"></a>

# 1.1 安装

[English](../../en/getting-started/installation.md)

[总目录](../../DOCUMENTATION_ZH.md) · [上一页：总目录](../../DOCUMENTATION_ZH.md) · [下一页：1.2 用浏览器驾驶](web-controller.md)

## 环境要求

环境推荐使用 Linux、Python 3.11 和 CUDA 12.1。

## 安装

```bash
git clone --recursive https://github.com/Project-Street/StreetWorld.git
cd StreetWorld

conda create -n streetworld python=3.11 'pip>=25.1' -y
conda activate streetworld

python -m pip install --group build
python -m pip install torch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1 --index-url https://download.pytorch.org/whl/cu121
python -m pip install -e . --no-build-isolation
```

`fast_gauss`、`st-renderer` 和 `trajdata` 由 `pyproject.toml` 安装，并固定到与 StreetWorld 子模块一致的 Git 提交。三者的本地源码分别位于 `submodules/fast-gauss-paral`、`submodules/st-renderer` 和 `submodules/trajdata`。

已有工作副本更新代码后，在 StreetWorld 根目录同步子模块，再重新安装依赖：

```bash
git submodule update --init --recursive
python -m pip install -e . --no-build-isolation
```

<a id="download-scenes"></a>

## StreetWorld资产下载

请从 [Hugging Face](https://huggingface.co/datasets/lvchangfu/streetworld-benchmark) 下载 StreetWorld benchmark资产并放在`data/benchmark`中。在 StreetWorld 目录执行：

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

[总目录](../../DOCUMENTATION_ZH.md) · [上一页：总目录](../../DOCUMENTATION_ZH.md) · [下一页：1.2 用浏览器驾驶](web-controller.md)
