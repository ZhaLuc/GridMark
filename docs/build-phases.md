# Build Phases (1-5)

Step-by-step bring-up for the GridMark. Complete each phase’s verification before moving on.

For architecture and package internals, see the [documentation index](README.md). Hardware detail lives under [hardware/](hardware/). Calibration values used on this chassis are recorded in [field-test-log.md](field-test-log.md) and `odom_calibration.yaml`.

---

## Phase 1 - Chassis + manual control

**Goal:** Power the drivetrain safely and command left/right PWM from the Arduino without ROS.

1. Assemble the 4WD chassis, mount both BTS7960 modules, and wire motors in parallel per side per [motor-driver-wiring.md](hardware/wiring/motor-driver-wiring.md).
2. Wire the 3S LiPo → fuse → switch → motor rails and compute buck per [power-wiring.md](hardware/wiring/power-wiring.md). Confirm buck output is **5.0 V** with a multimeter before connecting the Jetson.
3. Flash `robot_ws/src/robot_firmware/robot_firmware.ino` to the Mega 2560.
4. Power motors from the pack (switch on). Power the Mega via USB from a PC or the Jetson.
5. Open the serial monitor at **115200** baud. Send:
   ```text
   L80 R80
   ```
   then
   ```text
   L0 R0
   ```
   Wheels on both sides should spin the same forward direction at `L80 R80`. If a side runs backward, swap that side’s M+/M− (or fix parallel motor polarity).
6. Confirm the **500 ms** command timeout: stop sending commands; motors should coast/stop within about half a second.

**Pass criteria:** Both sides respond to signed PWM, stop on timeout, and no logic brown-outs when motors start under light load.

---

## Phase 2 - Wheel odometry + calibration

**Goal:** Trust encoder tick deltas enough to later integrate `/odom`.

1. Wire encoders to interrupt pins per [encoder-wiring.md](hardware/wiring/encoder-wiring.md) (left A/B → D2/D3, right A/B → D18/D19, 5 V/GND).
2. With firmware running, lift the robot so wheels can spin freely. Watch serial for lines:
   ```text
   ODOM <d_left> <d_right> <dt_ms>
   ```
3. **Measure `TICKS_PER_REVOLUTION`:** mark a wheel and the chassis; rotate exactly one revolution by hand; sum tick deltas (or note the change in cumulative counts if you temporarily print totals). Update the constant in `robot_firmware.ino` **and** `robot_bridge/config/odom_calibration.yaml` to the same value.
4. **Measure `WHEEL_RADIUS_M`:** measure wheel diameter with calipers/tape, divide by two, convert to meters.
5. **Measure `TRACK_WIDTH_M`:** distance between left and right wheel contact patches (center-to-center), in meters.
6. Optional sanity check: command equal PWM both sides on the ground for a short straight push; left and right tick deltas should stay close in magnitude. Large divergence means slip, bad wiring, or mismatched wheel radii.

**Pass criteria:** Stable `ODOM` lines at ~20 ms, measured geometry written into firmware + YAML, forward motion produces same-sign ticks on both sides.

---

## Phase 3 - ROS 2 + Arduino bridge bring-up

**Goal:** Close the loop Jetson ↔ Mega with `/cmd_vel` and `/odom`.

1. On the Jetson (JetPack 6.x / Ubuntu 22.04, ROS 2 Jazzy), build the workspace and source it:
   ```bash
   cd robot_ws
   colcon build --packages-select robot_bridge
   source install/setup.bash
   ```
2. Identify the Mega serial device (`/dev/ttyACM0` or similar); set `serial_port` in `odom_calibration.yaml` if needed. Add your user to the `dialout` group if permission denied.
3. Launch the bridge:
   ```bash
   ros2 launch robot_bridge bridge.launch.py
   ```
4. In another terminal, echo odometry:
   ```bash
   ros2 topic echo /odom
   ```
5. Publish a gentle twist (or use `teleop_twist_keyboard`):
   ```bash
   ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.1}, angular: {z: 0.0}}" -r 10
   ```
6. In RViz (or `tf2_echo`), confirm `odom` → `base_link` updates when the robot moves and stops updating when `/cmd_vel` is zero and wheels are still.

