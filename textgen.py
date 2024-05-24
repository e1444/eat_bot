from PIL import Image, ImageDraw, ImageFont
import textwrap

def centered_text_image(text: str, output_path: str, *, font_path: str = 'assets/Arial.ttf', font_size=20, max_width=20, bg_color: str = "white", text_color: str = "black"):
    # Load font
    font = ImageFont.truetype(font_path, font_size)

    # Wrap the text
    wrapped_text_lines = textwrap.wrap(text, width=max_width)

    # Calculate total height of the wrapped text
    total_height = font.size * len(wrapped_text_lines)

    # Create a blank image with a white background
    image = Image.new("RGB", (200, 200), bg_color)

    # Initialize the drawing context
    draw = ImageDraw.Draw(image)

    # Draw the wrapped text onto the image
    y = (200 - total_height) // 2 - 20
    for line in wrapped_text_lines:
        # Get the width and height of the current line of text
        text_width = draw.textlength(line, font=font)
        
        # Calculate the position to center the text horizontally
        x = (image.width - text_width) / 2
        
        # Draw the text onto the image>
        draw.text((x, y), line, font=font, fill=text_color)
        
        # Move to the next line
        y += font.size

    # Save or display the image
    image.save(output_path)