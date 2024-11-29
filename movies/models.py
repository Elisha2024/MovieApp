from django.db import models
from django.contrib.auth.models import User

class MovieRating(models.Model):
    movie_id = models.IntegerField()
    rating = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)


    def __str__(self):
        return f"Movie {self.movie_id} - Rating {self.rating} by {self.user}"

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    tmdb_id = models.IntegerField(unique=True)

    def __str__(self):
        return self.name
