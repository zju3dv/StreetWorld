# 5.2 Manager

[简体中文](../../zh/reference/manager.md)

[Contents](../../DOCUMENTATION_EN.md) · [Previous: 5.1 Environment](environment.md) · [Next: 5.3 Observation](observation.md)

See [configuration and example conventions](environment.md#reference-conventions).

On this page

- [5.2.1 BaseManager](#api-4-1)
- [5.2.2 ScenarioDataManager](#api-4-2)
- [5.2.3 AgentManager](#api-4-3)

<a id="api-4-1"></a>

## 5.2.1 BaseManager

### Purpose and construction

BaseManager is the base class for Managers and provides object registration, creation, and destruction. A Manager may create one or more physical objects during a scene and must release them together when scenes change. Subclasses can use these methods to implement their own scene or Agent management logic.

It uses [Randomizable](randomizable.md#api-9-3), stores objects by ID in `spawned_objects`, and calls their `destroy()` during cleanup. Environment calls each concrete Manager's `reset()`, `step()`, and `update_state()` directly; it does not automatically run every before/after hook.

Source: [streetworld/manager/base_manager.py](../../../streetworld/manager/base_manager.py).

### Configuration

Pass object constructor arguments through _spawn_object kwargs. BaseManager has no Config argument; subclasses store their own configuration.

### API

| Category and signature | Parameters | Returns | Behavior and conditions | Exceptions and implementation status |
| --- | --- | --- | --- | --- |
| Constructor<br>`__init__(self)` | — | None | Creates random state and an empty spawned_objects registry. | — |
| Instance method<br>`before_step(self, *args, **kwargs) -> dict` | `*args`: positional arguments; `**kwargs`: keyword arguments | dict | Pre-step hook; the base implementation returns an empty dictionary. | — |
| Instance method<br>`step(self, *args, **kwargs)` | `*args`: positional arguments; `**kwargs`: keyword arguments | None | Advancement hook; the base implementation does nothing. | — |
| Instance method<br>`after_step(self, *args, **kwargs) -> dict` | `*args`: positional arguments; `**kwargs`: keyword arguments | dict | Post-step hook; the base implementation returns an empty dictionary. | — |
| Instance method<br>`before_reset(self)` | — | None | Destroys all objects created by this Manager. | — |
| Instance method<br>`reset(self)` | — | None | Scene-reset hook; the base implementation does nothing. | — |
| Instance method<br>`after_reset(self)` | — | None | Post-reset hook; the base implementation does nothing. | — |
| Instance method<br>`destroy(self)` | — | None | Clears the random generator and all managed objects. | — |
| Instance method<br>`clear_object(self, object_id)` | `object_id`: object ID | The destroyed Object instance | Removes the object from spawned_objects and calls destroy. | Unknown IDs raise KeyError. |
| Instance method<br>`clear_all_objects(self)` | — | None | Destroys all entries and clears spawned_objects. | — |
| Instance method<br>`get_metadata(self)` | — | dict | Reads metadata before the first step; the base implementation returns an empty dictionary. | The checked episode_step property is not defined in BaseManager, so direct calls raise AttributeError. |
| Protected method<br>`_spawn_object(self, object_class, **kwargs)` | `object_class`: Object class to construct; `**kwargs`: keyword arguments | Object instance | Constructs object_class with kwargs and stores it under object.id. | Constructor errors propagate. Duplicate IDs overwrite registry entries without a check. |

### Example

```python
from streetworld.manager.base_manager import BaseManager

class ObjectManager(BaseManager):
    def create(self, object_class, **kwargs):
        return self._spawn_object(object_class, **kwargs)

manager = ObjectManager()
manager.seed(7)
print(manager.spawned_objects)
manager.destroy()
```

<a id="api-4-2"></a>

## 5.2.2 ScenarioDataManager

### Purpose and construction

ScenarioDataManager prepares recorded scenes for simulation. It resamples ego and participant trajectories onto the physics timeline so initialization, replay, and physics use consistent timestamps despite different recording intervals.

BaseEnv constructs it with configuration and metadata/model loading callbacks. `reset()` selects a scene, loads data and rendering models, prepares object initial states and camera parameters, and adjusts the ego origin and camera extrinsics for Controller height.

Source: [streetworld/manager/scenario_data_manager.py](../../../streetworld/manager/scenario_data_manager.py).

### Configuration

| Field | Type and unit | Default | Purpose and conditions |
| --- | --- | --- | --- |
| `scene_ids` | list[str] | Required | Available scene IDs; scene count is the list length and cannot be replaced by num_scenarios |
| `start_scenario_index` | int | `0` | Initial index for sequential sampling; the evaluation queue still begins at 0 |
| `random_scenario` | bool | `True` | Random selection outside evaluation when no scene_id is given; False cycles sequentially |
| `physics_world_step_size` | Number, µs | 20_000 (environment default) | Interval for alignment and interpolation of recorded tracks |
| `ego_z_height` | float, m | `0.0` | Height of the recorded ego origin; corrected by half the Controller height minus this value |
| `actor_config.controller` | Object class | DefaultVehicle (environment default) | Determines ego height and object type; supplied by complete environment configuration |
| `actor_config.controller_config.size` | Three-element sequence or None, meters | `None` | Uses the third element as ego height when supplied, otherwise the class DEFAULT_HEIGHT |

### API

| Category and signature | Parameters | Returns | Behavior and conditions | Exceptions and implementation status |
| --- | --- | --- | --- | --- |
| Constructor<br>`__init__(self, config, meta_loader, model_loader)` | `config`: component configuration dictionary; `meta_loader`: SimulatorInterface.load_metadata callback; `model_loader`: SimulatorInterface.load_model callback | None | Stores configuration/loaders and initializes the scene list and index. | Non-list scene_ids raises TypeError; an empty list cannot select a scene later. |
| Instance method<br>`eval(self, order=True, repeat_per_scene=1)` | `order`: ordering flag; `repeat_per_scene`: number of passes through the scene list | None | Rebuilds the index queue and enters evaluation mode. | order=False changes random_scenario without shuffling. repeat=2 repeats the whole list as A,B,A,B. |
| Instance method<br>`reset(self, scene_id=None)` | `scene_id`: ID in scene_ids, selected by Manager when None | VectorMap or None | Selects a scene, copies active configuration, loads/reformats metadata, prepares plane data, and calls model_loader. | The evaluation queue takes precedence over scene_id and raises LookupError when exhausted. Outside evaluation, an unknown ID raises ValueError. |
| Instance method<br>`get_current_scenario_data(self)` | — | dict | Returns current_metadata for ground, Agent, and camera creation. | Available after the first reset; returns the original object. |
| Instance method<br>`sort_scenarios(self)` | — | None, incomplete implementation | Curriculum difficulty sorting interface. | Incomplete: references uninitialized engine/summary_lookup and undefined scenario/SD. |
| Instance method<br>`destroy(self)` | — | None | Performs base object cleanup, then clears scene cache fields. | summary_lookup/mapping are not initialized by construction; calling this raises AttributeError. |
| Property getter<br>`current_scenario_difficulty(self)` | — | Number | Returns 0 when no difficulty table exists. | With a difficulty table, still depends on legacy summary_lookup/engine fields; sorting is not connected. |

The following metadata is available after loading.

| Field | Format and purpose |
| --- | --- |
| timestamp_range | Start/end microsecond timestamps aligned to ego recordings |
| scene_id | Current scene ID |
| camera_params | Camera K, H, W, ego2camera, and optional extra |
| ego_poses | Recorded ego poses after height correction |
| participants | Original participant poses, size, and type |
| init_state | Keyed by Agent name; contains spawn_position, spawn_yaw, spawn_velocity, spawn_angular_velocity, destination, and destination_yaw |
| agent_state | Keyed by Agent name and timestamp; each frame contains transform, position, velocity, angular_velocity, heading_theta, valid, and vehicle_class |
| ground_plane | Plane normal/constant; Environment uses mesh terrain when available |
| scene_mesh_path, scene_mesh_transform | Optional ground mesh path and coordinate transform |

Manager generates sample timestamps excluding the end time. An object with fewer than two recorded samples gets no trajectory. Ego recordings determine the scene time range.

### Example

```python
# The environment is already reset and manages this Manager's loading sequence.
manager = env.data_manager
metadata = manager.get_current_scenario_data()
print(metadata["timestamp_range"])
print(metadata["init_state"]["actor"])
print(metadata["agent_state"]["actor"].keys())
```

<a id="api-4-3"></a>

## 5.2.3 AgentManager

### Purpose and construction

AgentManager manages one simulated object: it creates the physical object, adds it to the physics world at its scheduled time, calls its Policy to update motion, and evaluates termination conditions such as collisions, leaving the road, and destination arrival. The ego vehicle and each surrounding participant have separate AgentManagers. Environment calls these Managers at each physics step so that their objects share one simulation timeline.

BaseEnv creates AgentManagers from ego/participant settings. `reset()` creates the Controller and passes scene data to Observer and Policy. The ego Manager persists across scenes; participant Managers are recreated. Observer and Policy are created only on the first reset, so later class-setting changes do not recreate them.

The Manager's `state` comes from this object's pose sequence in the dataset. ScenarioDataManager interpolates poses at physics-step intervals and derives position, velocity, heading, and other state fields for each sample. `state[timestamp]` is the object's state at that time. The key `timestamp` is in microseconds and shares the timeline used by StepCounter's current simulation time.

Source: [streetworld/manager/agent_manager.py](../../../streetworld/manager/agent_manager.py).

### Configuration

The config constructor argument takes actor_config or participant_config contents. The table uses complete environment paths for editing these settings.

| Field | Type and unit | Default | Purpose and conditions |
| --- | --- | --- | --- |
| `actor_config.check_crash` | bool | `True` | Checks collisions for nonstatic vehicles in ALIVE state |
| `actor_config.max_step` | int or None, environment steps | `10_000` | This Agent's step limit, distinct from top-level max_step |
| `actor_config.observer` | Observation class | `AssemblyObservation` | Created on the first reset |
| `actor_config.observer_config` | dict | `gaussian/navigation/states/surrounding` | Passed to Observer; fields are described under each Observation |
| `actor_config.policy` | Policy class | `EnvInputPolicy` | Created on first reset; output goes to Controller.move |
| `actor_config.policy_config` | dict | See each Policy | Passed to Policy; also supplies Manager.out_of_road_threshold |
| `actor_config.controller` | Object class | `DefaultVehicle` | Creates a Controller of this class on every reset |
| `actor_config.controller_config` | dict | See [BaseVehicle](object.md#api-7-2) | Physics and spawn settings |
| `actor_config.warmup_step` | int or None, environment steps | `None` | When not None, creates ExpertILQRPolicy and uses it while eposide_step is below this value |
| `actor_config.policy_config.out_of_road_threshold` | float, m | `5.0` | Off-road threshold: with a map, no lane within this radius means off-road; without a map, a minimum horizontal distance to dataset trajectory samples at or above this value means off-road |
| `participant_config.check_crash` | bool | `True` | Collision checking for surrounding vehicles |
| `participant_config.max_step` | int or None, environment steps | `10_000` | Surrounding Agent step limit |
| `participant_config.observer` | Observation class | `DefaultObservation` | Surrounding vehicles do not collect observations by default |
| `participant_config.observer_config` | dict | `{}` | Passed to the participant Observer |
| `participant_config.policy` | Policy class | `ReplayPolicy` | Reads dataset states at the current simulation time and directly sets participant pose, linear velocity, and angular velocity |
| `participant_config.policy_config` | dict | Same discrete-action fields as ego | ReplayPolicy does not read discrete-action fields |
| `participant_config.policy_config.discrete_action` | bool | `False` | EnvInputPolicy input mode; default ReplayPolicy does not read it |
| `participant_config.policy_config.discrete_steering_dim` | int | `5` | EnvInputPolicy steering levels; default ReplayPolicy does not read it |
| `participant_config.policy_config.discrete_throttle_dim` | int | `5` | EnvInputPolicy throttle/brake levels; default ReplayPolicy does not read it |
| `participant_config.policy_config.action_check` | bool | `False` | EnvInputPolicy input checking; default ReplayPolicy does not read it |
| `participant_config.controller` | Object class | Supplied from metadata type/dimensions | Vehicles use a Vehicle class; pedestrians/cyclists use their dedicated classes |
| `participant_config.controller_config` | dict | `size=None, enable_reverse=True, spawn_velocity=True, check_crash_world=False` | Scene dimensions override size. Environment assigns DummyObservation/ReplayPolicy to pedestrians and cyclists |

### API

| Category and signature | Parameters | Returns | Behavior and conditions | Exceptions and implementation status |
| --- | --- | --- | --- | --- |
| Constructor<br>`__init__(self, config, step_manager)` | `config`: component configuration dictionary; `step_manager`: StepCounter instance | None | Stores configuration and timing, initializing uncreated component references to None. | Requires max_step and check_crash; required component settings are read on first reset. |
| Instance method<br>`reset(self, config=None, **kwargs)` | `config`: optional updated settings; `kwargs`: runtime context including state, init_state, physics_world, render_fn, camera_params, collector, trajdata_map, and ground | None | Creates Controller, extracts the 2D positions whose state entries have valid=True, schedules the object to enter simulation at min(state), and initializes Policy and Observer. | kwargs must include scene state/init_state and component reset inputs. Policy selection after IDM route initialization failure is described under [IDMPolicy](policy.md#api-6-7). |
| Instance method<br>`step(self, action)` | `action`: external input in the current Policy's format | None | For nonstatic ALIVE Agents, calls active_policy to compute the action, then Controller.move. | — |
| Instance method<br>`initialize_state(self)` | — | None | For a NOT_SPAWN object, adds its physical body to the physics world and changes its state to ALIVE at the first key_step when simulation time is at or beyond spawn_timestamp. | — |
| Instance method<br>`update_state(self)` | — | None | Calls initialize_state, then evaluates collisions, step limits, leaving the road, and destination arrival for nonstatic ALIVE Agents in that order. When a termination condition is met, immediately destroys the physical object and sets the corresponding state. | — |
| Instance method<br>`set_state(self, new_state)` | `new_state`: AgentState value | None | Sets state externally; a NOT_SPAWN→ALIVE transition adds the body to the physics world, and the terminal states listed in this method destroy the physical object. | OUT_OF_STEP is absent from this method's cleanup list; normal advancement handles it in update_state. |
| Instance method<br>`observe(self)` | — | {'observation': observation_or_None} | Collects and caches Observer output when ALIVE; other states return the last cache. | — |
| Instance method<br>`get_base_state(self, transform=None)` | `transform`: 4×4 homogeneous `transform` | dict | Returns world pose/motion, dimensions, type, and map lane; static Agents have zero motion values. | Non-ALIVE Agents raise ValueError. Controller.transform overwrites the transform argument, so it cannot specify a sampling pose. |
| Instance method<br>`get_observation_spaces(self)` | — | Observer space declaration | Returns observer.observation_space directly. | Use after Observer creation and any required reset. |
| Instance method<br>`get_action_spaces(self)` | — | gym.Space | Returns active_policy.get_input_space. | During warmup, the expert Policy supplies the space. Trajectory Policies inherit a two-control input declaration. |
| Instance method<br>`get_state(self)` | — | dict, incomplete implementation | Agent state export is incomplete. | BaseManager has no get_state and _agent_object is undefined; calls raise AttributeError. |
| Instance method<br>`destroy(self)` | — | None | After initialization, clears objects and all three components; otherwise returns immediately. | — |
| Property getter<br>`active_policy(self)` | — | BasePolicy subclass instance | Returns the expert during warmup and the configured Policy afterward. | — |
| Property getter<br>`is_warmup_step(self)` | — | bool | True when an expert Policy exists and eposide_step < warmup_step. | — |

AgentState includes NOT_SPAWN, ALIVE, SUCCESS, OUT_OF_ROAD, OUT_OF_STEP, CRASH_VEHICLE, CRASH_HUMAN, CRASH_OBJECT, CRASH_WORLD, and IDLE. When conditions coincide, update_state's check order determines reason. At termination it destroys physical objects while retaining Manager state and the last observation for the environment response.

`spawn_timestamp` is the smallest timestamp in the supplied `state`, or `min(state)`. It schedules when the object enters the physics world. After `reset()` creates the object, its state is `NOT_SPAWN`. Once simulation time reaches that timestamp, `initialize_state()` calls `Controller.attachDyWld()` at the first environment-step boundary with `key_step=True` and changes the state to `ALIVE`. For example, if a participant's track starts two seconds after the scene begins, it enters the physics world when simulation reaches that time. The timestamp is the smallest key in `state`, without first filtering by `valid`.

`expert_trajectory` stores this object's 2D path from the dataset. The Manager traverses `state` in timestamp order, selects entries with `state[timestamp]["valid"] == True`, and retains their world-coordinate `position[:2]` values in meters. `valid` marks whether a state entry is usable; the current standard loading pipeline sets every state generated by `parse_object_state()` to `valid=True`. Here, “valid” specifically means that this Boolean field is True. The Manager uses these positions to measure deviation from the path when no map is available and to calculate path length after IDM initialization failure.

`is_static` is determined from the mean magnitude of the velocity vectors across all state samples. A mean speed below `0.01 m/s` marks the object as static. Static objects still enter the physics world according to `spawn_timestamp`, but the Manager does not call their Policy to update actions or evaluate collision termination, step limits, leaving the road, or destination arrival for them.

The off-road check determines whether an object has moved too far from map lanes or its dataset path and should stop running. `update_state()` performs this check only for nonstatic objects in `ALIVE` state on a `key_step`. The threshold comes from `policy_config.out_of_road_threshold` and defaults to `5.0 m`:

- With a `trajdata_map`, the Manager computes the center of the object's bottom face from its pose and height, then calls `get_lanes_within()` to find lanes within the threshold radius. This point is near the road surface, matching the height used by map lanes. An empty result marks the object as off-road.
- Without a map, the Manager computes the 2D Euclidean distance from the object's current world-coordinate `(x, y)` position to every sample in `expert_trajectory`. A minimum distance greater than or equal to the threshold marks the object as off-road. This calculation measures distance to discrete samples.

When either condition is met, the Manager destroys the object's physical instance and sets its state to `OUT_OF_ROAD`. For the ego vehicle, Environment ends the episode with `terminated=True` and `info["reason"]="out_of_road"`. For a surrounding participant, only that participant stops running.

`get_base_state()` performs a separate lane lookup to populate `current_lane` for observations and control Policies. It uses a fixed `2.25 m` matching radius and does not read NavigationObservation.current_lane_max_dist. The off-road check uses `out_of_road_threshold` as described above.

### Example

```python
# The environment is already reset; it advances the ego vehicle, so do not call manager.step separately.
manager = env.actor_manager
print(manager.state, manager.active_policy.name)
print(manager.get_base_state()["velocity"])
print(manager.is_warmup_step)
```

---

[Contents](../../DOCUMENTATION_EN.md) · [Previous: 5.1 Environment](environment.md) · [Next: 5.3 Observation](observation.md)
