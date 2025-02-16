from rest_framework import serializers


class GenerateJobListing(serializers.Serializer):
    job_title = serializers.CharField(max_length=255)
    company = serializers.CharField(max_length=255)
    location = serializers.CharField(max_length=255)
    requirements = serializers.CharField(max_length=1000)
    experience_required = serializers.CharField(max_length=255)
    salary_range = serializers.CharField(
        max_length=100, required=False, allow_blank=True
    )
    benefits = serializers.CharField(max_length=255, required=False, allow_blank=True)


class GenerateBlogSerializer(serializers.Serializer):
    blog_title = serializers.CharField(max_length=255)
    blog_description = serializers.CharField()
    BLOG_LENGTH_CHOICES = [
        ("600 words", "600 words"),
        ("800 words", "800 words"),
        ("1000 words", "1000 words"),
    ]
    blog_keywords = serializers.CharField(
        max_length=255, required=False, allow_blank=True
    )
    blog_length = serializers.ChoiceField(
        choices=BLOG_LENGTH_CHOICES, allow_blank=True, required=False
    )
