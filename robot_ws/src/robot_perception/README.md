# robot_perception

USB camera (`usb_cam` → `/image_raw`) and Ultralytics YOLO26 detector (`/detections`).

## Run

```bash
ros2 launch robot_perception perception.launch.py
```

Default weights: `models/target_object_n.pt` (fine-tuned YOLO26-nano). ONNX export `target_object_n.onnx` is included for TensorRT conversion on the Orin Nano Super.

```bash
ros2 launch robot_perception perception.launch.py weights_path:=/absolute/path/to/target_object_n.engine
```
