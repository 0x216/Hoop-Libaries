from django.db import models

from hoop.hula import Hula


class AddressMixin(models.Model):
    building_unit = models.CharField(max_length=100, blank=True, null=True)
    building_name = models.CharField(max_length=100, blank=True, null=True)
    street_number = models.CharField(max_length=10, blank=True, null=True)
    street_name = models.CharField(max_length=100)
    neighbourhood = models.CharField(max_length=100, blank=True, null=True)
    administrative_area = models.CharField(max_length=100, blank=True, null=True)
    town = models.CharField(max_length=100, blank=True, null=True)
    county = models.CharField(max_length=100, blank=True, null=True)
    postcode = models.CharField(max_length=10)
    country = models.CharField(max_length=100)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    class Meta:
        abstract = True

    def update(self, data):
        super(AddressMixin, self).update(data)

        try:
            neighbourhood = Hula().execute(
                'geo',
                'neighbourhoods.find_nearest', {
                    'latitude': data['latitude'],
                    'longitude': data['longitude'],
                },
                version='v1'
            )[0]

            self.neighbourhood = neighbourhood['name']

        except IndexError:
            self.neighbourhood = None

        self.save()

    def serialize(self):
        return {
            'buildingUnit': self.building_unit,
            'buildingName': self.building_name,
            'streetNumber': self.street_number,
            'streetName': self.street_name,
            'town': self.town,
            'county': self.county,
            'postcode': self.postcode,
            'country': self.country,
            'latitude': self.latitude,
            'longitude': self.longitude,
        }
