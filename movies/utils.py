from rest_framework.response import Response
from movies.models import Genre
from rest_framework.pagination import PageNumberPagination



def build_response(data=None, errors=None, status_code=200, message=None):
    """
    Utility function to build a standardized response for the API.
    """
    response = {
        "status": status_code,
        "message": message or "Success",
        "data": data or {},
        "errors": errors or {},
    }
    return Response(response, status=status_code)


def map_genres_to_ids(genre_names):
    genres = Genre.objects.filter(name__in=genre_names).values_list('tmdb_id', flat=True)
    if not genres:
        raise ValueError("Invalid genres provided.")
    return list(genres)


class CustomPagination(PageNumberPagination):
    page_size = 5  # Number of items per page
    page_size_query_param = 'page_size'
    max_page_size = 100