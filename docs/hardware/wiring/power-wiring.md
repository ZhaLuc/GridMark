# Power Wiring

Motors and compute must not share an unprotected low-impedance rail. Gear-motor **stall** current can pull a shared 5 V/USB supply into brown-out, resetting the Jetson or Arduino mid-run. This project isolates **motor power** (raw pack → BTS7960) from **compute power** (pack → buck → regulated 5 V → Jetson).

## Schematic

![Power tree schematic](../../images/schematics/schematic-power-tree.png)

## Power tree (logical)

1. **3S LiPo 11.1 V** pack 
2. → **Main power switch** (and fuse on B+) 
3. → Split: 
   - **(a) Motor branch:** switched pack voltage → both BTS7960 **B+/B−** (and thus the paralleled motor pairs) 
   - **(b) Compute branch:** switched pack voltage → **buck converter** → clean regulated **5 V** → Jetson Orin Nano Super **barrel / DC input**

Arduino Mega 2560 is powered **separately** via its **USB-B** port from a Jetson USB port (convenient for serial bridge + 5 V logic supply), **or** from a dedicated 5 V / ≥2 A regulator if you want the Mega electrically isolated from the Jetson’s USB bus.

## Reasoning

| Concern | Mitigation in this design |
| --- | --- |
| Motor stall / PWM current spikes | Heavy gauge wire + fuse; BTS7960 fed directly from pack; not from Jetson 5 V |
| Jetson brown-out under CUDA + USB devices | Dedicated buck to Jetson DC input; sensors on **powered** USB hub |
| Ground loops / logic reference | Common **signal** GND between Mega, driver logic GND, encoders; high current returns stay on pack negative |
| USB bus overload | LiDAR + camera on externally powered hub (see LiDAR/camera wiring) |

## Plain-text connection table

| Component | Pin / terminal | Connects to |
