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
