# brainlink

## Quick start example

- Ensure the vendor parser binary is available to Python: place `BrainLinkParser.so` (macOS) or `BrainLinkParser.pyd` (Windows) in the working directory or on `PYTHONPATH`.
- Install dependencies: `pip install pyserial`
- Run the live streaming example (adjust the port for your device):

```bash
python brainlink_live.py --port /dev/cu.BrainLink_Lite
```
