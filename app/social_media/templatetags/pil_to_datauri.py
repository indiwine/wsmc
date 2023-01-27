import base64
from io import BytesIO

from PIL import Image
from django import template

register = template.Library()


@register.filter
def pil_to_datauri(value: str):
    img = Image.open(value).convert('RGB')
    im_file = BytesIO()
    img.save(im_file, format="JPEG")
    img.close()
    im_b64 = base64.b64encode(im_file.getvalue()).decode("utf-8")
    return f'data:image/jpeg;base64,{im_b64}'
