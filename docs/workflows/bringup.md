# Workflow: Bringup

End-to-end cold start from powered hardware to a healthy ROS graph.

## Preconditions

- [ ] Firmware flashed; motors respond to serial `L80 R80` 
- [ ] Bridge YAML serial port correct; user in `dialout` 
- [ ] Powered USB hub for LiDAR + camera 
- [ ] Workspace built and sourced 
- [ ] YOLO `.engine` present if you need mission (optional for mapping-only)

## Steps

1. Power LiPo (switch on); confirm Jetson 5 V from buck. 
2. Connect Mega USB to Jetson; hub to Jetson; LiDAR + cam on hub. 
3. Run:

```bash
ros2 launch robot_bringup full_system.launch.py
```

4. Watch for:

```text
[bringup] topics ready: /odom, /scan
[bringup] /odom and /scan alive - starting SLAM
[bringup] topics ready: /map
[bringup] /map alive - starting Nav2...
```

5. Verify:

```bash
ros2 topic hz /scan
ros2 topic echo /odom --once
ros2 run tf2_ros tf2_echo map base_link
```

## Failure branches

| Stuck at | Check |
| --- | --- |
| Waiting `/odom` | Bridge, serial device, firmware ODOM lines |
| Waiting `/scan` | `lidar_port`, hub power, `rplidar_node` name |
| Waiting `/map` | SLAM TF, scan frame_id, slam lifecycle |

## Related

- [Architecture startup](../architecture.md) 
- [Troubleshooting](../troubleshooting.md) 
