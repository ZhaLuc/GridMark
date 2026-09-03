# FAQ

## Is this a complete robot project?

Yes. The repository includes Arduino firmware, the ROS 2 workspace, trained YOLO26 weights (`.pt` / `.onnx`), hardware BOM and wiring, operating captures, and field validation records for the assembled Jetson + Mega platform.

## Do I need TensorRT to run perception?

For production on the Orin Nano Super, export a TensorRT `.engine` from `target_object_n.pt` (see `robot_perception/models/README.md`). Bring-up can run on the shipped `.pt` or `.onnx` files.

## Why is YOLO capped at 8 Hz?

Unbounded inference contends with `slam_toolbox` and Nav2 on the Orin Nano. The rate limit keeps mapping and control responsive while detections remain useful for the mission node.

## Where are calibration numbers?

Odometry geometry lives in firmware constants and `robot_bridge`’s `odom_calibration.yaml`. Validation runs are summarized in [field-test-log.md](field-test-log.md).

## Can I change the target class?

Retrain or fine-tune with Ultralytics, update `weights_path` / class filters, and keep the `/detections` → mission contract unchanged.

## Why isolate motor power from the Jetson?

Stall current on gear motors can brown out a shared 5 V rail. Motor pack → BTS7960 is separate from pack → buck → Jetson 5 V.

## Related

- [System overview](system-overview.md)
- [Troubleshooting](troubleshooting.md)
- [Glossary](glossary.md)
