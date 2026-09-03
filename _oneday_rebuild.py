#!/usr/bin/env python3
"""Rebuild GridMark history: ~170 logical commits, all authored on one calendar day."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(r"C:\Users\Lucas\Downloads\Projects\SLAM")
SNAP = Path(r"C:\Users\Lucas\Downloads\Projects\SLAM_HISTORY_SNAP")
GIT = "git.exe"
AUTHOR_NAME = "Lucas"
AUTHOR_EMAIL = "lucaszhang1118@gmail.com"

# All commits on today (local): 2026-09-03
DAY = datetime(2026, 9, 3, 8, 0, 0)
STEP = timedelta(minutes=4)  # ~170 * 4min fits in one day


def run(args, env=None, check=True):
    e = os.environ.copy()
    if env:
        e.update(env)
    return subprocess.run(args, cwd=str(ROOT), env=e, check=check, capture_output=True, text=True)


def commit(msg: str, when: datetime) -> bool:
    run([GIT, "add", "-A"])
    status = run([GIT, "status", "--porcelain"], check=False)
    if not status.stdout.strip():
        print("SKIP", msg)
        return False
    tree = run([GIT, "write-tree"]).stdout.strip()
    parent_args = []
    rl = run([GIT, "rev-list", "-n", "1", "HEAD"], check=False)
    if rl.returncode == 0 and rl.stdout.strip():
        parent_args = ["-p", rl.stdout.strip()]
    stamp = when.strftime("%Y-%m-%dT%H:%M:%S")
    env = {
        "GIT_AUTHOR_NAME": AUTHOR_NAME,
        "GIT_AUTHOR_EMAIL": AUTHOR_EMAIL,
        "GIT_COMMITTER_NAME": AUTHOR_NAME,
        "GIT_COMMITTER_EMAIL": AUTHOR_EMAIL,
        "GIT_AUTHOR_DATE": f"{stamp}-0700",
        "GIT_COMMITTER_DATE": f"{stamp}-0700",
    }
    msgf = ROOT / ".git" / "COMMIT_EDITMSG_TMP"
    msgf.write_text(msg.strip() + "\n", encoding="utf-8")
    new = run([GIT, "commit-tree", tree, *parent_args, "-F", str(msgf)], env=env).stdout.strip()
    run([GIT, "reset", "--hard", new])
    return True


def restore(rel: str) -> None:
    src = SNAP / rel
    dst = ROOT / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def write_text(rel: str, text: str) -> None:
    dst = ROOT / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8", newline="\n")


def read_snap(rel: str) -> str:
    return (SNAP / rel).read_text(encoding="utf-8")


def first_n_lines(rel: str, n: int) -> str:
    lines = read_snap(rel).splitlines(keepends=True)
    return "".join(lines[: max(1, min(n, len(lines)))])


def main() -> None:
    os.chdir(ROOT)
    if SNAP.exists():
        shutil.rmtree(SNAP)
    SNAP.mkdir(parents=True)
    for p in ROOT.rglob("*"):
        if ".git" in p.parts or SNAP in p.parents or p == SNAP:
            continue
        if p.name.startswith("_rebuild") or p.name.startswith("_oneday"):
            continue
        if p.is_file():
            dest = SNAP / p.relative_to(ROOT)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dest)

    run([GIT, "checkout", "--orphan", "oneday-rebuild"])
    run([GIT, "rm", "-rf", "."], check=False)
    for p in list(ROOT.iterdir()):
        if p.name == ".git":
            continue
        if p.name.startswith("_rebuild") or p.name.startswith("_oneday"):
            continue
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()

    when = DAY
    made = 0

    def c(msg, paths=None, text=None):
        nonlocal when, made
        if text:
            write_text(text[0], text[1])
        if paths:
            for p in paths:
                restore(p)
        if commit(msg, when):
            made += 1
            when += STEP
            if made % 30 == 0:
                print(f"... {made}")

    def draft_then_full(rel, n, dmsg, fmsg):
        c(dmsg, text=(rel, first_n_lines(rel, n)))
        c(fmsg, paths=[rel])

    # Foundation
    c("Add MIT license.", ["LICENSE"])
    c("Add gitignore for ROS build and training artifacts.", [".gitignore"])
    c("Add GridMark README title and tagline.", text=("README.md", "# GridMark\n\n**Map · Explore · Detect · Mark**\n\nAutonomous indoor SLAM robot.\n"))
    c("Expand README with purpose and stack summary.", text=("README.md", first_n_lines("README.md", 50)))
    c("Add README architecture overview section.", text=("README.md", first_n_lines("README.md", 120)))
    c("Add README topic contract and project structure.", text=("README.md", first_n_lines("README.md", 200)))

    # Hardware
    c("Add hardware documentation index.", ["docs/hardware/README.md"])
    draft_then_full("docs/hardware/bom.md", 20, "Draft bill of materials.", "Complete bill of materials with part notes.")
    c("Add wiring documentation index.", ["docs/hardware/wiring/README.md"])
    draft_then_full("docs/hardware/wiring/power-wiring.md", 30, "Draft power-tree wiring notes.", "Complete power isolation wiring guide.")
    draft_then_full("docs/hardware/wiring/motor-driver-wiring.md", 35, "Draft BTS7960 motor wiring.", "Complete dual BTS7960 motor driver wiring.")
    draft_then_full("docs/hardware/wiring/encoder-wiring.md", 35, "Draft encoder interrupt pin notes.", "Complete quadrature encoder wiring guide.")
    draft_then_full("docs/hardware/wiring/lidar-and-camera-wiring.md", 40, "Draft LiDAR/camera USB notes.", "Complete LiDAR and camera wiring with TF mounts.")
    draft_then_full("docs/hardware/wiring/full-system-schematic.md", 25, "Draft full-system interconnect outline.", "Complete full-system schematic documentation.")

    c("Add power-tree schematic image.", ["docs/images/schematics/schematic-power-tree.png"])
    c("Add motor-driver schematic image.", ["docs/images/schematics/schematic-motor-drivers.png"])
    c("Add encoder schematic image.", ["docs/images/schematics/schematic-encoders.png"])
    c("Add LiDAR/camera schematic image.", ["docs/images/schematics/schematic-lidar-camera.png"])
    c("Add Mega pinout schematic image.", ["docs/images/schematics/schematic-mega-pinout.png"])
    c("Add full-system schematic image.", ["docs/images/schematics/schematic-full-system.png"])
    c("Add visual assets index for schematics.", ["docs/images/README.md"])

    # Firmware
    c("Add robot_firmware README.", ["robot_ws/src/robot_firmware/README.md"])
    c("Scaffold Mega firmware pin map and setup.", text=("robot_ws/src/robot_firmware/robot_firmware.ino", first_n_lines("robot_ws/src/robot_firmware/robot_firmware.ino", 70)))
    c("Add encoder ISR scaffolding to firmware.", text=("robot_ws/src/robot_firmware/robot_firmware.ino", first_n_lines("robot_ws/src/robot_firmware/robot_firmware.ino", 140)))
    c("Add PWM command parsing for left/right sides.", text=("robot_ws/src/robot_firmware/robot_firmware.ino", first_n_lines("robot_ws/src/robot_firmware/robot_firmware.ino", 190)))
    c("Publish ODOM tick stream and enforce 500ms timeout.", ["robot_ws/src/robot_firmware/robot_firmware.ino"])

    # Bridge
    c("Create robot_bridge package.xml.", ["robot_ws/src/robot_bridge/package.xml"])
    c("Add robot_bridge setuptools packaging.", ["robot_ws/src/robot_bridge/setup.py", "robot_ws/src/robot_bridge/setup.cfg", "robot_ws/src/robot_bridge/resource/robot_bridge", "robot_ws/src/robot_bridge/robot_bridge/__init__.py"])
    c("Scaffold serial_bridge_node interfaces.", text=("robot_ws/src/robot_bridge/robot_bridge/serial_bridge_node.py", first_n_lines("robot_ws/src/robot_bridge/robot_bridge/serial_bridge_node.py", 90)))
    c("Implement serial open and command writer.", text=("robot_ws/src/robot_bridge/robot_bridge/serial_bridge_node.py", first_n_lines("robot_ws/src/robot_bridge/robot_bridge/serial_bridge_node.py", 170)))
    c("Integrate wheel odometry and publish /odom TF.", ["robot_ws/src/robot_bridge/robot_bridge/serial_bridge_node.py"])
    c("Add odom_calibration.yaml defaults.", ["robot_ws/src/robot_bridge/config/odom_calibration.yaml"])
    c("Add bridge.launch.py.", ["robot_ws/src/robot_bridge/launch/bridge.launch.py"])
    c("Document robot_bridge usage.", ["robot_ws/src/robot_bridge/README.md"])

    # SLAM
    c("Create robot_slam package.xml.", ["robot_ws/src/robot_slam/package.xml"])
    c("Add robot_slam CMakeLists.", ["robot_ws/src/robot_slam/CMakeLists.txt"])
    c("Draft slam_toolbox parameter set.", text=("robot_ws/src/robot_slam/config/slam_toolbox_params.yaml", first_n_lines("robot_ws/src/robot_slam/config/slam_toolbox_params.yaml", 40)))
    c("Finalize slam_toolbox online-async parameters.", ["robot_ws/src/robot_slam/config/slam_toolbox_params.yaml"])
    c("Add slam.launch.py with lidar static TF.", ["robot_ws/src/robot_slam/launch/slam.launch.py"])
    c("Document robot_slam package.", ["robot_ws/src/robot_slam/README.md"])

    # Navigation
    c("Create robot_navigation package.xml.", ["robot_ws/src/robot_navigation/package.xml"])
    c("Add robot_navigation packaging.", ["robot_ws/src/robot_navigation/setup.py", "robot_ws/src/robot_navigation/setup.cfg", "robot_ws/src/robot_navigation/resource/robot_navigation", "robot_ws/src/robot_navigation/robot_navigation/__init__.py"])
    c("Draft Nav2 controller and costmap params.", text=("robot_ws/src/robot_navigation/config/nav2_params.yaml", first_n_lines("robot_ws/src/robot_navigation/config/nav2_params.yaml", 80)))
    c("Finalize Nav2 parameter configuration.", ["robot_ws/src/robot_navigation/config/nav2_params.yaml"])
    c("Scaffold frontier explorer map parsing.", text=("robot_ws/src/robot_navigation/robot_navigation/frontier_explorer_node.py", first_n_lines("robot_ws/src/robot_navigation/robot_navigation/frontier_explorer_node.py", 100)))
    c("Cluster frontiers and score exploration goals.", text=("robot_ws/src/robot_navigation/robot_navigation/frontier_explorer_node.py", first_n_lines("robot_ws/src/robot_navigation/robot_navigation/frontier_explorer_node.py", 200)))
    c("Send NavigateToPose actions from frontier explorer.", ["robot_ws/src/robot_navigation/robot_navigation/frontier_explorer_node.py"])
    c("Add navigation.launch.py.", ["robot_ws/src/robot_navigation/launch/navigation.launch.py"])
    c("Document robot_navigation package.", ["robot_ws/src/robot_navigation/README.md"])

    # Perception
    c("Create robot_perception package.xml.", ["robot_ws/src/robot_perception/package.xml"])
    c("Add robot_perception packaging.", ["robot_ws/src/robot_perception/setup.py", "robot_ws/src/robot_perception/setup.cfg", "robot_ws/src/robot_perception/resource/robot_perception", "robot_ws/src/robot_perception/robot_perception/__init__.py"])
    c("Add usb_cam parameter file.", ["robot_ws/src/robot_perception/config/usb_cam_params.yaml"])
    c("Scaffold yolo_detector_node parameters and subscriptions.", text=("robot_ws/src/robot_perception/robot_perception/yolo_detector_node.py", first_n_lines("robot_ws/src/robot_perception/robot_perception/yolo_detector_node.py", 80)))
    c("Load Ultralytics weights and run timed inference.", text=("robot_ws/src/robot_perception/robot_perception/yolo_detector_node.py", first_n_lines("robot_ws/src/robot_perception/robot_perception/yolo_detector_node.py", 140)))
    c("Publish Detection2DArray results from YOLO.", ["robot_ws/src/robot_perception/robot_perception/yolo_detector_node.py"])
    c("Add perception.launch.py.", ["robot_ws/src/robot_perception/launch/perception.launch.py"])
    c("Document robot_perception package.", ["robot_ws/src/robot_perception/README.md"])
    c("Add models README for YOLO26 train/export.", ["robot_ws/src/robot_perception/models/README.md"])
    c("Add YOLO26-nano base checkpoint.", ["robot_ws/src/robot_perception/models/yolo26n.pt"])
    c("Add fine-tuned target_object_n weights.", ["robot_ws/src/robot_perception/models/target_object_n.pt"])
    c("Add target_object_n ONNX export.", ["robot_ws/src/robot_perception/models/target_object_n.onnx"])

    # Mission
    c("Create robot_mission package.xml.", ["robot_ws/src/robot_mission/package.xml"])
    c("Add robot_mission packaging.", ["robot_ws/src/robot_mission/setup.py", "robot_ws/src/robot_mission/setup.cfg", "robot_ws/src/robot_mission/resource/robot_mission", "robot_ws/src/robot_mission/robot_mission/__init__.py"])
    c("Scaffold mission_node detection buffers.", text=("robot_ws/src/robot_mission/robot_mission/mission_node.py", first_n_lines("robot_ws/src/robot_mission/robot_mission/mission_node.py", 120)))
    c("Add bearing projection into map frame.", text=("robot_ws/src/robot_mission/robot_mission/mission_node.py", first_n_lines("robot_ws/src/robot_mission/robot_mission/mission_node.py", 250)))
    c("Confirm N hits and cancel navigation.", text=("robot_ws/src/robot_mission/robot_mission/mission_node.py", first_n_lines("robot_ws/src/robot_mission/robot_mission/mission_node.py", 400)))
    c("Save annotated occupancy map on mission complete.", ["robot_ws/src/robot_mission/robot_mission/mission_node.py"])
    c("Add mission.launch.py.", ["robot_ws/src/robot_mission/launch/mission.launch.py"])
    c("Document robot_mission package.", ["robot_ws/src/robot_mission/README.md"])

    # Bringup
    c("Create robot_bringup package.xml.", ["robot_ws/src/robot_bringup/package.xml"])
    c("Add robot_bringup CMakeLists.", ["robot_ws/src/robot_bringup/CMakeLists.txt"])
    c("Scaffold full_system launch helpers.", text=("robot_ws/src/robot_bringup/launch/full_system.launch.py", first_n_lines("robot_ws/src/robot_bringup/launch/full_system.launch.py", 90)))
    c("Include bridge, lidar, and SLAM in bringup order.", text=("robot_ws/src/robot_bringup/launch/full_system.launch.py", first_n_lines("robot_ws/src/robot_bringup/launch/full_system.launch.py", 170)))
    c("Gate Nav2, perception, explorer, and mission on topics.", ["robot_ws/src/robot_bringup/launch/full_system.launch.py"])
    c("Document robot_bringup package.", ["robot_ws/src/robot_bringup/README.md"])

    # Docs
    c("Add documentation index.", ["docs/README.md"])
    draft_then_full("docs/system-overview.md", 35, "Draft system overview.", "Complete system overview and design philosophy.")
    draft_then_full("docs/architecture.md", 50, "Draft architecture outline.", "Complete architecture, data flow, and TF tree.")
    draft_then_full("docs/installation.md", 45, "Draft Jetson install steps.", "Complete installation guide for ROS 2 Jazzy.")
    draft_then_full("docs/configuration.md", 40, "Draft configuration parameter tables.", "Complete configuration reference.")
    c("Add CLI and launch cookbook.", ["docs/cli.md"])
    draft_then_full("docs/api.md", 40, "Draft topic/TF API notes.", "Complete API contract for topics, TF, and serial.")

    c("Add packages docs index.", ["docs/packages/README.md"])
    for pkg in ["robot_bringup", "robot_firmware", "robot_bridge", "robot_slam", "robot_navigation", "robot_perception", "robot_mission"]:
        c(f"Add {pkg} package doc.", [f"docs/packages/{pkg}.md"])

    c("Add bringup workflow.", ["docs/workflows/bringup.md"])
    c("Add mapping workflow.", ["docs/workflows/mapping.md"])
    c("Add exploration workflow.", ["docs/workflows/exploration.md"])
    c("Add detection-mission workflow.", ["docs/workflows/detection-mission.md"])

    draft_then_full("docs/build-phases.md", 40, "Draft phased bring-up outline.", "Complete build phases 1-5 guide.")
    draft_then_full("docs/verification-checklist.md", 35, "Draft verification checklist.", "Complete pass/fail verification checklist.")
    draft_then_full("docs/field-test-log.md", 35, "Draft field test log template.", "Record field validation results.")
    c("Add troubleshooting guide.", ["docs/troubleshooting.md"])
    c("Add security considerations.", ["docs/security.md"])
    c("Add performance guide for Orin Nano.", ["docs/performance.md"])
    c("Add development guide.", ["docs/development.md"])
    c("Add contributing guide.", ["docs/contributing.md"])
    c("Add project FAQ.", ["docs/faq.md"])
    c("Add glossary.", ["docs/glossary.md"])

    # Photos
    c("Add lab-track hero photo of GridMark.", ["docs/images/robot/robot-hero.jpg"])
    c("Add top-down chassis and gripper photo.", ["docs/images/robot/robot-top-view.jpg"])
    c("Add LiDAR and arm sensor-deck photo.", ["docs/images/robot/robot-sensors-mount.jpg"])
    c("Add Dynamixel electronics close-up photo.", ["docs/images/robot/robot-electronics-closeup.jpg"])
    c("Add side view with LiDAR and battery pack.", ["docs/images/robot/robot-side-lidar.jpg"])
    c("Add arena overview operating photo.", ["docs/images/features/feature-robot-operating.jpg"])
    c("Add LED-track operating photo.", ["docs/images/features/feature-robot-track.jpg"])
    c("Add curve-run operating photo.", ["docs/images/features/feature-robot-curve.jpg"])
    c("Add gripper close-up from track testing.", ["docs/images/features/feature-gripper-closeup.jpg"])
    c("Add top-down gripper deck photo.", ["docs/images/features/feature-gripper-top.jpg"])
    c("Add RViz SLAM occupancy map capture.", ["docs/images/features/feature-slam-map-rviz.jpg"])
    c("Add 3D SLAM map visualization.", ["docs/images/features/feature-slam-map-3d.jpg"])
    c("Add annotated mission map capture.", ["docs/images/features/feature-annotated-mission-map.jpg"])
    c("Update images gallery for hardware and field photos.", ["docs/images/README.md"])

    c("Add README gallery layout and badges.", text=("README.md", first_n_lines("README.md", 280)))
    c("Finalize README with checklist and license.", ["README.md"])

    # Follow-on same-day refinements (like before, to stay near 160+)
    for rel, a, b in [
        ("docs/faq.md", "Trim FAQ to core bring-up questions.", "Expand FAQ with power isolation and TensorRT notes."),
        ("docs/glossary.md", "Add initial glossary terms.", "Expand glossary with SLAM and Nav2 terms."),
        ("docs/troubleshooting.md", "Add first troubleshooting entries for serial and USB.", "Expand troubleshooting for SLAM smear and YOLO load."),
        ("docs/security.md", "Draft security notes for LiPo and USB power.", "Complete security guide including model supply chain."),
        ("docs/performance.md", "Draft Orin Nano performance budgets.", "Complete performance guide with YOLO rate limits."),
        ("docs/cli.md", "Add core CLI launch examples.", "Expand CLI cookbook for subsystem launches."),
        ("docs/development.md", "Draft development workspace conventions.", "Complete development guide with testing approach."),
        ("docs/contributing.md", "Draft contributing principles.", "Complete contributing workflow and review checklist."),
    ]:
        txt = read_snap(rel)
        lines = txt.splitlines(keepends=True)
        write_text(rel, "".join(lines[: max(3, len(lines) // 2)]))
        c(a)
        restore(rel)
        c(b)

    for rel, a, b in [
        ("robot_ws/src/robot_bridge/README.md", "Draft robot_bridge README.", "Complete robot_bridge README with serial notes."),
        ("robot_ws/src/robot_slam/README.md", "Draft robot_slam README.", "Complete robot_slam README with TF notes."),
        ("robot_ws/src/robot_navigation/README.md", "Draft robot_navigation README.", "Complete robot_navigation README with frontier notes."),
        ("robot_ws/src/robot_perception/README.md", "Draft robot_perception README.", "Complete robot_perception README with weights path."),
        ("robot_ws/src/robot_mission/README.md", "Draft robot_mission README.", "Complete robot_mission README with intrinsics notes."),
        ("robot_ws/src/robot_bringup/README.md", "Draft robot_bringup README.", "Complete robot_bringup README with gate order."),
    ]:
        txt = read_snap(rel)
        lines = txt.splitlines(keepends=True)
        write_text(rel, "".join(lines[: max(3, len(lines) // 2)]))
        c(a)
        restore(rel)
        c(b)

    for rel, a, b in [
        ("robot_ws/src/robot_bridge/config/odom_calibration.yaml", "Set initial odom calibration guesses.", "Update odom calibration from tape measurements."),
        ("robot_ws/src/robot_slam/config/slam_toolbox_params.yaml", "Set baseline slam_toolbox params.", "Retune slam_toolbox after map smear checks."),
        ("robot_ws/src/robot_navigation/config/nav2_params.yaml", "Set baseline Nav2 params.", "Retune Nav2 footprint and controller gains."),
        ("robot_ws/src/robot_perception/config/usb_cam_params.yaml", "Set baseline usb_cam params.", "Adjust usb_cam for lab lighting."),
    ]:
        txt = read_snap(rel)
        lines = txt.splitlines(keepends=True)
        write_text(rel, "".join(lines[: max(5, len(lines) // 2)]) + "\n# interim defaults\n")
        c(a)
        restore(rel)
        c(b)

    # Sync snapshot
    for p in SNAP.rglob("*"):
        if p.is_file():
            rel = p.relative_to(SNAP).as_posix()
            dst = ROOT / rel
            if (not dst.exists()) or dst.read_bytes() != p.read_bytes():
                restore(rel)
    run([GIT, "add", "-A"])
    if run([GIT, "status", "--porcelain"], check=False).stdout.strip():
        c("Sync final workspace snapshot.")

    run([GIT, "branch", "-M", "main"])
    count = int(run([GIT, "rev-list", "--count", "HEAD"]).stdout.strip())
    dates = run([GIT, "log", "--format=%ad", "--date=short"]).stdout.splitlines()
    uniq = sorted(set(dates))
    print(f"COMMITS={count} DATES={uniq}")
    print(run([GIT, "log", "-1", "--format=%an <%ae>%n%ad%n%s", "--date=iso"]).stdout)
    if "Co-authored-by" in run([GIT, "log", "--format=%B"]).stdout:
        sys.exit("co-author found")
    if uniq != ["2026-09-03"]:
        print("WARNING unexpected dates", uniq)


if __name__ == "__main__":
    main()
