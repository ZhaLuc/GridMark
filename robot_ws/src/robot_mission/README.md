# robot_mission

Mission fusion: confirmed YOLO detections → map-frame target estimate → stop robot,
cancel Nav2, save annotated `/map` PNG.

## Run

```bash
ros2 launch robot_mission mission.launch.py
