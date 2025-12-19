"""
CORRECT Django Models for CourtListener API
Matches: Court → Docket → OpinionCluster → Opinion → Citations
"""

from django.db import models
# from pgvector.django import VectorField


class Court(models.Model):
    """Court (Supreme Court, Circuit Court, District Court, etc.)"""
    court_id = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=500)
    short_name = models.CharField(max_length=200, blank=True)
    jurisdiction = models.CharField(max_length=100)  # "F" (Federal) or "S" (State)
    position = models.CharField(max_length=100, blank=True)  # "Supreme", "Appellate", "District"
    court_type = models.CharField(max_length=100, blank=True)
    citation_string = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'courts'
        ordering = ['name']
        indexes = [
            models.Index(fields=['jurisdiction']),
            models.Index(fields=['position']),
        ]
    
    def __str__(self):
        return f"{self.short_name or self.name}"


class Judge(models.Model):
    """Judge/Justice who authors opinions"""
    judge_id = models.IntegerField(unique=True, db_index=True)
    name_first = models.CharField(max_length=200, blank=True)
    name_middle = models.CharField(max_length=200, blank=True)
    name_last = models.CharField(max_length=200, blank=True)
    name_suffix = models.CharField(max_length=50, blank=True)
    full_name = models.CharField(max_length=500, db_index=True)
    
    # Biography
    date_birth = models.DateField(null=True, blank=True)
    date_death = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, blank=True)
    race = models.CharField(max_length=100, blank=True)
    dob_city = models.CharField(max_length=200, blank=True)
    dob_state = models.CharField(max_length=100, blank=True)
    biography = models.TextField(blank=True)
    
    # Education & Positions (JSON from /educations/ and /positions/ APIs)
    education = models.JSONField(default=list, blank=True)
    positions = models.JSONField(default=list, blank=True)
    
    # Embedding for semantic search
    embedding = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'judges'
        ordering = ['full_name']
        indexes = [
            models.Index(fields=['full_name']),
        ]
    
    def __str__(self):
        return self.full_name


class Docket(models.Model):
    """Case file (lawsuit/case)"""
    docket_id = models.IntegerField(unique=True, db_index=True)
    court = models.ForeignKey(Court, on_delete=models.CASCADE, related_name='dockets')
    
    # Case information
    case_name = models.CharField(max_length=1000)
    case_name_short = models.CharField(max_length=500, blank=True)
    case_name_full = models.CharField(max_length=2000, blank=True)
    docket_number = models.CharField(max_length=200, blank=True, db_index=True)
    
    # Dates
    date_filed = models.DateField(null=True, blank=True, db_index=True)
    date_terminated = models.DateField(null=True, blank=True)
    date_last_filing = models.DateField(null=True, blank=True)
    
    # Case type (Civil/Criminal)
    nature_of_suit = models.CharField(max_length=500, blank=True, db_index=True)
    cause = models.CharField(max_length=500, blank=True)
    jury_demand = models.CharField(max_length=200, blank=True)
    jurisdiction_type = models.CharField(max_length=200, blank=True)
    
    # Parties
    parties = models.JSONField(default=list, blank=True)
    
    # Source
    source = models.CharField(max_length=100, default='court_listener')
    pacer_case_id = models.CharField(max_length=200, blank=True)
    
    # Embedding for semantic search
    embedding = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dockets'
        ordering = ['-date_filed']
        indexes = [
            models.Index(fields=['-date_filed']),
            models.Index(fields=['nature_of_suit']),
        ]
    
    def __str__(self):
        return f"{self.case_name_short or self.case_name}"


class OpinionCluster(models.Model):
    """Groups multiple opinions from same case decision"""
    cluster_id = models.IntegerField(unique=True, db_index=True)
    docket = models.ForeignKey(Docket, on_delete=models.CASCADE, related_name='clusters')
    
    # Case name
    case_name = models.CharField(max_length=1000)
    case_name_short = models.CharField(max_length=500, blank=True)
    case_name_full = models.CharField(max_length=2000, blank=True)
    
    # Date
    date_filed = models.DateField(null=True, blank=True, db_index=True)
    
    # Citation count
    citation_count = models.IntegerField(default=0)
    
    # Panel of judges
    panel = models.ManyToManyField(Judge, blank=True, related_name='panel_memberships')
    non_participating_judges = models.ManyToManyField(Judge, blank=True, related_name='non_participating_cases')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'opinion_clusters'
        ordering = ['-date_filed']
        indexes = [
            models.Index(fields=['-citation_count']),
        ]
    
    def __str__(self):
        return f"Cluster {self.cluster_id} - {self.case_name_short}"


