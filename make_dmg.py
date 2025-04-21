#!/usr/bin/env python3

import os
import sys
import plistlib
from pathlib import Path

def get_version():
    # Try to get version from Info.plist if it exists
    app_path = Path("dist/RecMouse.app")
    plist_path = app_path / "Contents/Info.plist"
    
    if plist_path.exists():
        with open(plist_path, 'rb') as f:
            plist = plistlib.load(f)
            return plist.get('CFBundleShortVersionString', '1.0.0')
    return '1.0.0'

# Configuration for dmgbuild
settings = {
    'filename': f'RecMouse-{get_version()}.dmg',
    'volume_name': 'RecMouse',
    'format': 'UDBZ',
    'size': '100M',
    'files': ['dist/RecMouse.app'],
    'symlinks': {'Applications': '/Applications'},
    'icon_locations': {
        'RecMouse.app': (140, 120),
        'Applications': (400, 120)
    },
    'window_rect': ((100, 100), (540, 300)),
    'icon_size': 64,
    'background': 'buildassets/dmg_background.png',
    'show_status_bar': False,
    'show_tab_view': False,
    'show_toolbar': False,
    'show_pathbar': False,
    'show_sidebar': False,
}

if __name__ == '__main__':
    # First check if the app exists
    if not os.path.exists('dist/RecMouse.app'):
        print("Error: RecMouse.app not found in dist directory.")
        print("Please build the app first using: python setup.py py2app")
        sys.exit(1)

    # Create buildassets directory if it doesn't exist
    os.makedirs('buildassets', exist_ok=True)

    # Create a simple background image if it doesn't exist
    if not os.path.exists('buildassets/dmg_background.png'):
        try:
            from PIL import Image, ImageDraw
            
            # Create a white background image
            img = Image.new('RGB', (540, 300), 'white')
            draw = ImageDraw.Draw(img)
            
            # Optional: Add a simple text or design
            # draw.text((270, 150), "RecMouse", fill='black', anchor='mm')
            
            img.save('buildassets/dmg_background.png')
        except ImportError:
            print("Warning: Pillow not installed. Skipping background image creation.")
            settings['background'] = None

    # Build the DMG
    import dmgbuild
    dmgbuild.build_dmg('dist/RecMouse.dmg', 'RecMouse', settings=settings)
    print(f"DMG created successfully: dist/RecMouse.dmg") 