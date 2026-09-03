# Workflow: Mapping

Build an occupancy map with teleop or slow autonomous motion while slam_toolbox runs.

## Goal

Produce a `/map` whose walls are **thin and straight** after a closed loop.

## Procedure

1. Start bridge + LiDAR + `ros2 launch robot_slam slam.launch.py` (or full bringup). 
2. RViz: Fixed Frame `map`; displays Map, LaserScan, TF, Odometry. 
3. Teleop a slow perimeter. 
4. If walls smear → **stop and recalibrate odometry** (Phase 2). Do not only retune SLAM.

## Pass criteria

- Continuous `/map` updates 
- Walls thin/straight after loop 
- TF `map`→`odom`→`base_link`→`lidar_link` complete 

## Related

- [Build phases Phase 5](../build-phases.md) 
- [Verification §2](../verification-checklist.md) 
