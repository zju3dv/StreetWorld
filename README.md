<p align="center">
  <img src="assets/streetworld-logo.svg" alt="StreetWorld logo" width="900">
</p>

# StreetWorld: A Comprehensive and Photorealistic Closed-Loop Autonomous Driving Benchmark

<p align="center">
  Lvchang Fu<sup>1</sup>, Hejiakang Cao<sup>1</sup>, Futang Zhu<sup>2</sup>,
  Yongchen Zai<sup>2</sup>, Zhen Yang<sup>2</sup>, Tian Xie<sup>1</sup>,
  Hujun Bao<sup>1</sup>, Xiaowei Zhou<sup>1</sup>, Sida Peng<sup>1</sup>
  <br>
  <sup>1</sup> Zhejiang University &nbsp; <sup>2</sup> BYD Company Limited
</p>

<p align="center">
  <a href="https://zju3dv.github.io/StreetWorld/"><img src="https://img.shields.io/badge/Project%20page-Website-blue?logo=googlechrome&logoColor=white" alt="Project page"></a>
  <a href="https://zju3dv.github.io/StreetWorld/demo.html"><img src="https://img.shields.io/badge/Demo-Video-red" alt="Demo video"></a>
  <a href="https://huggingface.co/datasets/lvchangfu/streetworld-benchmark"><img src="https://img.shields.io/badge/Hugging%20Face-Dataset-yellow?logo=huggingface" alt="Hugging Face"></a>
  <img src="https://img.shields.io/badge/arXiv-coming%20soon-grey?logo=arxiv" alt="arXiv">
  <a href="LICENSE.txt"><img src="https://img.shields.io/badge/License-Apache%202.0-green" alt="License: Apache 2.0"></a>
</p>

