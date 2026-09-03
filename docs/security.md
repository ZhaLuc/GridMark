# Security Considerations

This is a research/education robot stack, not a hardened product. Reviewers should treat the ROS graph and USB links as **trusted-lab** components.

## Physical / electrical

| Risk | Mitigation in design docs |
| --- | --- |
| LiPo fire / abuse | Balance charge, fuse on B+, storage practices (BOM/power wiring) |
| Motor stall brown-out | Isolated motor vs compute rails |
| Reverse polarity on BTS7960 | Pin tables; verify before power |

## Cyber / software

| Risk | Status in this repo |
| --- | --- |
| Unauthenticated `/cmd_vel` | Anyone on the ROS domain can drive - use isolated network |
| Serial spoofing | No auth on USB CDC ACM |
| Model supply chain | You train/export your own `.engine`; do not trust random binaries |
| RCE via pickle/weights | Prefer official Ultralytics export path; keep Jetson patched |

## Privacy

Camera frames may leave the robot if you remapping/record bags - handle datasets carefully.

## Recommendations

1. Dedicated Wi-Fi / no default public DDS discovery exposure. 
2. Disable unused USB gadgets. 
3. Store LiPo safely when unattended. 
4. E-stop: hardware switch on battery positive (documented power tree). 

## Related

- [Power wiring](hardware/wiring/power-wiring.md) 
- [Performance](performance.md) (resource exhaustion as availability issue) 
