#!/usr/bin/env python3
"""
Generate test images for asset pipeline testing
"""

import os
from PIL import Image, ImageDraw, ImageFont

def create_test_image(filename, size=(800, 600), color='blue', text='Test Image'):
    """Create a simple test image"""
    img = Image.new('RGB', size, color=color)
    draw = ImageDraw.Draw(img)

    # Add text in the center
    try:
        # Try to use a better font
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
    except:
        # Fallback to default font
        font = ImageFont.load_default()

    # Calculate text position (centered)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2

    draw.text((x, y), text, fill='white', font=font)

    # Save image
    img.save(filename)
    print(f"✅ Created: {filename} ({size[0]}x{size[1]}, {color})")

def main():
    """Generate test images"""
    fixtures_dir = os.path.dirname(__file__)
    images_dir = os.path.join(fixtures_dir, 'images')

    os.makedirs(images_dir, exist_ok=True)

    print("🎨 Generating test images...")

    # Create various test images
    create_test_image(
        os.path.join(images_dir, 'test-photo-1.jpg'),
        size=(800, 600),
        color='#4A90E2',
        text='Timeline Photo 1'
    )

    create_test_image(
        os.path.join(images_dir, 'test-photo-2.jpg'),
        size=(1024, 768),
        color='#E24A90',
        text='Timeline Photo 2'
    )

    create_test_image(
        os.path.join(images_dir, 'test-photo-3.jpg'),
        size=(640, 480),
        color='#90E24A',
        text='Timeline Photo 3'
    )

    # Create a large image to test size handling
    create_test_image(
        os.path.join(images_dir, 'test-photo-large.jpg'),
        size=(2048, 1536),
        color='#E2904A',
        text='Large Photo'
    )

    # Create a small thumbnail
    create_test_image(
        os.path.join(images_dir, 'test-thumbnail.jpg'),
        size=(150, 150),
        color='#4AE290',
        text='Thumb'
    )

    print("✅ All test images generated successfully!")

if __name__ == '__main__':
    main()
