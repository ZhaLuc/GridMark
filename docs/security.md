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
