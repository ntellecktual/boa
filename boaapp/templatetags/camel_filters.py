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
    Converts file names like '02-linear_regression_project.ipynb'
    to 'LinearRegressionProject'
    """
    import os
    if not isinstance(value, str):
        return value

    name = os.path.splitext(os.path.basename(value))[0]  # strip folder and extension
    name = name.lstrip("0123456789-_")  # remove leading digits or hyphens
    parts = name.replace('-', '_').split('_')
    return ''.join(part.capitalize() for part in parts if part)
