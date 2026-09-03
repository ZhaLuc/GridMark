# Workflow: Detection and Mission

From camera frames to a marked map PNG.

## Pipeline

```mermaid
sequenceDiagram
  participant Cam as usb_cam
  participant YOLO as yolo_detector_node
  participant Mission as mission_node
  participant Nav as Nav2
  participant Bridge as serial_bridge

  Cam->>YOLO: /image_raw
  YOLO->>Mission: /detections
  Mission->>Mission: N consecutive hits
  Mission->>Bridge: Twist zero
  Mission->>Nav: CancelGoal
  Mission->>Mission: save PNG
```

## Operator checklist

1. Engine loaded; `ros2 topic echo /detections` shows the target class string. 
2. `mission_node.target_class` matches that string. 
3. Camera TF and intrinsics set. 
4. Place target in mapped space; allow approach. 
5. Confirm logs: consecutive hits → confirmed pose → PNG path under `mission_outputs/`. 
6. Visually check red dot vs real object location.

## Related

- [robot_mission](../packages/robot_mission.md) 
- [robot_perception](../packages/robot_perception.md) 
- [Verification §4-5](../verification-checklist.md) 
