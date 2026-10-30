# TODO: how to lane shifting?
# TODO: how to use map?
# TODO: parameter space

import math
import numpy as np
import gymnasium as gym

from streetworld.policy.base_policy import BasePolicy
from streetworld.policy.idm_policy import IDMRouteInitializationError
from streetworld.type import MetaDriveType
from streetworld.utils.navigation_utils import nearest_front_index

class TrajectoryIDMPolicy(BasePolicy):
    ACC_FACTOR = 2.0
    DEACC_FACTOR = 3.0
    DELTA = 4.0
    MIN_LOOKAHEAD = 3.0
    LOOKAHEAD_TIME = 1.0

    def __init__(self, step_manager, config=None):
        super().__init__(step_manager, config)
        self.front_distance = float(self.config.get("front_distance", 1.5))
        self.react_time = float(self.config.get("react_time", 1.0))

        # Sample speeds (km/h)
        self.max_speed = float(gym.spaces.Box(low=np.array([25.0]), high=np.array([50.0]), dtype=np.float32).sample()[0])
        self.path = None
        self.cumlen = None
        self.curve_radius = None

    def reset(self, controller, seed, state, init_state, **kwargs):
        if controller.metadrive_type != MetaDriveType.VEHICLE:
            raise ValueError("IDMPolicy can only be used for vehicle agents.")
        super().reset(controller, seed, state, init_state, **kwargs)
        self.last_action = (0.0, 0.0)
        self.path, self.cumlen = self.__build_path_from_trajectory()
        self.curve_radius = self.__curve_radius(self.path)
        segments = np.diff(self.path.astype(np.float64), axis=0)
        lengths = np.linalg.norm(segments, axis=1)
        nonzero = lengths > 0.0
        self.segment_starts = self.path[:-1][nonzero].astype(np.float64)
        self.segment_vectors = segments[nonzero]
        self.segment_lengths = lengths[nonzero]
        self.segment_s = np.r_[0.0, np.cumsum(lengths)][:-1][nonzero]

    def act(self, observation, *args, **kwargs):
        if not self.step_manager.key_step:
            return self.last_action
        if observation is None or "surrounding" not in observation:
            raise KeyError("IDMPolicy requires observation['surrounding'].")
        surround = observation["surrounding"]
        pts = self.path
        v = self.controller.speed_km_h
        v_m_s = self.controller.speed

        # Ego pose and heading
        ego_xy = np.array([self.controller.position[0], self.controller.position[1]], dtype=np.float32)
        h = self.controller.heading
        heading_vec = np.array([float(h[0]), float(h[1])], dtype=np.float32)

        # Locate the vehicle on the path for longitudinal IDM control.
        rel_all = pts - ego_xy[None, :]
        if not np.any((rel_all @ heading_vec) >= 0.0):
            raise RuntimeError("IDMPolicy found no forward waypoint on the trajectory path.")
        front_idx = int(nearest_front_index(pts, ego_xy, heading_vec))
        v0 = self.__target_speed(front_idx)

        # Free road acceleration
        a_free = self.ACC_FACTOR * (1.0 - (v / max(v0, 1e-3)) ** self.DELTA)

        # Select the nearest object ahead within half the vehicle width of the path.
        ego_s, _, _ = self.__project_to_path(ego_xy)
        lead = None
        lead_distance = None
        lead_direction = None
        for obj in surround.values():
            obj_s, lateral, direction = self.__project_to_path(np.asarray(obj["position"], dtype=np.float64)[:2])
            longitudinal = obj_s - ego_s
            if longitudinal <= 0 or lateral >= self.controller.WIDTH * 0.5:
                continue
            if lead is None or longitudinal < lead_distance:
                lead = obj
                lead_distance = longitudinal
                lead_direction = direction

        a_int = 0.0
        if lead is not None:
            ego_len = self.controller.LENGTH
            obj_len = lead["size"][0]
            lead_type = lead["type"]
            s0 = self.front_distance if lead_type == MetaDriveType.VEHICLE else 2.0

            # Gap s computed from path arclen minus half lengths
            s = max(1e-3, lead_distance - 0.5 * ego_len - 0.5 * obj_len)

            # Tangential velocities (km/h)
            v_obj = np.asarray(lead["velocity"], dtype=np.float32)[:2]
            v_obj_t = np.dot(v_obj, lead_direction) * 3.6
            dv = max(0.0, v - v_obj_t)
            dv_m_s = dv / 3.6

            s_star = s0 + v_m_s * self.react_time + v_m_s * dv_m_s / (2.0 * math.sqrt(self.ACC_FACTOR * self.DEACC_FACTOR))
            a_int = self.ACC_FACTOR * (s_star / s) ** 2

        a_cmd = a_free - a_int
        if a_cmd >= 0.0:
            throttle_brake = a_cmd / self.__controller_max_acceleration()
        else:
            throttle_brake = a_cmd / self.__controller_max_deceleration()
        throttle_brake = float(np.clip(throttle_brake, -1.0, 1.0))

        steering = self.__steering(ego_xy, heading_vec, v_m_s)
        self.last_action = (steering, throttle_brake)
        return self.last_action

    def __project_to_path(self, position):
        """Return arc length, distance, and tangent at the closest point on the polyline."""
        relative = position - self.segment_starts
        fractions = np.clip(np.sum(relative * self.segment_vectors, axis=1) / self.segment_lengths ** 2, 0.0, 1.0)
        projected = self.segment_starts + fractions[:, None] * self.segment_vectors
        distances_squared = np.sum((position - projected) ** 2, axis=1)
        index = int(np.argmin(distances_squared))
        return (float(self.segment_s[index] + fractions[index] * self.segment_lengths[index]),
                float(np.sqrt(distances_squared[index])),
                self.segment_vectors[index] / self.segment_lengths[index])

    def __steering(self, ego_xy, heading_vec, speed):
        """Pure pursuit from the rear axle with lookahead measured in meters."""
        rear_xy = ego_xy - float(self.controller.REAR_WHEELBASE) * heading_vec
        rear_idx = nearest_front_index(self.path, rear_xy, heading_vec)
        lookahead = max(self.MIN_LOOKAHEAD, self.LOOKAHEAD_TIME * speed)
        target_s = min(float(self.cumlen[-1]), float(self.cumlen[rear_idx]) + lookahead)
        target = np.array([np.interp(target_s, self.cumlen, self.path[:, axis]) for axis in (0, 1)])
        to_target = target - rear_xy
        distance_squared = float(np.dot(to_target, to_target))
        if distance_squared <= 1e-6:
            return 0.0

        lateral = float(heading_vec[0] * to_target[1] - heading_vec[1] * to_target[0])
        wheelbase = float(self.controller.FRONT_WHEELBASE + self.controller.REAR_WHEELBASE)
        angle = math.atan2(2.0 * wheelbase * lateral, distance_squared)
        angle_limit = math.radians(float(self.controller.max_steering))
        return float(np.clip(angle / angle_limit, -1.0, 1.0))

    def __build_path_from_trajectory(self):
        points = []
        for ts in sorted(self.trajectory.keys()):
            frame = self.trajectory[ts]
            if not frame["valid"]:
                continue
            pos = frame["position"]
            points.append([float(pos[0]), float(pos[1])])
        path = np.asarray(points, dtype=np.float32)
        if len(path) < 3:
            raise IDMRouteInitializationError(f"IDMPolicy requires at least 3 valid trajectory points, got {len(path)}.")
        seg_len = np.linalg.norm(path[1:] - path[:-1], axis=1)
        if not np.any(seg_len > 1e-6):
            raise IDMRouteInitializationError("IDMPolicy got zero-length trajectory path.")
        cumlen = np.concatenate([[0.0], np.cumsum(seg_len)]).astype(np.float32)
        return path, cumlen

    def __target_speed(self, front_idx):
        radius = float(self.curve_radius[front_idx])
        curve_speed = math.sqrt(self.__controller_max_acceleration() * radius) * 3.6
        return float(min(self.max_speed, curve_speed))

    def __controller_max_acceleration(self):
        return 4.0 * float(self.controller.max_engine_force) / float(self.controller.MASS)

    def __controller_max_deceleration(self):
        return 4.0 * float(self.controller.max_brake_force) / (
            float(self.controller.MASS) * float(self.controller.TIRE_RADIUS)
        )

    @staticmethod
    def __curve_radius(path):
        radius = np.full(len(path), np.inf, dtype=np.float32)
        for i in range(1, len(path) - 1):
            a = float(np.linalg.norm(path[i] - path[i - 1]))
            b = float(np.linalg.norm(path[i + 1] - path[i]))
            c = float(np.linalg.norm(path[i + 1] - path[i - 1]))
            v1 = path[i] - path[i - 1]
            v2 = path[i + 1] - path[i]
            cross = float(v1[0] * v2[1] - v1[1] * v2[0])
            if abs(cross) > 1e-6:
                radius[i] = a * b * c / (2.0 * abs(cross))
        return radius
