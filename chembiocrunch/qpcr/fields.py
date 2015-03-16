import json
from rest_framework import serializers
 
class JSONField(serializers.Field):
    
    def to_representation(self, obj):
        return json.dumps(obj)
    
    def to_internal_value(self, value):
        try:
            val = json.loads(value)
        except TypeError:
            raise serializers.ValidationError(
                "Could not load json <{}>".format(value)
            )
        return val