🚗 **What is StreetWorld?** StreetWorld is a high-fidelity, extensible closed-loop autonomous driving benchmark. It provides over 2,000 dynamic Gaussian splatting scene assets reconstructed from [nuScenes](https://www.nuscenes.org/) and [Waymo](https://waymo.com/open/), and integrates [NuRec](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles-NuRec) assets for closed-loop evaluation of AD policies. **Its highly extensible design gives the community the freedom to customize evaluation configurations and even integrate an unlimited number of scene assets.**

🎯 **Why is it important?** Open-loop trajectory metrics cannot measure how an AD policy's actions change subsequent observations or how errors accumulate over successive decisions. Closed-loop evaluation in synthetic environments also introduces a domain gap between simulation and real driving. AD policy evaluation therefore requires a **fully closed-loop**, **high-fidelity**, **large-scale**, and **physically correct** driving simulator.

🛠️ **How to use it?** StreetWorld follows Gym's environment design: AD policies interact through `reset()` and `step(action)` for training and evaluation. Users can also drive with keyboard controls in a browser. Rendering backends, observations, policies, and simulation objects have separate interfaces, so users can replace or extend them for new scenes, cameras, and AD policies.

[Documentation](documentation/DOCUMENTATION_EN.md) · [文档](documentation/DOCUMENTATION_ZH.md) · [Installation](documentation/en/getting-started/installation.md#section-1-1) · [Quick start](documentation/en/getting-started/web-controller.md#section-1-2)

## 🗓️ Release roadmap

- **[✓]** **[2026.10.31]** We have released StreetWorld simulator. More details are available on our [project page](https://zju3dv.github.io/StreetWorld/)
  - StreetWorld source code.
  - Updating and releasing the StreetWorld leaderboard on closed-loop nuScenes.
  - Release [nuScenes scene assets on Hugging Face](https://huggingface.co/datasets/lvchangfu/streetworld-benchmark)
- **[ ]** Release 2 Hz and 10 Hz evaluation results on Waymo
- **[ ]** Release Waymo scene assets
- **[ ]** Release StreetWorld paper paper

## 🗂️ Current assets

| Dataset | Scenes | Storage size | HD maps | Scene duration |
| --- | ---: | --- | --- | --- |
| [nuScenes](https://huggingface.co/datasets/lvchangfu/streetworld-benchmark) | 650 | 395 GiB | ✓ | 20 s |
| [Waymo] | TBD | TBD | ✓ | 20 s |
| [NuRec 25.07](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles-NuRec) | 923 | 1.51T | ✓ | 20 s |

## 🏆 StreetWorld leaderboard

Every E2E AD is evaluated on the 650 scenes in [`streetworld/examples/nuscene_list.txt`](streetworld/examples/nuscene_list.txt). Each scene has equal weight; NaN values count as 0 instead of being excluded. Rankings are ordered by RC.

### nuScenes · 2 Hz

| Rank | AD policy | NC ↑ (%) | DAC ↑ (%) | TTC ↑ (%) | COM ↑ (%) | RC ↑ (%) | RE ↑ (%) |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | [ST-P3](https://github.com/OpenDriveLab/ST-P3) | 52.00 | 95.05 | 46.93 | 95.75 | 59.83 | 16.98 |
| 2 | [OpenDriveVLA](https://github.com/DriveVLA/OpenDriveVLA) | 60.31 | 90.86 | 36.73 | 99.51 | 57.02 | 24.77 |
| 3 | [SparseDrive](https://github.com/swc-17/SparseDrive) | 50.46 | 95.08 | 40.01 | 97.49 | 55.86 | 17.46 |
| 4 | [DiffusionDrive](https://github.com/hustvl/DiffusionDrive) | 46.92 | 95.50 | 46.25 | 98.07 | 53.68 | 16.00 |
| 5 | [UniAD](https://github.com/OpenDriveLab/UniAD) | 60.31 | 91.19 | 36.78 | 99.17 | 53.50 | 37.50 |
| 6 | [MomAD](https://github.com/adept-thu/MomAD) | 54.77 | 92.09 | 37.98 | 96.18 | 52.09 | 19.20 |
| 7 | [Epona](https://github.com/Kevin-thu/Epona) | 73.54 | 81.04 | 34.55 | 92.47 | 51.55 | 23.75 |
| 8 | [AutoVLA](https://github.com/ucla-mobility/AutoVLA) | 51.08 | 91.12 | 45.16 | 95.38 | 51.39 | 12.69 |
| 9 | [VAD](https://github.com/hustvl/VAD) | 62.77 | 90.20 | 39.16 | 98.83 | 48.72 | 31.96 |
| 10 | [GenAD](https://github.com/wzzheng/GenAD) | 59.08 | 90.70 | 29.27 | 99.54 | 48.30 | 36.15 |
| 11 | [Latent TransFuser](https://github.com/autonomousvision/transfuser) | 50.00 | 87.45 | 38.72 | 99.42 | 38.08 | 17.89 |
| 12 | [OpenEMMA-Qwen2](https://github.com/taco-group/OpenEMMA) | 65.23 | 70.95 | 37.53 | 84.54 | 31.81 | 11.62 |

### nuScenes · 10 Hz

| Rank | AD policy | NC ↑ (%) | DAC ↑ (%) | TTC ↑ (%) | COM ↑ (%) | RC ↑ (%) | RE ↑ (%) |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | [ST-P3](https://github.com/OpenDriveLab/ST-P3) | 63.38 | 95.82 | 35.67 | 98.66 | 65.41 | 21.55 |
| 2 | [VAD](https://github.com/hustvl/VAD) | 56.15 | 93.54 | 32.15 | 100.00 | 58.48 | 40.51 |
| 3 | [UniAD](https://github.com/OpenDriveLab/UniAD) | 61.85 | 91.13 | 33.14 | 100.00 | 57.98 | 39.61 |
| 4 | [OpenDriveVLA](https://github.com/DriveVLA/OpenDriveVLA) | 56.92 | 91.76 | 31.56 | 100.00 | 55.16 | 36.82 |
| 5 | [AutoVLA](https://github.com/ucla-mobility/AutoVLA) | 53.54 | 94.48 | 37.44 | 96.77 | 50.61 | 17.45 |
| 6 | [DiffusionDrive](https://github.com/hustvl/DiffusionDrive) | 43.38 | 97.35 | 41.74 | 99.88 | 35.11 | 12.48 |

## 📄 License

StreetWorld code is released under the [Apache 2.0 License](LICENSE.txt).

## 🙏 Acknowledgments
The basis of our implementation builds on [MetaDrive](https://github.com/metadriverse/metadrive)'s simulation framework. Our nuScenes and Waymo assets are reconstructed by [Hierarchy UGP](https://github.com/LiAutoAD/HierarchyUGP).

We thank the creators of [nuScenes](https://www.nuscenes.org/) and the [Waymo Open Dataset](https://waymo.com/open/) for providing the driving recordings, annotations, and HD maps used to construct our scene assets. We thank NVIDIA for the [NuRec](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles-NuRec) reconstructed driving scenes and rendering service.

We also thank the authors of the AD policies for releasing their code and model weights. Their code allows us to integrate these AD policies into StreetWorld and compared under a common closed-loop evaluation protocol.

## 📚 Citation

```bibtex
@misc{streetworld,
  title  = {StreetWorld: A Comprehensive and Photorealistic Closed-Loop Autonomous Driving Benchmark},
  author = {Fu, Lvchang and Cao, Hejiakang and Zhu, Futang and
            Zai, Yongchen and Yang, Zhen and Xie, Tian and
            Bao, Hujun and Zhou, Xiaowei and Peng, Sida},
  year   = {2026}
}
```
