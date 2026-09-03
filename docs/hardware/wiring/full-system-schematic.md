# Full System Schematic

Consolidated interconnection view for the GridMark. Prefer the
rendered schematic image below for assembly reviews; Mermaid remains available
for text diffs. For pin-level detail, use the sibling docs: [power-wiring.md](power-wiring.md), [motor-driver-wiring.md](motor-driver-wiring.md), [encoder-wiring.md](encoder-wiring.md), [lidar-and-camera-wiring.md](lidar-and-camera-wiring.md).

## Rendered schematic

![Full system interconnect schematic](../../images/schematics/schematic-full-system.png)

## Visual reference (assembled robot)

![Robot top view](../../images/robot/robot-top-view.jpg)

## Consolidated Mermaid schematic

```mermaid
flowchart TB
  subgraph Power["Power"]
    LiPo["3S LiPo 11.1V"]
    Fuse[Fuse]
    SW[Main power switch]
    Buck["Buck converter → 5V regulated"]
    HubPSU[Powered USB hub PSU]
    LiPo --> Fuse --> SW
    SW --> Buck
    SW --> HubPSU
  end

  subgraph LowLevel["Low-level control (Arduino)"]
    Mega[Arduino Mega 2560]
    LDRV[Left BTS7960]
    RDRV[Right BTS7960]
    LMot["Left DC motor pair parallel"]
    RMot["Right DC motor pair parallel"]
    LEnc[Left quadrature encoder]
    REnc[Right quadrature encoder]

    Mega -->|"D22 EN / D5 RPWM / D6 LPWM"| LDRV
    Mega -->|"D23 EN / D9 RPWM / D10 LPWM"| RDRV
    LDRV --> LMot
    RDRV --> RMot
    LEnc -->|"A→D2 B→D3"| Mega
    REnc -->|"A→D18 B→D19"| Mega
  end

  subgraph HighLevel["High-level compute (Jetson)"]
    Jetson[Jetson Orin Nano Super Developer Kit]
    Hub[Powered USB hub]
    LiDAR[RPLIDAR A2]
    Cam[USB webcam]

    Jetson --> Hub
    Hub --> LiDAR
    Hub --> Cam
  end

  SW -->|"B+/B- motor rail"| LDRV
  SW -->|"B+/B- motor rail"| RDRV
  Buck -->|"5V DC input"| Jetson
  HubPSU --> Hub
  Jetson -->|"USB-B serial + optional Mega power"| Mega
```

## Signal / power legend (plain text)

| From | To | What |
| --- | --- | --- |
| 3S LiPo → fuse → switch | Both BTS7960 B+/B− | Motor power |
| Switch → buck → 5 V | Jetson DC / barrel input | Isolated compute power |
| Switch / wall → hub PSU | Powered USB hub | LiDAR + camera device power |
| Jetson USB | Powered hub upstream | Sensor data |
| Hub | RPLIDAR A2 USB adapter | `/scan` path |
| Hub | USB webcam | `/image_raw` path |
| Jetson USB | Arduino Mega USB-B | Serial bridge + optional Mega 5 V |
| Mega D22/D5/D6 | Left BTS7960 | Enable + PWM |
| Mega D23/D9/D10 | Right BTS7960 | Enable + PWM |
| Left encoder A/B | Mega D2 / D3 | Quadrature IRQs |
| Right encoder A/B | Mega D18 / D19 | Quadrature IRQs |
| Left/right BTS7960 M+/M− | Left/right motor pairs | Drive |
| Mega 5V/GND | Encoder VCC/GND + driver logic VCC/GND | Logic supply / reference |

## Related ROS topic contract (software side)

Once powered and launched, the software architecture expects:

| Topic | Type | Producer |
| --- | --- | --- |
| `/scan` | `sensor_msgs/LaserScan` | `rplidar_ros` |
| `/odom` | `nav_msgs/Odometry` | `robot_bridge` (from Mega encoder stream) |
| `/cmd_vel` | `geometry_msgs/Twist` | Nav2 → `robot_bridge` → Mega → BTS7960 |
| `/image_raw` | `sensor_msgs/Image` | `usb_cam` |
| `/map` | `nav_msgs/OccupancyGrid` | `slam_toolbox` |

TF: `map` → `odom` → `base_link` → `{lidar_link, camera_link}`.
