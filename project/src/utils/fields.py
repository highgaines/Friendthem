from rest_framework.serializers import Field
from django.contrib.gis.geos import GEOSGeometry

class PointField(Field):
    default_error_messages = {
        'incorrect_format': 'Point must have `lng` and `lat` keys.'
    }

    def to_representation(self, obj):
        return {'lng': obj.x, 'lat': obj.y}

    def to_internal_value(self, data):
        if not all([data.get('lng'), data.get('lat')]):
            self.fail('incorrect_format')

        return GEOSGeometry('POINT ({} {})'.format(data['lng'], data['lat']))
