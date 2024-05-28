# serializers.py
from rest_framework import serializers

class QueryDataSerializer(serializers.Serializer):
    country = serializers.CharField(max_length=100)
    year_founded = serializers.IntegerField()
    state = serializers.CharField(max_length=100)
    industry = serializers.CharField(max_length=200)
    employee_from = serializers.IntegerField()
    employee_to = serializers.IntegerField()
    city=serializers.CharField(max_length=100)
