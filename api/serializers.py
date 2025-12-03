from rest_framework import serializers
from court_data.models import (
    Court, Judge, Docket, OpinionCluster, Opinion, OpinionsCited,
    JudgeDocketRelation, CaseOutcome, Statute
)


class CourtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Court
        fields = '__all__'


class JudgeSerializer(serializers.ModelSerializer):
    """Serializer for Judge model"""
    total_cases = serializers.SerializerMethodField()
    recent_cases = serializers.SerializerMethodField()
    
    class Meta:
        model = Judge
        fields = '__all__'
    
    def get_total_cases(self, obj):
        return obj.authored_opinions.count()
    
    def get_recent_cases(self, obj):
        recent = obj.authored_opinions.order_by('-date_filed')[:5]
        return OpinionSerializer(recent, many=True, context=self.context).data


class JudgeListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for judge lists"""
    total_opinions = serializers.SerializerMethodField()
    
    class Meta:
        model = Judge
        fields = ['id', 'judge_id', 'full_name', 'gender', 'biography', 'total_opinions', 'created_at']
    
    def get_total_opinions(self, obj):
        return obj.authored_opinions.count()


class DocketSerializer(serializers.ModelSerializer):
    """Serializer for Docket model"""
    court_name = serializers.CharField(source='court.name', read_only=True)
    opinions_count = serializers.SerializerMethodField()
    judges = serializers.SerializerMethodField()
    outcome = serializers.SerializerMethodField()
    
    class Meta:
        model = Docket
        fields = '__all__'
    
    def get_opinions_count(self, obj):
        return obj.opinions.count()
    
    def get_judges(self, obj):
        relations = obj.judge_relations.select_related('judge').all()
        return [{
            'judge_id': rel.judge.judge_id,
            'name': rel.judge.full_name,
            'role': rel.role,
        } for rel in relations]
    
    def get_outcome(self, obj):
        try:
            return CaseOutcomeSerializer(obj.outcome).data
        except CaseOutcome.DoesNotExist:
            return None


class DocketListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for docket lists"""
    court_name = serializers.CharField(source='court.short_name', read_only=True)
    
    class Meta:
        model = Docket
        fields = ['id', 'docket_id', 'case_name', 'case_name_short', 'court_name', 
                  'date_filed', 'nature_of_suit', 'created_at']


class OpinionClusterSerializer(serializers.ModelSerializer):
    """Serializer for OpinionCluster model"""
    docket_name = serializers.CharField(source='docket.case_name_short', read_only=True)
    court_name = serializers.CharField(source='docket.court.short_name', read_only=True)
    panel_judges = serializers.SerializerMethodField()
    opinions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = OpinionCluster
        fields = '__all__'
    
    def get_panel_judges(self, obj):
        return [judge.full_name for judge in obj.panel.all()]
    
    def get_opinions_count(self, obj):
        return obj.sub_opinions.count()


class OpinionSerializer(serializers.ModelSerializer):
    """Serializer for Opinion model"""
    case_name = serializers.CharField(source='cluster.case_name_short', read_only=True)
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    joined_by_names = serializers.SerializerMethodField()
    citations_made_count = serializers.SerializerMethodField()
    citations_received_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Opinion
        fields = '__all__'
    
    def get_joined_by_names(self, obj):
        return [judge.full_name for judge in obj.joined_by.all()]
    
    def get_citations_made_count(self, obj):
        return obj.cites_to.count()
    
    def get_citations_received_count(self, obj):
        return obj.cited_by.count()


class OpinionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for opinion lists"""
    case_name = serializers.CharField(source='cluster.case_name_short', read_only=True)
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    
    class Meta:
        model = Opinion
        fields = ['id', 'opinion_id', 'case_name', 'author_name', 'type', 'date_filed', 'created_at']


class OpinionsCitedSerializer(serializers.ModelSerializer):
    """Serializer for OpinionsCited model"""
    citing_case = serializers.CharField(source='citing_opinion.cluster.case_name_short', read_only=True)
    cited_case = serializers.CharField(source='cited_opinion.cluster.case_name_short', read_only=True)
    citing_opinion_id = serializers.IntegerField(source='citing_opinion.opinion_id', read_only=True)
    cited_opinion_id = serializers.IntegerField(source='cited_opinion.opinion_id', read_only=True)
    
    class Meta:
        model = OpinionsCited
        fields = '__all__'


class CitationNetworkSerializer(serializers.Serializer):
    """Serializer for citation network data"""
    opinion_id = serializers.IntegerField()
    case_name = serializers.CharField()
    cites_to = serializers.ListField(child=serializers.DictField())
    cited_by = serializers.ListField(child=serializers.DictField())
    total_citations = serializers.IntegerField()


class JudgeDocketRelationSerializer(serializers.ModelSerializer):
    """Serializer for Judge-Docket relationships"""
    judge_name = serializers.CharField(source='judge.full_name', read_only=True)
    case_name = serializers.CharField(source='docket.case_name_short', read_only=True)
    
    class Meta:
        model = JudgeDocketRelation
        fields = '__all__'


class CaseOutcomeSerializer(serializers.ModelSerializer):
    """Serializer for Case Outcomes"""
    case_name = serializers.CharField(source='docket.case_name_short', read_only=True)
    
    class Meta:
        model = CaseOutcome
        fields = '__all__'


class StatuteSerializer(serializers.ModelSerializer):
    """Serializer for Statutes"""
    related_cases_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Statute
        fields = '__all__'
    
    def get_related_cases_count(self, obj):
        return obj.related_opinions.count()


class JudgeAnalyticsSerializer(serializers.Serializer):
    """Serializer for judge analytics data"""
    judge_id = serializers.IntegerField()
    judge_name = serializers.CharField()
    total_cases = serializers.IntegerField()
    grant_rate = serializers.FloatField()
    deny_rate = serializers.FloatField()
    average_decision_days = serializers.FloatField()
    recent_cases = serializers.ListField(child=serializers.DictField())
    case_type_breakdown = serializers.DictField()
    yearly_activity = serializers.ListField(child=serializers.DictField())


class CasePredictionSerializer(serializers.Serializer):
    """Serializer for case prediction data"""
    case_id = serializers.IntegerField()
    case_name = serializers.CharField()
    predicted_outcome = serializers.CharField()
    success_probability = serializers.FloatField()
    factors = serializers.ListField(child=serializers.DictField())
    similar_cases = serializers.ListField(child=serializers.DictField())


class SearchQuerySerializer(serializers.Serializer):
    """Serializer for search queries"""
    query = serializers.CharField(required=True, max_length=500)
    court = serializers.CharField(required=False, allow_blank=True)
    date_from = serializers.DateField(required=False, allow_null=True)
    date_to = serializers.DateField(required=False, allow_null=True)
    case_type = serializers.CharField(required=False, allow_blank=True)
    max_results = serializers.IntegerField(required=False, default=50, max_value=100)


class LegalResearchQuerySerializer(serializers.Serializer):
    """Serializer for legal research queries"""
    question = serializers.CharField(required=True)
    jurisdiction = serializers.CharField(required=False, allow_blank=True)
    case_type = serializers.CharField(required=False, allow_blank=True)
    date_range = serializers.CharField(required=False, allow_blank=True)
    include_statutes = serializers.BooleanField(default=True)


class LegalResearchResponseSerializer(serializers.Serializer):
    """Serializer for legal research responses"""
    query = serializers.CharField()
    summary = serializers.CharField()
    key_authorities = serializers.ListField(child=serializers.DictField())
    analysis = serializers.CharField()
    citations = serializers.ListField(child=serializers.DictField())
    related_statutes = serializers.ListField(child=serializers.DictField())

