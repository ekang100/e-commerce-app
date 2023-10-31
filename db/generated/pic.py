import pkg_resources
from PIL import Image, ImageDraw, ImageFont
import os

def generate_product_image(product_id, product_name): # NOT SURE WHAT INPUT SHOUDLD BE
    # Set up image dimensions and font
    width, height = 500, 500
    font_size = 50
    font = ImageFont.truetype("arial.ttf", font_size)

    # Create image and draw object
    image = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    # Draw product name in center of image
    text_width, text_height = draw.textsize(product_name, font=font)
    x = (width - text_width) / 2
    y = (height - text_height) / 2
    draw.text((x, y), product_name, fill=(0, 0, 0), font=font)

    # Save image with product id as filename
    # filename = f"{product_id}.jpg"
    # filepath = os.path.join("/app/static", filename)
    # image.save(filepath)

    return image
