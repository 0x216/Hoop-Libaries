from django.core.exceptions import ValidationError
from django.db.models.fields import CharField
from django import forms
from django.utils.translation import ugettext_lazy as _


def validate_url(value):
    if not (value.startswith('http://') or value.startswith('https://')):
        raise ValidationError(
            _('%(value)s does not start with http:// or https://'),
            params={'value': value},
        )


class HoopURLField(CharField):
    default_validators = [validate_url]
    description = _("URL")

    def __init__(self, verbose_name=None, name=None, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 500)
        super(HoopURLField, self).__init__(verbose_name, name, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(HoopURLField, self).deconstruct()
        if kwargs.get("max_length") == 500:
            del kwargs['max_length']
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        # As with CharField, this will cause URL validation to be performed
        # twice.
        defaults = {
            'form_class': forms.URLField,
        }
        defaults.update(kwargs)

        return super(HoopURLField, self).formfield(**defaults)
