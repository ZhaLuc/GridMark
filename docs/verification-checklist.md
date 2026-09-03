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

