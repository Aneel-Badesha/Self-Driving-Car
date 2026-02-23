# Self-Driving-Car

Self-driving RC car project (work in progress) with:
- Raspberry Pi motor control
- Pi camera streaming
- PC-side object detection and visualization

## Current status

- Motor controller implemented (`control/control.py`)
- Pi camera streaming implemented (`vision/stream_pi.py` )
- PC receiver + optional detection implemented (`vision/receiver_pc.py`)
- [TODO] Planning/safety/simulation modules are placeholders (`control/planner.py`, `control/safety.py`, `sim/replay.py`)

## Repository structure

```text
control/
	control.py      # Raspberry Pi GPIO motor controller
	main.py         # Basic motor drive smoke test
	planner.py      # (empty placeholder)
	safety.py       # (empty placeholder)

vision/
	stream_pi.py    # Send camera frames from Pi over TCP
	receiver_pc.py  # Receive frames on PC + optional object detection
	test_cam.py     # Quick camera check
	test_torch.py   # Quick torch/cuda check

sim/
	replay.py       # (empty placeholder)
	test_frames.py/ # directory placeholder
```

## Requirements

Install Python dependencies:

```bash
pip install -r requirements.txt
```

`requirements.txt` currently includes:
- `torch`
- `torchvision`
- `opencv-python`
- `numpy`

## Quick start

### 1) Camera and PyTorch checks

```bash
python3 vision/test_cam.py
python3 vision/test_torch.py
```

### 2) Stream camera from Raspberry Pi

On the Raspberry Pi:

```bash
python3 vision/stream_pi.py
```

This starts a TCP server on `0.0.0.0:9999` and waits for a client.

### 3) Receive stream on PC

On your PC:

```bash
python3 vision/receiver_pc.py
```

By default, detection is enabled with `fasterrcnn_resnet50_fpn`.

Optional performance flags:

```bash
python3 vision/receiver_pc.py --no-detect
python3 vision/receiver_pc.py --scale 0.5 --skip-frames 2
```

## Networking note

`vision/receiver_pc.py` currently has the Pi IP hardcoded:

```python
pi_ip = '192.168.1.90'
```

Update this value to match your Raspberry Pi LAN IP before connecting.

## Motor control smoke test (Pi only)

```bash
python3 control/main.py
```

What it does:
- Initializes GPIO motor pins
- Drives all wheels forward at 25% duty cycle for 10 seconds
- Stops motors and cleans up GPIO

> Requires Raspberry Pi hardware and `RPi.GPIO` support.

## Planned control packet format

Control packet bytes (planned/legacy note):
- Byte 0: left speed (`0-255`)
- Byte 1: right speed (`0-255`)
- Byte 2: direction bits

## Safety

Use low speed and keep wheels off the ground during initial testing.
