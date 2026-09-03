# Performance

## Orin Nano Super budget

| Workload | Guidance in this project |
| --- | --- |
| slam_toolbox async | Continuous while moving |
| Nav2 controller @ 20 Hz | Keep footprint/inflation reasonable |
| YOLO | **Cap at ~8 Hz** default |
| usb_cam 640×480 | Prefer over 1080p for headroom |

## Bottlenecks observed in design (not bench numbers)

Benchmarks from our Orin Nano Super bring-up:

- USB contention without powered hub → scan drops 
- Unbounded YOLO → map update lag / controller timeouts 
- Huge occupancy maps → frontier O(W×H) cost every replan 

## Tunables that affect load

| Knob | Effect |
| --- | --- |
| `inference_hz` | Detector GPU/CPU |
| `throttle_scans` / travel gates | SLAM graph rate |
| Local costmap size 3×3 m | Controller CPU |
| `cmd_send_hz` | Serial traffic (keep ~20) |

## Latency path (cmd → motion)

Teleop/Nav2 → bridge timer (≤50 ms) → USB → Mega loop (20 ms) → PWM. Firmware timeout 500 ms is a safety ceiling, not a performance target.

## Related

- [Configuration](configuration.md) 
- [Troubleshooting](troubleshooting.md) 
