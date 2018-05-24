from rest_framework import serializers
from src.competition.models import CompetitionUser

class CompetitionUserSerializer(serializers.ModelSerializer):
    total_points = serializers.SerializerMethodField()

    class Meta:
        model = CompetitionUser
        fields = ('total_points', )

    def get_total_points(self, obj):
        return obj.total_points
