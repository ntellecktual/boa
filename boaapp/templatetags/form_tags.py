from django import template

register = template.Library()


@register.filter(name='add_class')
def add_class(field, css_class):
    """
    Adds a CSS class to a Django form field widget.
    Usage: {{ form.field|add_class:"your-class" }}
    """
    existing_classes = field.field.widget.attrs.get('class', '')
    return field.as_widget(attrs={'class': f'{existing_classes} {css_class}'.strip()})


# You can add other custom filters or tags here if needed
