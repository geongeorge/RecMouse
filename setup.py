from setuptools import setup

APP = ['app.py']
DATA_FILES = [
    ('', ['RecMouse.icns']),
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