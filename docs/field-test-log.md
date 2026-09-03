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

