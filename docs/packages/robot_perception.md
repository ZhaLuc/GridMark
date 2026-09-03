# Package: robot_perception

## Purpose

Capture RGB frames from a USB webcam and run **Ultralytics YOLO26** inference on a **TensorRT** `.engine`, publishing `vision_msgs/Detection2DArray` on `/detections` at a capped rate so SLAM/Nav2 retain GPU/CPU budget on the Orin Nano.

## Location

`robot_ws/src/robot_perception/`

| Artifact | Role |
| --- | --- |
| `robot_perception/yolo_detector_node.py` | Detector |
| `launch/perception.launch.py` | usb_cam + detector |
| `config/usb_cam_params.yaml` | Camera settings |
| `models/yolo26n.pt` | Ultralytics YOLO26-nano base |
| `models/target_object_n.pt` | Fine-tuned mission detector |
| `models/target_object_n.onnx` | ONNX export for TensorRT |
| `models/README.md` | Train/export instructions |

## Detector lifecycle

1. Declare parameters (`weights_path`, `confidence_threshold`, `inference_hz`, …). 
2. Load `YOLO(weights)`; if file missing, log error and leave `_model is None` (timers no-op). 
3. Store latest `/image_raw` (best-effort QoS). 
4. On timer (default 8 Hz): cv_bridge → BGR numpy → `model.predict` → build `Detection2DArray`.

## Why rate-limit

Unbounded YOLO on Orin Nano contends with slam_toolbox and Nav2 controllers. Project default **8 Hz** keeps detection useful without starving mapping.

## Inputs / outputs

| In | Out |
| --- | --- |
| `/image_raw` (`sensor_msgs/Image`) | `/detections` (`Detection2DArray`) |
| `.engine` weights file | Logs |

## Assumptions

- Class names in the engine match what `mission_node.target_class` expects (default `target_object`). 
- Engine built on **this** Jetson’s TensorRT version.

## Failure modes

| Symptom | Fix |
| --- | --- |
| No detections | Missing engine, low confidence, wrong topic/QoS |
| USB camera stalls with LiDAR | Use powered hub |
| ImportError ultralytics | Install Jetson-compatible stack |

## Training note

We collected ~100-200 labeled images with augmentation for one distinctive object - from our labeled target-object dataset.

## Related

- [Detection & mission workflow](../workflows/detection-mission.md) 
- [models/README](../../robot_ws/src/robot_perception/models/README.md) 
