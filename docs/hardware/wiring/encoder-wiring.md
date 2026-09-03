# Encoder Wiring (Quadrature → Arduino Mega Interrupts)

Each driven side uses a quadrature (A/B) encoder for wheel odometry. Channels are wired to the Mega’s **external interrupt-capable** pins so every rising/falling edge can be captured even when the main `loop()` is busy with serial I/O or motor updates.

## Schematic

![Encoder wiring schematic](../../images/schematics/schematic-encoders.png)

## Why interrupt pins are required

Quadrature decoding advances (or retreats) a tick count on **every edge** of A and/or B, depending on the decode mode (×1 / ×2 / ×4). At typical gear-motor speeds, edge rates are high enough that polling inside `loop()` will miss edges whenever the CPU is blocked on other work (USB serial to the Jetson, PWM updates, etc.). Missed edges become odometry slip and corrupt `/odom`.

The Arduino Mega 2560 exposes external interrupts on pins **2, 3, 18, 19, 20, 21**. This project uses four of them for the two encoders (A/B × left/right). Pins 20/21 remain free (also used for I2C SDA/SCL if a future sensor needs the bus).

## Channel assignment

| Encoder | Channel | Arduino Mega pin | Interrupt capability |
| --- | --- | --- | --- |
| Left | A | **D2** | External interrupt |
| Left | B | **D3** | External interrupt |
| Right | A | **D18** | External interrupt |
| Right | B | **D19** | External interrupt |

## Power and ground

Encoder modules on these chassis kits are typically **5 V** logic devices. Power them from the Mega’s regulated 5 V (or a shared clean 5 V logic rail referenced to Mega GND) - **not** from the raw 3S LiPo.

| Supply | Connection |
| --- | --- |
| Encoder VCC (left and right) | Arduino Mega **5V** |
| Encoder GND (left and right) | Arduino Mega **GND** |

Share a single solid GND between Mega, encoders, and BTS7960 **logic** grounds so A/B thresholds are valid. Motor high-current return stays on the pack/BTS7960 power harness (see power wiring).

## Plain-text pin table
