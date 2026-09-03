# robot_mission

Mission fusion: confirmed YOLO detections → map-frame target estimate → stop robot,
cancel Nav2, save annotated `/map` PNG.

## Run

```bash
ros2 launch robot_mission mission.launch.py
```

Default localization of the target uses the **no-depth** bearing + ground-plane /
`assumed_range_m` projection described in the project spec. Enable an optional
RealSense depth path with `use_depth:=true` (and a depth topic).

Camera intrinsics (`fx`, `fy`, `cx`, `cy`) default to the calibrated 640×480
webcam values used on this chassis. Re-calibrate if you swap cameras before
trusting meter-level accuracy.
