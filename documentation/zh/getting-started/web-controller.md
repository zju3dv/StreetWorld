<a id="section-1-2"></a>

# 1.2 用浏览器驾驶

[English](../../en/getting-started/web-controller.md)

[总目录](../../DOCUMENTATION_ZH.md) · [上一页：1.1 安装](installation.md) · [下一页：1.3 启动 Environment Server](environment-server.md)

这个示例让你在浏览器中查看仿真场景，用 W/A/S/D 向车辆发送转向、加速和制动指令。初次使用 StreetWorld，可以先运行它，看一下相机画面，试一下车辆控制。

[env_easydrive_web_controller.py](../../../streetworld/examples/env_easydrive_web_controller.py) 会在本机启动仿真和网页。场景持续运行，浏览器中的按键输入用于控制车辆。

## 启动

完成[安装](installation.md#section-1-1)后，从 StreetWorld 根目录运行：

```bash
conda activate streetworld
python -m streetworld.examples.env_easydrive_web_controller
```

在终端先选择 nuScenes，再按道路区域、交通密度、时间、天气等分类选择场景条件。用上下方向键移动，按 Enter 选中或取消选中条目；每个分类至少选择一项，选好后移到 Continue，按 Enter 进入下一页。完成分类选择后，脚本开始运行筛选出的场景。

nuScenes 场景从 [1.1](installation.md#download-scenes) 下载到的 `data/benchmark/nuscenes` 加载，地图使用同目录的 `map_cache.npz`。

## 运行后

打开 `http://127.0.0.1:8080`。页面显示相机画面、时间（s）、速度（m/s）和角速度（rad/s），下方的 `STEER` 与 `THROTTLE / BRAKE` 控制条显示带正负号的百分比。点击浏览器窗口后使用以下按键：

| 按键 | 操作 |
| --- | --- |
| W | 踩油门，向前加速 |
| S | 向后驱动；前进时先减速，随后倒车 |
| A | 向左转向 |
| D | 向右转向 |

`throttle_brake` 控制量范围为 `[-1, 1]`，`1` 表示最大油门，`0` 表示不加油，负值用于向后驱动或制动。按住 W 发送 `1`（+100%），按住 S 发送 `-1`（-100%），松开后恢复为 `0`。

本示例默认允许倒车，S 会向后施加驱动力。将 `actor_config.controller_config.enable_reverse` 设为 `False` 后，S 改为制动。`steering` 是转向控制量，`1`、`-1`、`0` 分别表示最大左转、最大右转和方向回正；A 和 D 分别发送 `1` 和 `-1`。

脚本依次运行选中的场景，一个场景结束后自动切换到下一个。视频保存到 `videos/`。全部场景结束后，网页仍会保留，在终端按 `Ctrl-C` 退出。

## 参数

| 参数 | 默认值 | 用途 |
| --- | --- | --- |
| `--web-host`、`--web-port` | `127.0.0.1`、`8080` | 浏览器页面的监听地址 |
| `--video-output-dir` | `videos` | 视频保存目录 |

---

[总目录](../../DOCUMENTATION_ZH.md) · [上一页：1.1 安装](installation.md) · [下一页：1.3 启动 Environment Server](environment-server.md)
