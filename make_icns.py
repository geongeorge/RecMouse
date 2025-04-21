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

    # Create a simple mouse icon
    size = 1024
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    
    # Draw a simple mouse shape (you might want to replace this with your own icon)
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    
    # Mouse body (rounded rectangle)
    draw.rounded_rectangle([size//4, size//4, 3*size//4, 3*size//4], 
                         radius=size//8, fill='#666666')
    
    # Mouse buttons
    button_width = size//4
    draw.line([size//2, size//4, size//2, size//2], 
              fill='#444444', width=5)
    
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