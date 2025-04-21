# PyAutoMouse

A Python project for automated mouse control and clicking at specific screen coordinates.

## Setup

1. Install uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Create a virtual environment and install dependencies:

```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
# or
.\.venv\Scripts\activate  # On Windows

uv pip install -r requirements.txt
```

## Usage

Run the main script:

```bash
python main.py
```

The script provides functionality to:

- Move the mouse to specific coordinates
- Perform clicks at specified locations
- Get current mouse position
- Add safety features like failsafe (move mouse to corner to stop)

## Safety Features

- Press Ctrl+C to stop the script
- Move mouse to any corner of the screen to trigger failsafe
