from rest_framework import serializers
from court_data.models import (
    Court, Judge, Docket, OpinionCluster, Opinion, OpinionsCited,
    JudgeDocketRelation, Statute
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
    """Lightweight serializer for judge search list with analytics summary"""
    court_name = serializers.CharField(source='authored_opinions.first.cluster.docket.court.name', read_only=True, default="Unknown Court")
    specialty = serializers.SerializerMethodField()
    grant_rate = serializers.SerializerMethodField()
    total_cases = serializers.SerializerMethodField()
    avg_decision_time = serializers.SerializerMethodField()
    recent_cases_count = serializers.SerializerMethodField()

    class Meta:
        model = Judge
        fields = [
            'id', 'judge_id', 'full_name', 'court_name', 'specialty', 
            'grant_rate', 'total_cases', 'avg_decision_time', 'recent_cases_count'
        ]

    def get_specialty(self, obj):
        # Most frequent nature of suit
        from django.db.models import Count
        nature = obj.docket_relations.values('docket__nature_of_suit').annotate(count=Count('id')).order_by('-count').first()
        return nature['docket__nature_of_suit'] if nature and nature['docket__nature_of_suit'] else "General Law"

    def get_grant_rate(self, obj):
        total = obj.docket_relations.exclude(outcome='').count()
        if total == 0: return 50.0  # Default or null
        granted = obj.docket_relations.filter(outcome__icontains='grant').count()
        return round((granted / total) * 100, 1)

    def get_total_cases(self, obj):
        return obj.docket_relations.count()

    def get_avg_decision_time(self, obj):
        from django.db.models import Avg
        avg = obj.docket_relations.filter(docket__decision_days__isnull=False).aggregate(Avg('docket__decision_days'))['docket__decision_days__avg']
        return round(avg, 1) if avg else 0

    def get_recent_cases_count(self, obj):
        return obj.authored_opinions.count() # Simplified


class DocketSerializer(serializers.ModelSerializer):
    """Serializer for Docket model"""
    court_name = serializers.CharField(source='court.name', read_only=True)
    opinions_count = serializers.SerializerMethodField()
    judges = serializers.SerializerMethodField()
    precedent_value = serializers.SerializerMethodField()
    
    class Meta:
        model = Docket
        fields = '__all__'
    
    def get_opinions_count(self, obj):
        return Opinion.objects.filter(cluster__docket=obj).count()
    
    def get_judges(self, obj):
        relations = obj.judge_relations.select_related('judge').all()
        return [{
            'judge_id': rel.judge.judge_id,
            'name': rel.judge.full_name,
            'role': rel.role,
        } for rel in relations]

    def get_precedent_value(self, obj):
        # Calculate based on total citations received by opinions in this docket
        count = OpinionsCited.objects.filter(cited_opinion__cluster__docket=obj).count()
        if count > 50: return "High"
        if count > 10: return "Medium"
        return "Low"


class DocketListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for docket lists"""
    court_name = serializers.CharField(source='court.short_name', read_only=True)
    
    class Meta:
        model = Docket
        fields = ['id', 'docket_id', 'case_name', 'case_name_short', 'court_name', 
                  'date_filed', 'nature_of_suit', 'outcome_status', 'created_at']


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


class StatuteSerializer(serializers.ModelSerializer):
    """Serializer for Statute model"""
    class Meta:
        model = Statute
        fields = '__all__'


class RulingPatternSerializer(serializers.Serializer):
    factor = serializers.CharField()
    lift = serializers.CharField()
    example = serializers.CharField()

class TimePatternSerializer(serializers.Serializer):
    window = serializers.CharField()
    percentage = serializers.IntegerField()

class JudgeProfileSerializer(serializers.Serializer):
    overview = serializers.DictField()
    analytics = serializers.DictField()
    patterns = serializers.ListField(child=RulingPatternSerializer())
    insights = serializers.ListField(child=TimePatternSerializer())
    distribution = serializers.ListField(child=serializers.DictField())

class CaseHistoryItemSerializer(serializers.Serializer):
    case_name = serializers.CharField()
    case_number = serializers.CharField()
    description = serializers.CharField()
    date_filed = serializers.CharField()
    date_decided = serializers.CharField()
    duration = serializers.IntegerField()
    amount = serializers.FloatField()
    outcome = serializers.CharField()
    case_type = serializers.CharField()
    plaintiff = serializers.CharField()
    defendant = serializers.CharField()
    precedent_value = serializers.CharField()
    status = serializers.CharField()

class CaseHistorySerializer(serializers.Serializer):
    total_cases = serializers.IntegerField()
    closed_cases = serializers.IntegerField()
    active_cases = serializers.IntegerField()
    avg_decision_time = serializers.FloatField()
    cases = serializers.ListField(child=CaseHistoryItemSerializer())


class ContributingFactorSerializer(serializers.Serializer):
    name = serializers.CharField()
    weight = serializers.CharField(required=False)
    value = serializers.CharField(required=False)
    sentiment = serializers.CharField(required=False) # For General Prediction

class CasePredictionSerializer(serializers.Serializer):
    """Serializer for judge-specific case prediction"""
    success_probability = serializers.IntegerField()
    confidence_level = serializers.CharField()
    estimated_decision_time = serializers.CharField()
    contributing_factors = serializers.ListField(child=ContributingFactorSerializer())
    strategic_recommendations = serializers.ListField(child=serializers.CharField())

class GeneralCasePredictionSerializer(serializers.Serializer):
    """Serializer for general case analysis and prediction"""
    success_probability = serializers.IntegerField()
    confidence_level = serializers.CharField()
    outcome_breakdown = serializers.DictField() # {favorable: 73, uncertain: 17, unfavorable: 10}
    contributing_factors = serializers.ListField(child=ContributingFactorSerializer())

class CaseTypeAnalysisSerializer(serializers.Serializer):
    """Serializer for aggregate case type success rates"""
    category = serializers.CharField()
    total_cases = serializers.IntegerField()
    granted_percentage = serializers.IntegerField()
    denied_percentage = serializers.IntegerField()

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


class LegalResearchResponseSerializer(serializers.Serializer):
    """Serializer for legal research responses"""
    question = serializers.CharField()
    summary = serializers.CharField()
    key_authorities = serializers.ListField(child=serializers.CharField())
    analysis = serializers.CharField()
    citations = serializers.ListField(child=serializers.CharField())
