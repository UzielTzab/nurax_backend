from rest_framework import serializers

class BarcodeLookupRequestSerializer(serializers.Serializer):
    barcode = serializers.CharField(max_length=64)
    store_id = serializers.UUIDField(required=False, allow_null=True)
