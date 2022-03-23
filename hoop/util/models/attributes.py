from django.core.exceptions import ValidationError
from django.db import models

from hoop.util.fields import HoopURLField

AGE_MODE_CHOICES = (
    ('M', 'Months'),
    ('Y', 'Years'),
    ('X', 'Mixed'),
)


class AttributesMixin(models.Model):
    # Age Limits - min and max are always in months
    age_mode = models.CharField(max_length=1, choices=AGE_MODE_CHOICES, blank=True)
    age_min = models.PositiveSmallIntegerField(blank=True, null=True)
    age_max = models.PositiveSmallIntegerField(blank=True, null=True)
    age_notes = models.TextField(blank=True, null=True)

    # Booking Info
    booking_notes = models.TextField(blank=True, null=True)
    booking_website = HoopURLField(max_length=500, blank=True, null=True)
    booking_email = models.EmailField(blank=True, null=True)
    booking_telephone = models.CharField(max_length=100, blank=True, null=True)

    # Disability Info
    disability_notes = models.TextField(blank=True, null=True)
    assisted_hearing = models.NullBooleanField(default=None)
    audio_described = models.NullBooleanField(default=None)
    autism_friendly = models.NullBooleanField(default=None)
    captioned = models.NullBooleanField(default=None)
    signed = models.NullBooleanField(default=None)
    subtitled = models.NullBooleanField(default=None)
    wheelchair_access = models.NullBooleanField(default=None)
    disability_link = HoopURLField(max_length=500, blank=True, null=True)

    # Additional Pricing Info (prices are held in PricePoint models)
    pricing_notes = models.TextField(blank=True, null=True)

    # Timing
    timing_notes = models.TextField(blank=True, null=True)

    featured = models.NullBooleanField(default=None)

    class Meta:
        abstract = True

    def clean(self):
        if self.age_mode == 'Y':
            if self.age_min and self.age_min % 12 != 0:
                raise ValidationError('Age mode are in years but age_min should be in months (number of years * 12)')
            if self.age_max and (self.age_max - 11) % 12 != 0:
                raise ValidationError(
                    'Age mode are in years but age_max should be in months (number of years * 12 + 11)'
                )

    def serialize_attributes(self):

        return {
            'ageMode': self.age_mode,
            'ageMin': self.age_min,
            'ageMax': self.age_max,
            'ageNotes': self.age_notes,
            'bookingNotes': self.booking_notes,
            'bookingWebsite': self.booking_website,
            'bookingEmail': self.booking_email,
            'bookingTelephone': self.booking_telephone,
            'disabilityLink': self.disability_link,
            'disabilityURL': self.disability_link,
            'pricingNotes': self.pricing_notes,
            'timingNotes': self.timing_notes,
            'featured': self.featured,
        }
