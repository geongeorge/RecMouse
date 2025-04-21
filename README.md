# RecMouse

<img src="/mouse-icon.png" width="200" />

A macOS application that records and replays mouse movements and clicks.

## Features

- Record mouse movements and clicks
- Play back recordings
- Repeat playback multiple times
- Status bar app for easy access
- Native macOS look and feel

## Build Requirements

- macOS
- Python 3.x
- uv (modern Python package installer)

## Build Instructions

1. **Install uv** (if not already installed)

```bash
# Using pip
pip install uv

# Or using Homebrew
brew install uv
```

2. **Create and activate a virtual environment**

```bash
# Create a new virtual environment
uv venv

# Activate the virtual environment
source .venv/bin/activate
```

3. **Install dependencies**

```bash
# Install development dependencies
uv pip install py2app
uv pip install -r requirements.txt
```

4. **Generate Icons**

```bash
# The icons will be generated automatically during build, but you can also generate them manually:
python make_icns.py
```

5. **Build the App**

```bash
# Clean previous builds and create new app
rm -rf build dist && python setup.py py2app
```

The built application will be available at `dist/RecMouse.app`.

## Installation

After building, you can:

1. Copy `RecMouse.app` to your Applications folder
2. Or run it directly from the `dist` directory

## First Run

When running RecMouse for the first time:

1. macOS may ask for permission to:
   - Monitor input (for recording)
   - Control the computer (for playback)
2. Grant these permissions in System Preferences > Security & Privacy > Privacy

## Usage

- Click the mouse icon in the status bar to access the menu
- Choose "Start Recording" to begin recording mouse movements
- Use "Play Recording" to replay the last recording
- Use "Repeat Play..." to replay multiple times

## Development

The app uses:

- `rumps` for the status bar interface
- `pynput` for mouse control
- `py2app` for building the macOS app

Recordings are stored in:

```
~/Library/Application Support/RecMouse/recording.json
```

## Icons

- `mouse-icon.png` - Used for the application icon
- `mouse-status-icon.png` - Used for the status bar icon
- `RecMouse.icns` - Generated automatically from mouse-icon.png

## Troubleshooting

If the build fails:

1. Make sure you're in the virtual environment
2. Try removing and recreating the virtual environment:

```bash
rm -rf .venv
uv venv
source .venv/bin/activate
uv pip install py2app
uv pip install -r requirements.txt
```

3. Clean the build directories:

```bash
rm -rf build dist
```
