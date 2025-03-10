from rest_framework import serializers


class GenerateContractSerializer(serializers.Serializer):
    app_id = serializers.IntegerField()
    start_date = serializers.DateField()
    end_date = serializers.DateField(required=False, allow_null=True)
    terms = serializers.CharField(
        required=False, default="Standard terms and conditions apply."
    )


class GenerateJobListing(serializers.Serializer):
    job_title = serializers.CharField(max_length=255, required=False, allow_blank=True)
    company = serializers.CharField(max_length=255, required=False, allow_blank=True)
    location = serializers.CharField(max_length=255, required=False, allow_blank=True)
    description = serializers.CharField(max_length=1000)
    experience_required = serializers.CharField(
        max_length=255, required=False, allow_blank=True
    )
    salary_range = serializers.CharField(
        max_length=100, required=False, allow_blank=True
    )


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


class BestCandidateSerializer(serializers.Serializer):
    applications = serializers.ListField()
    job_id = serializers.IntegerField()
