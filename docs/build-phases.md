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