**Pass criteria:** `/cmd_vel` moves the robot; `/odom` pose integrates; TF `odom` → `base_link` is present; killing the bridge (or unplugging USB) results in motors stopping via the firmware timeout.

---

## Phase 4 - LiDAR integration

**Goal:** Publish a clean `/scan` in the correct frame.

1. Mount the RPLIDAR A2 and connect it through the **powered USB hub** per [lidar-and-camera-wiring.md](hardware/wiring/lidar-and-camera-wiring.md) - not a bare Jetson root port.
2. Install/launch `rplidar_ros` so it publishes `sensor_msgs/LaserScan` on `/scan` with `frame_id` = `lidar_link` (or remap/set accordingly).
3. Measure the real `base_link` → LiDAR offset; keep the doc example (`x=0.10`, `y=0.00`, `z=0.15`, yaw `0.0`) only until you measure. Those same numbers are the defaults in `robot_slam/launch/slam.launch.py`.
4. Launch the static TF (alone for now, or via the SLAM launch in Phase 5):
   ```bash
   ros2 run tf2_ros static_transform_publisher --x 0.10 --y 0 --z 0.15 --yaw 0 --pitch 0 --roll 0 --frame-id base_link --child-frame-id lidar_link
   ```
5. In RViz, set Fixed Frame to `base_link` (or `odom` if the bridge is running) and display `/scan`. Rotate the robot in place by hand; the scan should rotate consistently with the chassis.

**Pass criteria:** Continuous `/scan`, no USB disconnect storms under spin-up, laser points sit where you expect relative to the robot model/TF.

---

## Phase 5 - SLAM bring-up and tuning

**Goal:** Build an occupancy map online with `slam_toolbox` and prove odometry is good enough for mapping.

1. Ensure Phases 3-4 are running: bridge (`/odom`, `odom`→`base_link`), LiDAR (`/scan`), and power stable.
2. Build and launch SLAM:
   ```bash
   cd robot_ws
   colcon build --packages-select robot_slam
   source install/setup.bash
   ros2 launch robot_slam slam.launch.py
   ```
   Override LiDAR TF after measuring, for example:
   ```bash
   ros2 launch robot_slam slam.launch.py lidar_x:=0.10 lidar_y:=0.0 lidar_z:=0.15
   ```
3. Open RViz: Fixed Frame = `map`. Add Map (`/map`), LaserScan (`/scan`), TF, and Odometry (`/odom`).
4. **Verification - manual teleop mapping loop:** drive a slow teleop loop around a room with clear walls (rectangle hallway or office perimeter). Confirm the `/map` walls appear **thin and straight, not smeared**.

   - Thin, sharp walls that close on themselves after a loop → odometry + SLAM are in a healthy range; proceed to fine-tune `slam_toolbox` params if needed.
   - **Smeared, doubled, or curved walls** almost always trace back to **bad odometry calibration** (wrong ticks/rev, wheel radius, track width, or left/right polarity) - **not** a mysterious SLAM bug. Return to Phase 2, remeasure, keep firmware and `odom_calibration.yaml` in lockstep, then remapping with a fresh map.
5. Light SLAM tuning only after odom is trustworthy: adjust `minimum_travel_distance` / `minimum_travel_heading`, match response thresholds, or `max_laser_range` if your mounting clips range. Prefer fixing encoder geometry over cranking scan-match penalties to hide systematic drift.
6. When satisfied, save the map / pose-graph using slam_toolbox’s map saver tooling for later Nav2 work.

**Pass criteria:** `map` → `odom` → `base_link` → `lidar_link` TF tree complete; `/map` updates while teleoping; walls look thin and straight on a closed manual loop.

---

## Suggested order of terminals (Phase 5)

1. `ros2 launch robot_bridge bridge.launch.py`
2. RPLIDAR driver launch (package-specific)
3. `ros2 launch robot_slam slam.launch.py`
4. Teleop + RViz

If anything fails, work bottom-up: power → PWM → `ODOM` serial → `/odom` TF → `/scan` → `/map`.
