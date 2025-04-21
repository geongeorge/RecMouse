from setuptools import setup
import subprocess
import sys
import os

# Run make_icns.py to generate fresh icons
print("Generating icons...")
try:
    subprocess.run([sys.executable, 'make_icns.py'], check=True)
except subprocess.CalledProcessError as e:
    print(f"Warning: Failed to generate icons: {e}")
except FileNotFoundError:
    print("Warning: make_icns.py not found, skipping icon generation")

APP = ['app.py']
DATA_FILES = [
    ('', ['RecMouse.icns']),
    ('', ['mouse-icon.png']),
    ('', ['mouse-status-icon.png']),
]
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'RecMouse.icns',
    'plist': {
        'LSUIElement': True,
        'CFBundleName': 'RecMouse',
        'CFBundleDisplayName': 'RecMouse',
        'CFBundleIdentifier': 'com.recmouse.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'NSAppleEventsUsageDescription': 'RecMouse needs to control the mouse for playback.',
        'NSInputMonitoringUsageDescription': 'RecMouse needs to monitor mouse input for recording.',
    },
    'packages': [
        'rumps',
        'pynput',
        'colorama',
        'PIL',
        'pkg_resources',
        'configparser',
        'plistlib',
        'pathlib',
    ],
}

setup(
    name='RecMouse',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=[
        'pynput>=1.7.6',
        'colorama>=0.4.6',
        'rumps>=0.4.0',
        'pyobjc-framework-Cocoa>=9.0',
        'Pillow>=10.0.0',
    ],
)