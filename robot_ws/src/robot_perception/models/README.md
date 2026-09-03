# YOLO26 detection weights

Shipped weights for `yolo_detector_node` on this robot.

| File | Role |
| --- | --- |
| `yolo26n.pt` | Ultralytics YOLO26-nano base checkpoint (COCO-pretrained) |
| `target_object_n.pt` | Fine-tuned detector used for mission targets |
| `target_object_n.onnx` | ONNX export used for TensorRT conversion on the Orin Nano Super |

## Training performed

Base checkpoint: `yolo26n.pt` from the Ultralytics release assets (YOLO26-nano).

Bring-up fine-tune (recorded under `models/runs/`, gitignored):

```bash
yolo detect train model=yolo26n.pt data=coco8.yaml epochs=3 imgsz=640 \
  project=runs name=target_object_n exist_ok=true
```

Resulting weights were copied to `target_object_n.pt` and exported:

```bash
yolo export model=target_object_n.pt format=onnx
```

On the Orin Nano Super, convert to TensorRT for production inference:

```python
from ultralytics import YOLO
YOLO("target_object_n.pt").export(format="engine", device=0)
```

Point `weights_path` at the `.engine` after export, or keep `.pt` / `.onnx` for bring-up and CPU/GPU PyTorch inference.

## Runtime

Default ROS parameter: `weights_path:=.../target_object_n.pt` (see `perception.launch.py`).
Inference is rate-limited to 8 Hz so SLAM and Nav2 retain GPU/CPU headroom.
