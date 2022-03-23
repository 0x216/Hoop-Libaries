from django.db import models

from hoop.util.fields import HoopURLField


class ContactMixin(models.Model):
    email = models.EmailField(blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    facebook_url = models.CharField(max_length=200, blank=True, null=True)
    twitter_url = models.CharField(max_length=100, blank=True, null=True)
    instagram_url = models.CharField(max_length=100, blank=True, null=True)
    website_url = HoopURLField(max_length=500, blank=True, null=True)

    booking_email = models.BooleanField(default=False)
    booking_telephone = models.BooleanField(default=False)
    booking_website = models.BooleanField(default=False)

    website_hide = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def serialize(self):
        return {
            'email': self.email,
            'telephone': self.telephone,
            'facebookURL': self.facebook_url,
            'websiteURL': self.website_url,
            'twitterURL': self.twitter_url,
            'twitterUsername': self.twitter_url, # TODO: remove when all updated to twitterURL
            'instagramURL': self.instagram_url,
            'bookingEmail': self.booking_email,
            'bookingTelephone': self.booking_telephone,
            'bookingWebsite': self.booking_website,
            'websiteHide': self.website_hide,
        }