class Opinion(models.Model):
    """Individual opinion (majority, dissent, concurrence)"""
    OPINION_TYPES = [
        ('010combined', 'Combined Opinion'),
        ('020lead', 'Lead Opinion'),
        ('030concurrence', 'Concurrence'),
        ('040dissent', 'Dissent'),
        ('050addendum', 'Addendum'),
    ]
    
    opinion_id = models.IntegerField(unique=True, db_index=True)
    cluster = models.ForeignKey(OpinionCluster, on_delete=models.CASCADE, related_name='sub_opinions')
    
    # Opinion details
    type = models.CharField(max_length=50, choices=OPINION_TYPES, default='010combined')
    author = models.ForeignKey(Judge, on_delete=models.SET_NULL, null=True, blank=True, related_name='authored_opinions')
    joined_by = models.ManyToManyField(Judge, blank=True, related_name='joined_opinions')
    
    # Content
    plain_text = models.TextField(blank=True)
    html = models.TextField(blank=True)
    html_lawbox = models.TextField(blank=True)
    html_columbia = models.TextField(blank=True)
    html_anon_2020 = models.TextField(blank=True)
    html_with_citations = models.TextField(blank=True)
    
    # Metadata
    date_filed = models.DateField(null=True, blank=True, db_index=True)
    page_count = models.IntegerField(null=True, blank=True)
    download_url = models.URLField(max_length=500, blank=True)
    local_path = models.FileField(upload_to='opinions/', blank=True)
    
    # Citations extracted
    extracted_citations = models.JSONField(default=list, blank=True)
    
    # Embedding for semantic search (CRITICAL!)
    embedding = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'opinions'
        ordering = ['-date_filed']
        indexes = [
            models.Index(fields=['author']),
        ]
    
    def __str__(self):
        return f"Opinion {self.opinion_id}"


class OpinionsCited(models.Model):
    """Citation relationships between opinions"""
    citing_opinion = models.ForeignKey(Opinion, on_delete=models.CASCADE, related_name='cites_to')
    cited_opinion = models.ForeignKey(Opinion, on_delete=models.CASCADE, related_name='cited_by')
    depth = models.IntegerField(default=1)
    citation_text = models.TextField(blank=True)
    influence_score = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'opinions_cited'
        unique_together = [['citing_opinion', 'cited_opinion']]
        indexes = [
            models.Index(fields=['citing_opinion']),
            models.Index(fields=['cited_opinion']),
        ]
    
    def __str__(self):
        return f"{self.citing_opinion.opinion_id} cites {self.cited_opinion.opinion_id}"


class JudgeDocketRelation(models.Model):
    """Judge-Case relationship for analytics"""
    ROLE_CHOICES = [
        ('author', 'Author'),
        ('joined', 'Joined'),
        ('dissent', 'Dissent'),
        ('concurrence', 'Concurrence'),
        ('presiding', 'Presiding Judge'),
        ('panel', 'Panel Member'),
    ]
    
    judge = models.ForeignKey(Judge, on_delete=models.CASCADE, related_name='docket_relations')
    docket = models.ForeignKey(Docket, on_delete=models.CASCADE, related_name='judge_relations')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, blank=True)
    outcome = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'judge_docket_relations'
        unique_together = [['judge', 'docket', 'role']]
        indexes = [
            models.Index(fields=['judge', 'outcome']),
        ]
    
    def __str__(self):
        return f"{self.judge.full_name} - {self.role}"


class CaseOutcome(models.Model):
    """Case outcome for predictions"""
    OUTCOME_TYPES = [
        ('granted', 'Granted'),
        ('denied', 'Denied'),
        ('affirmed', 'Affirmed'),
        ('reversed', 'Reversed'),
        ('remanded', 'Remanded'),
        ('dismissed', 'Dismissed'),
        ('settled', 'Settled'),
        ('vacated', 'Vacated'),
        ('other', 'Other'),
    ]
    
    docket = models.OneToOneField(Docket, on_delete=models.CASCADE, related_name='outcome')
    outcome_type = models.CharField(max_length=50, choices=OUTCOME_TYPES)
    decision_days = models.IntegerField(null=True, blank=True)
    disposition = models.TextField(blank=True)
    precedential_status = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'case_outcomes'
        indexes = [
            models.Index(fields=['outcome_type']),
        ]
    
    def __str__(self):
        return f"{self.docket.case_name_short} - {self.outcome_type}"


class Statute(models.Model):
    """Statutes and legal codes"""
    statute_id = models.CharField(max_length=200, unique=True, db_index=True)
    title = models.CharField(max_length=500)
    section = models.CharField(max_length=200, blank=True)
    text = models.TextField()
    jurisdiction = models.CharField(max_length=100)
    jurisdiction_type = models.CharField(max_length=50)
    effective_date = models.DateField(null=True, blank=True)
    repeal_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    related_opinions = models.ManyToManyField(Opinion, blank=True, related_name='cited_statutes')
    embedding = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'statutes'
        ordering = ['title', 'section']
        indexes = [
            models.Index(fields=['jurisdiction']),
        ]
    
    def __str__(self):
        return f"{self.title} § {self.section}"
