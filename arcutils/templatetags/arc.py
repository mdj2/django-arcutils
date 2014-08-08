from django import template
from django.template.defaulttags import url
from django.core.urlresolvers import reverse
from django.conf import settings
from django.template import Node, Variable, VariableDoesNotExist
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def model_name(cls):
    """Given a model class, this returns its verbose name"""
    return cls._meta.verbose_name.title()


@register.tag
def full_url(parser, token):
    """Spits out the full URL"""
    url_node = url(parser, token)
    f = url_node.render
    url_node.render = lambda context: _get_host_from_context(context) + f(context)
    return url_node


def _get_host_from_context(context):
    """
    Returns the hostname from context or the settings.HOSTNAME or
    settings.HOST_NAME variables
    """
    try:
        request = Variable('request.HTTP_HOST').resolve(context)
    except VariableDoesNotExist:
        request = ""
    return request or getattr(settings, "HOSTNAME", "") or getattr(settings, "HOST_NAME", "")


class AddGetParameter(Node):
    def __init__(self, values):
        self.values = values

    def render(self, context):
        req = Variable('request').resolve(context)
        params = req.GET.copy()
        for key, value in self.values.items():
            params[key] = value.resolve(context)
        return '?%s' %  params.urlencode()


@register.tag
def add_get(parser, token):
    """
    The tag generates a parameter string in form '?param1=val1&param2=val2'.
    The parameter list is generated by taking all parameters from current
    request.GET and optionally overriding them by providing parameters to the tag.

    This is a cleaned up version of http://djangosnippets.org/snippets/2105/. It
    solves a couple of issues, namely:
     * parameters are optional
     * parameters can have values from request, e.g. request.GET.foo
     * native parsing methods are used for better compatibility and readability
     * shorter tag name

    Usage: place this code in your appdir/templatetags/add_get_parameter.py
    In template:
    {% load add_get_parameter %}
    <a href="{% add_get param1='const' param2=variable_in_context %}">
    Link with modified params
    </a>

    It's required that you have 'django.core.context_processors.request' in
    TEMPLATE_CONTEXT_PROCESSORS

    Original version's URL: http://django.mar.lt/2010/07/add-get-parameter-tag.html
    """
    pairs = token.split_contents()[1:]
    values = {}
    for pair in pairs:
        s = pair.split('=', 1)
        values[s[0]] = parser.compile_filter(s[1])
    return AddGetParameter(values)
