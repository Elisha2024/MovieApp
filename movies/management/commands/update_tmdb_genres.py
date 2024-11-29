import requests
from django.core.management.base import BaseCommand
from movies.models import Genre
from decouple import config

TMDB_API_URL = "https://api.themoviedb.org/3"
TMDB_API_KEY = config("TMDB_API_KEY")

class Command(BaseCommand):
    help = "Update TMDb genre mapping"

    def handle(self, *args, **kwargs):
        url = f"{TMDB_API_URL}/genre/movie/list"
        params = {'api_key': TMDB_API_KEY, 'language': 'en'}
        response = requests.get(url, params=params, verify=False)
        response.raise_for_status()
        data = response.json()

        for genre in data.get('genres', []):
            Genre.objects.update_or_create(
                tmdb_id=genre['id'],
                defaults={'name': genre['name']}
            )
        self.stdout.write(self.style.SUCCESS('Successfully updated genre mapping.'))
