from django.db.models import Q, F, Value, FloatField
from django.contrib.postgres.search import (
    SearchVector,
    SearchQuery,
    SearchRank,
    TrigramSimilarity,
)
from applications.models import Application
from django.db.models import Exists, OuterRef
from datetime import datetime, timedelta
from django.utils import timezone


def apply_job_filters(queryset, query_params, user=None):
    """
    Apply filters and search to job listings queryset.
    Returns filtered queryset with optimized search.
    """
    # Annotate with application status if user is provided
    if user and not user.is_anonymous:
        user_application = Application.objects.filter(
            job=OuterRef("pk"), candidate=user
        )
        queryset = queryset.annotate(user_has_applied=Exists(user_application))

    # Define valid filters with field mapping
    valid_filters = {
        "title": "title__icontains",
        "company": "company__icontains",
        "location": "location__icontains",
        "job_location_type": "job_location_type__icontains",
        "job_type": "job_type__icontains",
        "experience_level": "experience_level",
    }

    # Build filters
    filters = Q()
    has_filters = False

    # Apply direct field filters
    for param, db_field in valid_filters.items():
        value = query_params.get(param, None)
        if value:
            filters &= Q(**{db_field: value.strip()})
            has_filters = True

    # Apply time-based filters
    time_filter = query_params.get("time_published", None)
    if time_filter:
        now = timezone.now()
        if time_filter == "24h":
            # Jobs published in the last 24 hours
            time_threshold = now - timedelta(hours=24)
            filters &= Q(created_at__gte=time_threshold)
            has_filters = True
        elif time_filter == "7d":
            # Jobs published in the last 7 days
            time_threshold = now - timedelta(days=7)
            filters &= Q(created_at__gte=time_threshold)
            has_filters = True
        elif time_filter == "30d":
            # Jobs published in the last 30 days
            time_threshold = now - timedelta(days=30)
            filters &= Q(created_at__gte=time_threshold)
            has_filters = True

    # Enhanced search functionality
    search_query = query_params.get("search", None)
    if search_query:
        search_query = search_query.strip()

        # Apply advanced PostgreSQL search capabilities
        if len(search_query) > 2:  # Only apply for meaningful queries
            # Use both vector-based search and trigram similarity
            queryset = queryset.annotate(
                # Vector search with weights for different fields
                search_vector=SearchVector("title", weight="A")
                + SearchVector("company", weight="B")
                + SearchVector("location", weight="C"),
                # Trigram similarity for fuzzy matching on title
                title_similarity=TrigramSimilarity("title", search_query),
                # Trigram similarity for company
                company_similarity=TrigramSimilarity("company", search_query),
            )

            search_rank = SearchRank("search_vector", SearchQuery(search_query))

            # Combine both approaches with a weighted score
            queryset = (
                queryset.annotate(
                    rank=search_rank
                    + F("title_similarity") * Value(2.0, output_field=FloatField())
                    + F("company_similarity") * Value(1.0, output_field=FloatField())
                )
                .filter(rank__gt=0.1)
                .order_by("-rank")
            )

            return queryset

        # Fallback to basic search for very short queries
        search_words = search_query.lower().split()
        search_filter = Q()
        for word in search_words:
            search_filter |= (
                Q(title__icontains=word)
                | Q(company__icontains=word)
                | Q(location__icontains=word)
                | Q(job_location_type__icontains=word)
                | Q(job_type__icontains=word)
            )
        filters &= search_filter
        has_filters = True

    # Apply filters if any
    if has_filters:
        queryset = queryset.filter(filters)

    # Apply sorting based on query parameters
    sort_by = query_params.get("sort_by", None)
    if sort_by:
        if sort_by == "salary_low_to_high":
            # Order by salary ascending (nulls last)
            queryset = queryset.order_by(F("salary").asc(nulls_last=True))
        elif sort_by == "salary_high_to_low":
            # Order by salary descending (nulls last)
            queryset = queryset.order_by(F("salary").desc(nulls_last=True))
        elif sort_by == "latest":
            queryset = queryset.order_by("-created_at")
        elif sort_by == "oldest":
            queryset = queryset.order_by("created_at")
        # Add more sorting options as needed

    return queryset
