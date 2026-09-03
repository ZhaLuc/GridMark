# Bill of Materials

Bill of materials for the robot we built. Confirm current vendor SKUs if reordering.

Approximate prices below are order-of-magnitude USD figures based on common retail listings for these product classes at the time this document was drafted. Prices reflect the SKUs we ordered; re-check vendors for current quotes.

```mermaid
flowchart LR
  Chassis[4WD chassis + motors/encoders]
  Mega[Arduino Mega 2560]
  Jetson[Jetson Orin Nano Super]
  LiDAR[RPLIDAR A2]
  Driver[BTS7960 x2]
  Cam[USB webcam]
  Batt[3S LiPo]
  Buck[5V buck converter]
  Hub[Powered USB hub]
  Mech[Mounts / wiring]

  Chassis --> Mega
