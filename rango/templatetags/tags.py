from django import template
from django.template.defaultfilters import stringfilter
register = template.Library()

@register.filter
@stringfilter
def replacespaces(value):
	return value.replace(' ', '_')




