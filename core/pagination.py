from rest_framework.pagination import PageNumberPagination

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10  # Number of blogs per page
    page_size_query_param = 'limit'  # Optional: Allow dynamic page sizes
    max_page_size = 100
    page_query_param = 'page'  # Ensure it accepts 'page' parameter
