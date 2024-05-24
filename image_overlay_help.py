from PIL import Image
import io

from image_help import download_image

def pirate_overlay(avatar_url: str) -> bytes:
    avt_bytes = download_image(avatar_url)
    bytes_io = io.BytesIO(avt_bytes)

    avt = Image.open(bytes_io)
    pirate_hat = Image.open('assets/pirate_hat.png')

    width_ratio = avt.width / pirate_hat.width
    new_height = int(pirate_hat.height * width_ratio)
    pirate_hat = pirate_hat.resize((avt.width, new_height))

    avt.paste(pirate_hat, (0, 0), pirate_hat)
    
    imgByteArr = io.BytesIO()

    output_buffer = io.BytesIO()
    avt.save(output_buffer, format=avt.format)
    output_buffer.seek(0)

    # Get the bytes of the image
    overlayed_image_bytes = output_buffer.getvalue()
    output_buffer.close()

    return overlayed_image_bytes