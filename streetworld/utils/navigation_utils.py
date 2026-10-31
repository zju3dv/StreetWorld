import numpy as np


def nearest_front_index(path, xy, heading_vec):
    rel = path - xy[None, :]
    dot = rel @ heading_vec
    mask = dot >= 0.0
    d2 = np.sum(rel[mask] ** 2, axis=1)
    if not np.any(mask):
        return int(path.shape[0])
    idx_in_mask = int(np.argmin(d2))
    return int(np.arange(len(path))[mask][idx_in_mask])


def project_to_polyline(position, points):
    """Return arc-length progress, segment index and distance to a polyline."""
    points = np.asarray(points, dtype=np.float64)
    position = np.asarray(position, dtype=np.float64)
    if points.ndim != 2 or points.shape[1] != 2 or len(points) < 2:
        raise ValueError("Trajectory must contain at least two XY points.")
    if position.shape != (2,) or not np.isfinite(position).all() or not np.isfinite(points).all():
        raise ValueError("Trajectory and position must contain finite XY coordinates.")

    segments = np.diff(points, axis=0)
    lengths = np.linalg.norm(segments, axis=1)
    fractions = np.zeros_like(lengths)
    moving = lengths > 0.0
    # A zero-length segment is a point with zero arc-length progress.
    fractions[moving] = np.clip(
        np.sum((position - points[:-1][moving]) * segments[moving], axis=1) / lengths[moving]**2,
        0.0, 1.0,
    )
    projections = points[:-1] + fractions[:, None] * segments
    distances = np.linalg.norm(projections - position, axis=1)
    index = int(np.argmin(distances))
    progress = lengths[:index].sum() + fractions[index] * lengths[index]
    return float(progress), index, float(distances[index])
