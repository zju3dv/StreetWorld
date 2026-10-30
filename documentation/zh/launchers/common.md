<a id="chapter-7"></a>

# 7.1 统一启动流程

[English](../../en/launchers/common.md)

[总目录](../../DOCUMENTATION_ZH.md) · [上一页：6.4 BaseRunnable](../reference/base-runnable.md) · [下一页：7.2 UniAD](uniad.md)

本页目录

- [Latent TransFuser 控制量服务端](#latent-control-server)
- [Alpamayo 的 NuRec 轨迹服务端](#alpamayo-trajectory-server)

[policy_launcher.launch](../../../policy_launcher/launch.py) 先加载模型的 NativeAgent，再通过 GrpcClientEnv 连接服务端。客户端循环调用 reset、解包观测、predict_action 和 step，运行服务端的场景队列。模型加载失败时还未连接 gRPC，也未重置场景。

在一个终端使用[仿真环境](../getting-started/installation.md#section-1-1)运行服务端，另一个终端使用对应模型环境运行 Launcher。两个终端都从 StreetWorld 根目录执行命令。模型环境需要 Python 3.10 或更高版本；Alpamayo 需要 3.12。客户端公共依赖包括 NumPy、Gymnasium、grpcio、Protobuf、SciPy 和 Pillow，模型依赖另行安装。

在模型环境中安装公共依赖：

```bash
python -m pip install numpy gymnasium grpcio protobuf scipy pillow
```

统一命令行通过 --model 选择模型，不提供 --checkpoint、--config 或 --model-root。文件路径在对应 NativeAgent 的构造配置中修改。

```bash
python -m policy_launcher.launch --help
python -m policy_launcher.launch \
  --model vad --host 127.0.0.1 --port 50052 \
  --device cuda --timeout 360 --max-steps 1000
```

| 参数 | 默认值 | 用途与实际行为 |
| --- | --- | --- |
| --model | 必填 | [模型列表](../../DOCUMENTATION_ZH.md#chapter-7)中的 17 个入口之一 |
| --host | 127.0.0.1 | StreetWorld gRPC 服务主机 |
| --port | 50052 | StreetWorld gRPC 端口 |
| --device | cuda | 传给多数模型的构造函数；OpenEMMA 四个入口没有接收该参数 |
| --timeout | 360 s | step RPC 超时；reset 使用两倍，即默认 720 s |
| --max-steps | 1000 | 单场景客户端循环上限；环境可能更早终止 |
| --scene-name | None | 传入后在第一个场景结束时退出，不按名称筛选场景；场景由服务端 scene_ids 选择 |

`--model` 选择客户端加载的模型。服务端通过 `--ad-policy-config` 选择对应的模型配置。

| Launcher | 服务端配置 | 动作与时间 |
| --- | --- | --- |
| uniad、vad、genad、momad、stp3、opendrivevla、diffusiondrive、sparsedrive | default | 轨迹；默认 trajectory_dt/control_dt/决策周期均为 0.5 s |
| autovla | autovla | 轨迹 0.5 s；专家预热 4 步 |
| epona | epona | 轨迹 0.1 s，控制与决策 0.5 s；专家预热 10 步 |
| openemma_* | openemma | 轨迹 0.5 s；专家预热 10 步 |
| latent_transfuser | `latent_transfuser` | `[steering, throttle_brake]`，即转向和油门/制动 |
| alpamayo1、alpamayo1.5 | `alpamayo`，选择 NuRec 场景 | 轨迹点间隔为 0.1 s |

unpack_ad_observation 读取 gaussian、states、navigation 和 surrounding，将微秒时间戳转为秒，补充 scene_token、cam_params、route_waypoints、target_waypoint 等字段。command 的约定是右转 0、左转 1、直行 2。各模型的 dataparser 随后处理图像、转换坐标，并将张量移到模型设备。

服务端默认同步运行，每次模型推理后推进一个环境步。开启 async_mode 时，模型推理期间仿真仍在推进，step 可能返回缓存结果，详见[同步与异步](../guides/architecture.md#section-2-6)。客户端达到 max_steps 后切换场景；如果环境还未返回终止，该场景不会计入 ScenarioEnv 的已完成指标。

<a id="latent-control-server"></a>

## Latent TransFuser 控制量服务端

在仿真环境中运行以下命令，然后按分类选择场景。服务端使用 `EnvInputPolicy` 接收模型输出的转向和油门/制动：

```bash
python -m streetworld.examples.env_server \
  --ad-policy-config latent_transfuser \
  --host 127.0.0.1 --port 50052 --web-port 18080
```

<a id="alpamayo-trajectory-server"></a>

## Alpamayo 的 NuRec 轨迹服务端

先启动 [NuRec 渲染服务](../guides/rendering-backends.md#nurec)，再在仿真环境中运行以下命令，选择 NuRec 场景。`alpamayo` 配置使用 iLQR 跟踪轨迹，轨迹点间隔和控制周期均为 `0.1 s`：

```bash
python -m streetworld.examples.env_server \
  --ad-policy-config alpamayo \
  --nurec-grpc-host 127.0.0.1 --nurec-grpc-port 8080 \
  --host 127.0.0.1 --port 50052 --web-port 18080
```

---

[总目录](../../DOCUMENTATION_ZH.md) · [上一页：6.4 BaseRunnable](../reference/base-runnable.md) · [下一页：7.2 UniAD](uniad.md)
