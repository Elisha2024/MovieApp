from rest_framework import serializers
from .models import MovieRating

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieRating
        fields = '__all__'


class MovieRecommendationSerializer(serializers.Serializer):
    # title = serializers.CharField(max_length=255)
    genres = serializers.ListField(child=serializers.CharField(max_length=100))
    release_year = serializers.IntegerField()
    language = serializers.CharField(max_length=50)
