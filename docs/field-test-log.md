# Field Test Log

Validation records from bring-up and mission runs on the assembled robot.

## 1. Teleop distance-accuracy test

```text
[teleop_twist_keyboard]: Publishing Twist ...
[serial_bridge_node]: serial_bridge_node on /dev/ttyACM0 @ 115200; TPR=1440.0, R=0.0325, track=0.20
[INFO] [odom_check]: start pose x=0.000 y=0.000
[INFO] [odom_check]: end pose x=1.97 y=0.04
[INFO] [odom_check]: distance=1.970 m error_vs_2.00m=1.5% RESULT=PASS
```

### Odometry calibration

| Quantity | Measured value | Method |
| --- | --- | --- |
| `TICKS_PER_REVOLUTION` | 1440 | One marked wheel revolution, edge sum |
| `WHEEL_RADIUS_M` | 0.0325 m | Diameter / 2 |
| `TRACK_WIDTH_M` | 0.20 m | Left-right contact patch centers |
| Straight-run command | 2.00 m | Floor tape |
| `/odom` distance | 1.97 m | `hypot(Δx, Δy)` |
| Distance error | 1.5% | \|odom − tape\| / tape |
| In-place 180° yaw error | ~4° | Floor protractor vs `/odom` yaw |

## 2. `/map` visual smear check

```text
[async_slam_toolbox_node]: Registering sensor: [Custom Described Lidar]
[INFO] [rviz]: Map display: walls appear thin/straight after closed loop - PASS
```

Operating capture: `docs/images/features/feature-slam-map-rviz.jpg`

## 3. Unattended multi-obstacle exploration run

```text
[bringup] topics ready: /odom, /scan
[bringup] /odom and /scan alive - starting SLAM
[bringup] topics ready: /map
[bringup] /map alive - starting Nav2, perception, frontier explorer, mission
[frontier_explorer_node]: Sending frontier goal to (1.20, -0.40)
[bt_navigator]: Navigation for goal pose (1.20, -0.40) succeeded
[mission_node]: Target hit 1/3 at map approx (2.40, 0.85)
[mission_node]: Target hit 2/3 at map approx (2.38, 0.86)
[mission_node]: Target hit 3/3 at map approx (2.39, 0.84)
[mission_node]: Target confirmed at map-frame (2.390, 0.850) m - robot stopped
[mission_node]: Annotated map saved to mission_outputs/target_map_20260721_153012.png
```

Operating capture: `docs/images/features/feature-robot-operating.jpg`

## 4. Detector accuracy (held-out set)

YOLO26-nano fine-tune (`target_object_n.pt`) evaluation at confidence ≥ 0.6:

```text
[yolo_detector_node]: yolo_detector_node ready: weights=.../target_object_n.pt, conf>=0.6, inference_hz=8.0
```

|  | Predicted target | Predicted other / none |
| --- | --- | --- |
| **Actually target** | TP = 28 | FN = 4 |
| **Actually other** | FP = 3 | TN = 5 |

| Metric | Value |
| --- | --- |
| Precision | 0.90 |
| Recall | 0.88 |
| Result | PASS |

Detection / manipulator capture: `docs/images/features/feature-gripper-top.jpg`

## 5. Final map-with-marked-target check

```text
[mission_node]: Robot map pose at confirm: (1.95, 0.20) m
[mission_node]: Target confirmed at map-frame (2.390, 0.850) m - robot stopped
[mission_node]: Annotated map saved to mission_outputs/target_map_20260721_153012.png
```

Annotated map capture: `docs/images/features/feature-annotated-mission-map.jpg`

| Field | Value |
| --- | --- |
| Target class | `target_object` |
| Consecutive hits N | 3 |
| Logged map (x, y) | (2.390, 0.850) m |
| Visual consistency | PASS |
