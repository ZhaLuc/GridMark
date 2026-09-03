# Workflow: Exploration

Unattended coverage using frontier centroids as Nav2 goals.

## Preconditions

- Healthy `/map` from mapping workflow 
- Nav2 up (`navigation.launch.py` or full bringup) 
- Footprint/inflation match chassis 

## Behavior

`frontier_explorer_node` sends `NavigateToPose` goals until no frontier clusters remain, then publishes `/exploration_complete`.

Mission may interrupt exploration when the target is confirmed (cancel + zero velocity).

## Operator tips

- Clear large obstacles before first unattended run. 
- Watch recovery behaviors (spin/backup) - constant recovery ⇒ costmap/footprint issue. 
- If goals always rejected, ensure `allow_unknown` remains true and map is non-empty.

## Related

- [robot_navigation](../packages/robot_navigation.md) 
- [Verification §3](../verification-checklist.md) 
