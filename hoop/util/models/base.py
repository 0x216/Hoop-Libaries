from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import models
from django.utils import timezone
from uuid import uuid4

from hoop.util.dates import decode_datetime, decode_date, decode_time, encode_datetime
from hoop.util.text import camelcase
from hoop.util.fields import HoopURLField


class Model(models.Model):
    '''
    Abstract model that is deserialisable from a JSON representation
    '''

    class Meta:
        abstract = True

    def update(self, data, save=True):
        for field in self._meta.get_fields():
            if camelcase(field.name) in data:
                value = data[camelcase(field.name)]

                if value is None:
                    if not isinstance(field, models.ManyToOneRel) and not isinstance(
                        field, models.ManyToManyRel
                    ) and not isinstance(field, models.ManyToManyField):
                        setattr(self, field.name, None)

                else:
                    for field_class in [
                        models.BooleanField, models.CharField, models.DecimalField, models.FloatField,
                        models.NullBooleanField, models.PositiveSmallIntegerField, models.PositiveIntegerField,
                        models.TextField, models.URLField, HoopURLField, models.UUIDField
                    ]:
                        if isinstance(field, field_class):
                            setattr(self, field.name, value)

                    if isinstance(field, models.DateTimeField):
                        try:
                            setattr(self, field.name, decode_datetime(value))
                        except ValueError as e:
                            if not value and field.null:
                                setattr(self, field.name, None)
                            else:
                                raise e

                    elif isinstance(field, models.DateField):
                        try:
                            setattr(self, field.name, decode_date(value))
                        except ValueError as e:
                            if not value and field.null:
                                setattr(self, field.name, None)
                            else:
                                raise e

                    elif isinstance(field, models.TimeField):
                        setattr(self, field.name, decode_time(value))

                    elif isinstance(field, models.OneToOneField):
                        model = getattr(self, field.name, None) or field.rel.to()

                        model.update(value)

                        setattr(self, field.name, model)

        if save:
            self.full_clean()
            self.save()

        return self

    @classmethod
    def create(cls, data):
        model = cls()

        model.update(data)

        return model

    @classmethod
    def get_paginated_items(cls, data):
        if not data:
            data = {}
        page = data.get('page')
        limit = int(data.get('limit', '10') or 10)

        items_qs = cls.objects.all().select_related().distinct()

        if 'fields' in data:
            items_qs = items_qs.values(*data['fields'])
        if 'filters' in data:
            items_qs = items_qs.filter(**data['filters'])
        if 'orderBy' in data:
            items_qs = items_qs.order_by(data['orderBy'])
        if 'searchField' in data:
            items_qs = items_qs.filter(**{'%s__icontains' % data['searchField']: data['searchQuery']})

        paginator = Paginator(items_qs, limit)

        try:
            items = paginator.page(page)
        except (PageNotAnInteger, EmptyPage):
            items = paginator.page(1)

        return {
            'items': items.object_list,
            'count': items_qs.count(),
            'total': cls.objects.count(),
            'page': items.number,
            'num_pages': items.paginator.num_pages,
            'has_next': items.has_next(),
            'has_previous': items.has_previous(),
        }


class UUIDModel(Model):
    '''
    Abstract model that uses a UUID primary
    key instead of an integer field.
    '''
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True


class VersionedModel(UUIDModel):
    '''
    Tracks creation and update times of model changes.
    User ID is required when saving.
    '''
    created_at = models.DateTimeField(blank=True, null=True)
    created_by = models.UUIDField(blank=True, null=True)

    updated_at = models.DateTimeField(blank=True, null=True)
    updated_by = models.UUIDField(blank=True, null=True)

    class Meta:
        abstract = True

    def update(self, data, save=True):
        now = timezone.now()

        for field in ['createdAt', 'createdBy', 'updatedAt', 'updatedBy']:
            try:
                del data[field]
            except KeyError:
                pass

        if not self.created_at:
            self.created_at = now
            if 'adminID' in data:
                self.created_by = data['adminID']

        self.updated_at = now
        if 'adminID' in data:
            self.updated_by = data['adminID']

        super(VersionedModel, self).update(data, save)

        return self

    def serialize_version(self):
        return {
            'createdAt': encode_datetime(self.created_at),
            'createdBy': self.created_by,
            'updatedAt': encode_datetime(self.updated_at),
            'updatedBy': self.updated_by,
        }
