#!/usr/bin/env python3
"""
Simple streaming example for BrainLink devices.

Requirements:
- Place `BrainLinkParser.so` (macOS) or `BrainLinkParser.pyd` (Windows) where Python can import it.
- Install `pyserial`: `pip install pyserial`.
Usage:
    python examples/brainlink_live.py --port /dev/cu.BrainLink_Pro
"""

import argparse
import sys
import time
from typing import Optional


try:
    from BrainLinkParser import BrainLinkParser
except Exception as exc:
    sys.exit(
        "Unable to import BrainLinkParser. "
        "Ensure BrainLinkParser.so/.pyd is on your PYTHONPATH or in the working directory. "
        f"Original error: {exc}"
    )

try:
    import serial  # type: ignore
except Exception as exc:
    sys.exit(
        "Missing dependency pyserial. Install with `pip install pyserial`.\n"
        f"Original error: {exc}"
    )


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)

    def on_raw(raw: int) -> None:
        if args.verbose:
            print(f"raw = {raw}")

    def on_eeg(data) -> None:
        print(
            "EEG:"
            f" attention={data.attention}"
            f" meditation={data.meditation}"
            f" delta={data.delta}"
            f" theta={data.theta}"
            f" lowAlpha={data.lowAlpha}"
            f" highAlpha={data.highAlpha}"
            f" lowBeta={data.lowBeta}"
            f" highBeta={data.highBeta}"
            f" lowGamma={data.lowGamma}"
            f" highGamma={data.highGamma}"
        )

    def on_extend_eeg(data) -> None:
        print(
            "Extended:"
            f" ap={data.ap}"
            f" battery={data.battery}"
            f" version={data.version}"
            f" gnaw={data.gnaw}"
            f" temperature={data.temperature}"
            f" heart={data.heart}"
        )

    def on_gyro(x: int, y: int, z: int) -> None:
        print(f"Gyro: x={x} y={y} z={z}")

    def on_rr(rr1: int, rr2: int, rr3: int) -> None:
        print(f"RR: rr1={rr1} rr2={rr2} rr3={rr3}")

    parser = BrainLinkParser(
        eeg_callback=on_eeg,
        extend_eeg_callback=on_extend_eeg,
        gyro_callback=on_gyro,
        rr_callback=on_rr,
        raw_callback=on_raw if args.verbose else None,
    )

    try:
        with serial.Serial(args.port, args.baud, timeout=1) as ser:
            print(f"Connected to {args.port} @ {args.baud}. Press Ctrl+C to stop.")
            while True:
                chunk = ser.read(ser.in_waiting or 1)
                if chunk:
                    parser.parse(chunk)
                else:
                    time.sleep(0.01)
    except KeyboardInterrupt:
        print("\nInterrupted, closing connection.")
    except serial.SerialException as exc:
        sys.exit(f"Serial error: {exc}")

    return 0


def parse_args(argv: Optional[list[str]]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Stream BrainLink data and print parsed values."
    )
    parser.add_argument(
        "--port",
        required=True,
        help="Serial port of the BrainLink dongle (e.g. /dev/cu.BrainLink_Pro or COM5).",
    )
    parser.add_argument(
        "--baud",
        type=int,
        default=115200,
        help="Baud rate reported by the device (default: 115200).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print raw data values in addition to parsed metrics.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())


# from cushy_serial import CushySerial
# from BrainLinkParser import BrainLinkParser

# def onRaw(raw):
#     print("raw = " + str(raw))
#     return

# def onEEG(data):
#     print("attention = " + str(data.attention) +
#           " meditation = " + str(data.meditation) +
#           " delta = " + str(data.delta) +
#           " theta = " + str(data.theta) +
#           " lowAlpha = " + str(data.lowAlpha) +
#           " highAlpha = " + str(data.highAlpha) +
#           " lowBeta = " + str(data.lowBeta) +
#           " highBeta = " + str(data.highBeta) +
#           " lowGamma = " + str(data.lowGamma) +
#           " highGamma = " + str(data.highGamma))
#     return

# def onExtendEEG(data):
#     print("ap = " + str(data.ap) +
#           " battery = " + str(data.battery) +
#           " version = " + str(data.version) +
#           " gnaw = " + str(data.gnaw) +
#           " temperature = " + str(data.temperature) +
#           " heart = " + str(data.heart))
#     return

# def onGyro(x, y, z):
#     print("x = " + str(x) + " y = " + str(y) + " z = " + str(z))
#     return

# def onRR(rr1, rr2, rr3):
#     print("rr1 = " + str(rr1) + " rr2 = " + str(rr2) + " rr3 = " + str(rr3))
#     return

# parser = BrainLinkParser(onEEG, onExtendEEG, onGyro, onRR, onRaw)

# serial = CushySerial('/dev/cu.BrainLink_Lite', 115200)
# # serial = CushySerial('/dev/cu.BrainLink_Lite', 115200)

# @serial.on_message()
# def handle_serial_message(msg: bytes):
#     print(f"[serial] rec raw: {msg}")
#     parser.parse(msg)