# Package: robot_firmware

## Purpose

Low-level real-time control on the **Arduino Mega 2560**: accept side PWM commands over USB serial, drive two BTS7960 modules, decode quadrature encoders on interrupt pins, and stream tick deltas for Jetson-side odometry.

## Why a Mega (not Uno)

Six external interrupt-capable pins (2, 3, 18, 19, 20, 21) allow four encoder channels on CHANGE without sharing pin-change interrupts awkwardly. Pins 20/21 remain free (I2C).

## Location

`robot_ws/src/robot_firmware/robot_firmware.ino` - **not** built by `colcon`.

## Pin map

| Function | Pin |
| --- | --- |
| Left EN (R_EN+L_EN tied) | D22 |
| Left RPWM / LPWM | D5 / D6 |
| Right EN | D23 |
| Right RPWM / LPWM | D9 / D10 |
| Left encoder A/B | D2 / D3 |
| Right encoder A/B | D18 / D19 |

## Internal logic

### Quadrature decoding

On each CHANGE of A or B, read `(A<<1)|B`, index `QUAD_TRANSITIONS[(prev<<2)|curr]`, add −1/0/+1 to a `volatile long` tick count. This is full 2-bit state-machine decoding (direction-aware), not simple edge counting.

### Control loop (20 ms)

1. Poll serial for `L.. R..` lines. 
2. If command age ≥ 500 ms → stop motors. 
3. Snapshot ticks under `noInterrupts()`. 
4. Compute wheel ω, then `v` and `ω` (Phase 2 local kinematics). 
5. Print `ODOM dL dR dt_ms`.

### Motor mapping

| Command | Hardware |
| --- | --- |
| pwm > 0 | EN high, RPWM=pwm, LPWM=0 |
| pwm < 0 | EN high, LPWM=|pwm|, RPWM=0 |
| pwm = 0 | EN low, both PWM 0 |

## Inputs / outputs

| Input | Output |
| --- | --- |
| USB serial commands | Motor PWM / enables |
| Encoder A/B edges | `ODOM` lines @ 50 Hz |

## Assumptions

- Logic 5 V shared Mega↔encoders↔driver logic GND. 
- Motor power is **not** from Mega 5 V. 
- Geometry constants are measured on the robot.

## Edge cases

- Illegal Gray transitions → table returns 0 (missed noise). 
- Serial buffer overflow → line discarded. 
- Boot: `g_last_cmd_ms` initialized so timeout does not immediate-stop before first command grace.

## Extensibility

- Pins 20/21 free for I2C IMU later. 
- Could extend serial to print `v`/`ω`; currently kept off-wire to leave float math on Jetson.

## Related

- [Hardware motor wiring](../hardware/wiring/motor-driver-wiring.md) 
- [Encoder wiring](../hardware/wiring/encoder-wiring.md) 
- [robot_bridge](robot_bridge.md) 
