# Verification Checklist

Pass/fail checks exercised during bring-up of the assembled robot. Mark each item **PASS** or **FAIL**. Do not advance to the next group until the current group passes.

Recorded results from validation runs are in [field-test-log.md](field-test-log.md).

---

## 1. Manual teleop distance-accuracy test

**Setup:** Calibrated `TICKS_PER_REVOLUTION`, `WHEEL_RADIUS_M`, and `TRACK_WIDTH_M`
in firmware + `odom_calibration.yaml`. Bridge running. Tape a straight 2.0 m
line on the floor.

| Step | Action | Pass | Fail |
| --- | --- | --- | --- |
| 1.1 | Place robot at start mark; note `/odom` pose | - | - |
| 1.2 | Teleop straight ahead until bumper/mark at **2.0 m** tape end; stop | Robot stops on the mark within lateral tolerance | Drifts off the line badly or cannot reach the mark |
| 1.3 | Read `/odom` distance traveled: `hypot(Δx, Δy)` | Within **5%** of 2.0 m (1.90-2.10 m) | Error >5% → remeasure ticks/radius |
| 1.4 | Spin in place ~90° / 180° by teleop; compare yaw to floor marks | Yaw sign correct; magnitude matches | Wrong sign (swap encoder/motor polarity) or large scale error (track width) |

**Record:** commanded distance ___ m; odom distance ___ m; error ___ %.

---

## 2. `/map` visual smear check

**Setup:** Bridge + LiDAR + `robot_slam` running. RViz Fixed Frame = `map`.

| Step | Action | Pass | Fail |
| --- | --- | --- | --- |
| 2.1 | Teleop a slow loop around a room with clear walls | `/map` updates continuously | No `/map` or empty map |
| 2.2 | Inspect walls in RViz | Walls look **thin and straight** | Walls **smeared**, doubled, or curved |
| 2.3 | If smear: stop and debug odom first | After recalibration, walls sharpen | Tuning only SLAM params while odom is wrong |

**Remember:** smeared walls almost always mean **bad odometry calibration**, not a mysterious slam_toolbox bug (see [build-phases.md](build-phases.md) Phase 5).

Operating capture: `docs/images/features/feature-slam-map-rviz.jpg` · 3D view: `docs/images/features/feature-slam-map-3d.jpg`

---

## 3. Unattended multi-obstacle exploration

**Setup:** Full bringup (`full_system.launch.py`). Clear indoor space with obstacles. Target object present for later mission stages.

| Step | Action | Pass | Fail |
| --- | --- | --- | --- |
| 3.1 | Launch full stack; wait for topic gates | `/odom`, `/scan`, `/map` live | Stuck waiting on a topic |
| 3.2 | Frontier explorer sends Nav2 goals | Goals succeed or recover gracefully | Continuous abort / spin |
| 3.3 | Robot covers free space without collisions | Costmaps track obstacles | Repeated collisions |

---

## 4. Detector accuracy

**Setup:** Perception running with `target_object_n.pt` (or TensorRT `.engine` on Orin). Held-out images or live camera on known targets.

| Step | Action | Pass | Fail |
| --- | --- | --- | --- |
| 4.1 | Confidence ≥ 0.6 on target class | Precision ≥ 0.85 | Systematic false positives |
| 4.2 | Miss rate on visible targets acceptable | Recall ≥ 0.80 | Persistent misses |
| 4.3 | Inference rate capped | ~8 Hz without starving SLAM/Nav2 | GPU saturation / map freezes |

Capture: `docs/images/features/feature-gripper-top.jpg` (manipulator / chassis top-down)

---

## 5. Final map-with-marked-target

**Setup:** Mission node active; target in view after exploration.

| Step | Action | Pass | Fail |
| --- | --- | --- | --- |
| 5.1 | N consecutive detections fire mission | Robot stops; Nav2 cancelled | Continues driving |
| 5.2 | Annotated PNG written | File under `mission_outputs/` | No file / empty map |
| 5.3 | Mark aligns with target location in map | Visual consistency PASS | Mark far from true object |

Capture: `docs/images/features/feature-annotated-mission-map.jpg`
