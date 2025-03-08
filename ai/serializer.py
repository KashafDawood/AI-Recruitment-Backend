from rest_framework import serializers

class GenerateContractSerializer(serializers.Serializer):
    employer_name = serializers.CharField(max_length=255)
    employee_name = serializers.CharField(max_length=255)
    job_title = serializers.CharField(max_length=255)
    start_date = serializers.DateField()
    end_date = serializers.DateField(required=False, allow_null=True)
    salary = serializers.CharField(max_length=100)
    responsibilities = serializers.CharField()
    benefits = serializers.CharField(required=False, allow_blank=True)
    terms = serializers.CharField()
    state = serializers.CharField(max_length=100)  # New field for state
    employer_address = serializers.CharField(max_length=255)  # New field for employer address
    employee_address = serializers.CharField(max_length=255)  # New field for employee address

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
