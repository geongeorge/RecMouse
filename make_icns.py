"""
Script to generate an icns file from a PNG image for macOS apps.
Requires PIL (Python Imaging Library).
"""
import os
import subprocess
from PIL import Image

def create_icns():
    # Create iconset directory
    iconset_name = "RecMouse.iconset"
    if not os.path.exists(iconset_name):
        os.makedirs(iconset_name)

    # Load the mouse icon
    source_icon = "mouse-icon.png"
    if not os.path.exists(source_icon):
        raise FileNotFoundError(f"Source icon {source_icon} not found!")
        
    img = Image.open(source_icon)
    
    # Convert to RGBA if not already
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Resize to 1024x1024 as the master size
    size = 1024
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    
    # Save sizes required for macOS
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    
    for s in sizes:
        img_scaled = img.resize((s, s), Image.Resampling.LANCZOS)
        img_scaled.save(f"{iconset_name}/icon_{s}x{s}.png")
        if s <= 512:  # macOS also needs @2x versions
            img_scaled = img.resize((s*2, s*2), Image.Resampling.LANCZOS)
            img_scaled.save(f"{iconset_name}/icon_{s}x{s}@2x.png")

    # Convert to icns using iconutil
    subprocess.run(['iconutil', '-c', 'icns', iconset_name])
    
    # Clean up the iconset directory
    import shutil
    shutil.rmtree(iconset_name)

if __name__ == "__main__":
    create_icns() 