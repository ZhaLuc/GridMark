# FAQ

## Is this a complete robot project?

Yes. The repository includes Arduino firmware, the ROS 2 workspace, trained YOLO26 weights (`.pt` / `.onnx`), hardware BOM and wiring, operating captures, and field validation records for the assembled Jetson + Mega platform.

## Do I need TensorRT to run perception?

For production on the Orin Nano Super, export a TensorRT `.engine` from `target_object_n.pt` (see `robot_perception/models/README.md`). Bring-up can run on the shipped `.pt` or `.onnx` files.

## Why is YOLO capped at 8 Hz?

Unbounded inference contends with `slam_toolbox` and Nav2 on the Orin Nano. The rate limit keeps mapping and control responsive while detections remain useful for the mission node.

## Where are calibration numbers?
