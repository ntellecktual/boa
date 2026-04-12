import os
import re

from django import template

register = template.Library()


@register.filter
def camelcase_filename(value):
    """
    Converts strings like 'rdd_transformations_and_actions' to 'RddTransformationsAndActions'
    """
    if not isinstance(value, str):
        return value
    parts = value.replace('.mp3', '').split('_')
    return ''.join(part.capitalize() for part in parts if part)


@register.filter
def camelcase_file(value):
    """
    Converts '02-linear_regression_project.ipynb' → 'Linear Regression Project'
    """
    if not isinstance(value, str):
        return value

    name = os.path.splitext(os.path.basename(value))[0]  # Remove extension
    name = name.lstrip('0123456789-_')  # Remove leading numbers/dashes
    parts = name.replace('-', '_').split('_')
    camel = ''.join(part.capitalize() for part in parts if part)
    spaced = re.sub(r'(?<!^)(?=[A-Z])', ' ', camel)  # Add spaces
    return spaced


@register.filter
def basename(value):
    """
    Extracts just the filename from a full path like 'C:\\path\\to\\media\\audio\\file.mp3'
    Returns: 'file.mp3'
    """
    return os.path.basename(value).replace('\\', '/')


@register.filter
def relative_media_path(value):
    """
    Cleans full file path to be relative to MEDIA_ROOT.
    For example: 'boa/media/audio/file.mp3' -> 'audio/file.mp3'
    """
    parts = value.replace('\\', '/').split('media/')
    return parts[-1] if len(parts) > 1 else value
