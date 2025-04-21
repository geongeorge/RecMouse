# Building RecMouse macOS App

This document explains how to build the RecMouse application into a native macOS app.

## Prerequisites

- Python 3.12 or higher
- uv package manager
- macOS operating system

## Build Steps

1. Install dependencies using uv:

   ```bash
   uv pip install -e .
   ```

2. Install py2app:

   ```bash
   uv pip install py2app
   ```

3. Build the application:
   ```bash
   python setup.py py2app
   ```

The built application will be available in the `dist` directory as `RecMouse.app`.

## Development Build

For testing, you can create a development build that links to your Python installation:

```bash
python setup.py py2app -A
```

This creates a development version that's faster to rebuild during testing.

## Notes

- The app will appear in your menu bar, not in the Dock
- First launch might require right-clicking and selecting "Open" due to macOS security
- The app requires accessibility permissions to control the mouse
