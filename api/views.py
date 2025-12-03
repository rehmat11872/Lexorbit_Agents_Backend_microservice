from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q, Avg, F, Sum, Case, When, IntegerField
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)

from court_data.models import (
    Court, Judge, Docket, OpinionCluster, Opinion, OpinionsCited,
    JudgeDocketRelation, CaseOutcome, Statute
)
from .serializers import (
    CourtSerializer, JudgeSerializer, JudgeListSerializer,
    DocketSerializer, DocketListSerializer,
    OpinionClusterSerializer,
    OpinionSerializer, OpinionListSerializer,
    OpinionsCitedSerializer, CitationNetworkSerializer,
    JudgeDocketRelationSerializer, CaseOutcomeSerializer,
    StatuteSerializer, JudgeAnalyticsSerializer,
    CasePredictionSerializer, SearchQuerySerializer,
    LegalResearchQuerySerializer, LegalResearchResponseSerializer
)


class StandardResultsPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class CourtViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Court model"""
    queryset = Court.objects.all()
    serializer_class = CourtSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['jurisdiction', 'court_type']
    search_fields = ['name', 'short_name']
    ordering_fields = ['name', 'created_at']
    permission_classes = [AllowAny]


class JudgeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Judge model"""
    queryset = Judge.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['gender', 'race']
    search_fields = ['full_name', 'name_last', 'name_first']
    ordering_fields = ['full_name', 'created_at']
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return JudgeListSerializer
        return JudgeSerializer
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get analytics for a specific judge"""
        judge = self.get_object()
        
        # Get all opinions by this judge
        opinions = judge.authored_opinions.select_related('cluster__docket').all()
        
        # Get judge-docket relations
        relations = JudgeDocketRelation.objects.filter(judge=judge)
        
        # Calculate grant/deny rates
        total_with_outcome = relations.exclude(outcome='').count()
        granted = relations.filter(outcome__icontains='grant').count()
        denied = relations.filter(outcome__icontains='deny').count()
        
        grant_rate = (granted / total_with_outcome * 100) if total_with_outcome > 0 else 0
        deny_rate = (denied / total_with_outcome * 100) if total_with_outcome > 0 else 0
        
        # Calculate average decision time
        outcomes = CaseOutcome.objects.filter(
            docket__judge_relations__judge=judge,
            decision_days__isnull=False
        )
        avg_decision_days = outcomes.aggregate(avg=Avg('decision_days'))['avg'] or 0
        
        # Get recent cases
        recent_opinions = opinions.order_by('-date_filed')[:10]
        recent_cases = [{
            'case_name': op.cluster.docket.case_name_short if op.cluster and op.cluster.docket else 'Unknown',
            'date_filed': op.date_filed,
            'type': op.type,
        } for op in recent_opinions]
        
        # Case type breakdown
        case_types = {}
        for relation in relations:
            nature = relation.docket.nature_of_suit or 'Unknown'
            case_types[nature] = case_types.get(nature, 0) + 1
        
        # Yearly activity
        yearly_activity = []
        for year in range(datetime.now().year - 5, datetime.now().year + 1):
            count = opinions.filter(date_filed__year=year).count()
            yearly_activity.append({
                'year': year,
                'count': count
            })
        
        data = {
            'judge_id': judge.judge_id,
            'judge_name': judge.full_name,
            'total_cases': opinions.count(),
            'grant_rate': round(grant_rate, 2),
            'deny_rate': round(deny_rate, 2),
            'average_decision_days': round(avg_decision_days, 1),
            'recent_cases': recent_cases,
            'case_type_breakdown': case_types,
            'yearly_activity': yearly_activity,
        }
        
        serializer = JudgeAnalyticsSerializer(data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def cases(self, request, pk=None):
        """Get all cases for a specific judge"""
        judge = self.get_object()
        opinions = judge.authored_opinions.select_related('cluster__docket').all()
        
        page = self.paginate_queryset(opinions)
        if page is not None:
            serializer = OpinionListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = OpinionListSerializer(opinions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def complete_profile(self, request, pk=None):
        """
        Get COMPLETE judge profile with ALL related data for frontend
        Includes: bio, education, positions, all cases, opinions, citations, analytics
        """
        judge = self.get_object()
        
        # Basic Info
        basic_info = {
            'judge_id': judge.judge_id,
            'full_name': judge.full_name,
            'name_first': judge.name_first,
            'name_middle': judge.name_middle,
            'name_last': judge.name_last,
            'gender': judge.gender,
            'race': judge.race,
            'date_birth': judge.date_birth,
            'date_death': judge.date_death,
            'dob_city': judge.dob_city,
            'dob_state': judge.dob_state,
            'biography': judge.biography,
        }
        
        # Education
        education = judge.education if judge.education else []
        
        # Positions
        positions = judge.positions if judge.positions else []
        
        # Get all opinions authored
        opinions = judge.authored_opinions.select_related('cluster__docket__court').all()
        
        # Process cases with details
        cases = []
        for opinion in opinions:
            docket = opinion.cluster.docket if opinion.cluster else None
            if not docket:
                continue
            
            # Get citations for this opinion
            cites_to_count = opinion.cites_to.count()
            cited_by_count = opinion.cited_by.count()
            
            case_info = {
                'case_id': docket.docket_id,
                'case_name': docket.case_name,
                'case_name_short': docket.case_name_short,
                'docket_number': docket.docket_number,
                'court': docket.court.short_name if docket.court else 'Unknown',
                'court_full_name': docket.court.name if docket.court else 'Unknown',
                'date_filed': docket.date_filed,
                'date_terminated': docket.date_terminated,
                'nature_of_suit': docket.nature_of_suit,
                'case_type': docket.nature_of_suit or 'Unknown',
                'cause': docket.cause,
                'jurisdiction': docket.jurisdiction_type,
                'opinion': {
                    'opinion_id': opinion.opinion_id,
                    'type': opinion.get_type_display(),
                    'date_filed': opinion.date_filed,
                    'excerpt': opinion.plain_text[:300] + '...' if opinion.plain_text else '',
                    'page_count': opinion.page_count,
                },
                'citations': {
                    'cites_to': cites_to_count,
                    'cited_by': cited_by_count,
                    'total': cites_to_count + cited_by_count,
                },
                'parties': docket.parties,
            }
            cases.append(case_info)
        
        # Analytics
        total_cases = len(cases)
        
        # Case types breakdown
        case_types = {}
        for case in cases:
            case_type = case['case_type']
            case_types[case_type] = case_types.get(case_type, 0) + 1
        
        # Get judge-docket relations for outcomes
        relations = JudgeDocketRelation.objects.filter(judge=judge)
        total_with_outcome = relations.exclude(outcome='').count()
        granted = relations.filter(outcome__icontains='grant').count()
        denied = relations.filter(outcome__icontains='deny').count()
        
        grant_rate = (granted / total_with_outcome * 100) if total_with_outcome > 0 else 0
        deny_rate = (denied / total_with_outcome * 100) if total_with_outcome > 0 else 0
        
        # Average decision time
        from django.db.models import Avg
        avg_decision_days = CaseOutcome.objects.filter(
            docket__judge_relations__judge=judge,
            decision_days__isnull=False
        ).aggregate(avg=Avg('decision_days'))['avg'] or 0
        
        # Yearly activity
        from django.db.models.functions import ExtractYear
        yearly_activity = []
        for year in range(datetime.now().year - 5, datetime.now().year + 1):
            count = opinions.filter(date_filed__year=year).count()
            yearly_activity.append({
                'year': year,
                'count': count
            })
        
        # Recent cases (last 10)
        recent_cases = sorted(cases, key=lambda x: x['date_filed'] or datetime.min.date(), reverse=True)[:10]
        
        # Courts served
        courts_served = list(set([case['court_full_name'] for case in cases]))
        
        # Build complete response
        response_data = {
            'basic_info': basic_info,
            'education': education,
            'positions': positions,
            'statistics': {
                'total_cases': total_cases,
                'total_opinions': opinions.count(),
                'grant_rate': round(grant_rate, 2),
                'deny_rate': round(deny_rate, 2),
                'average_decision_days': round(avg_decision_days, 1),
                'courts_served': courts_served,
            },
            'case_types_breakdown': case_types,
            'yearly_activity': yearly_activity,
            'recent_cases': recent_cases,
            'all_cases': cases,  # All cases for detailed view
        }
        
        return Response(response_data)


class DocketViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Docket (Case) model"""
    queryset = Docket.objects.select_related('court').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['court', 'nature_of_suit', 'jurisdiction_type']
    search_fields = ['case_name', 'case_name_short', 'docket_number']
    ordering_fields = ['date_filed', 'created_at']
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return DocketListSerializer
        return DocketSerializer
    
    @action(detail=True, methods=['get'])
    def opinions(self, request, pk=None):
        """Get all opinions for a specific case"""
        docket = self.get_object()
        opinions = docket.opinions.select_related('author').all()
        
        serializer = OpinionSerializer(opinions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def judges(self, request, pk=None):
        """Get all judges involved in a specific case"""
        docket = self.get_object()
        relations = docket.judge_relations.select_related('judge').all()
        
        serializer = JudgeDocketRelationSerializer(relations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def similar(self, request, pk=None):
        """Find similar cases using embeddings"""
        from .ai_services import embedding_service
        
        docket = self.get_object()
        max_results = int(request.query_params.get('max_results', 10))
        
        similar_cases = embedding_service.find_similar_cases(
            docket.docket_id, 
            max_results=max_results
        )
        
        return Response({
            'case_id': docket.docket_id,
            'case_name': docket.case_name_short,
            'similar_cases': similar_cases,
        })


class OpinionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Opinion model"""
    queryset = Opinion.objects.select_related('cluster__docket', 'author').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'author']
    search_fields = ['plain_text', 'docket__case_name']
    ordering_fields = ['date_filed', 'created_at']
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return OpinionListSerializer
        return OpinionSerializer
    
    @action(detail=True, methods=['get'])
    def citations(self, request, pk=None):
        """Get citation network for a specific opinion"""
        opinion = self.get_object()
        
        # Get opinions this opinion cites
        cites_to = OpinionsCited.objects.filter(
            source_opinion=opinion,
            citation_type='cites_to'
        ).select_related('cited_opinion__cluster__docket')
        
        cites_to_data = [{
            'opinion_id': c.cited_opinion.opinion_id,
            'case_name': c.cited_opinion.cluster.docket.case_name_short if c.cited_opinion.cluster and c.cited_opinion.cluster.docket else 'Unknown',
            'influence_score': c.influence_score,
        } for c in cites_to]
        
        # Get opinions that cite this opinion
        cited_by = OpinionsCited.objects.filter(
            target_opinion=opinion,
            citation_type='cites_to'
        ).select_related('citing_opinion__cluster__docket')
        
        cited_by_data = [{
            'opinion_id': c.citing_opinion.opinion_id,
            'case_name': c.citing_opinion.cluster.docket.case_name_short if c.citing_opinion.cluster and c.citing_opinion.cluster.docket else 'Unknown',
            'influence_score': c.influence_score,
        } for c in cited_by]
        
        data = {
            'opinion_id': opinion.opinion_id,
            'case_name': opinion.cluster.docket.case_name_short if opinion.cluster and opinion.cluster.docket else 'Unknown',
            'cites_to': cites_to_data,
            'cited_by': cited_by_data,
            'total_citations': len(cites_to_data) + len(cited_by_data),
        }
        
        serializer = CitationNetworkSerializer(data)
        return Response(serializer.data)


class OpinionsCitedViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for OpinionsCited model"""
    queryset = OpinionsCited.objects.select_related(
        'citing_opinion__cluster__docket',
        'cited_opinion__cluster__docket'
    ).all()
    serializer_class = OpinionsCitedSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['depth']
    ordering_fields = ['created_at']
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def most_influential(self, request):
        """Get most influential cases based on citation count"""
        # Get opinions with most citations received
        influential_opinions = Opinion.objects.annotate(
            citation_count=Count('cited_by')
        ).filter(citation_count__gt=0).order_by('-citation_count')[:20]
        
        data = [{
            'opinion_id': op.opinion_id,
            'case_name': op.cluster.case_name_short if op.cluster else 'Unknown',
            'citation_count': op.citation_count,
            'date_filed': op.date_filed,
        } for op in influential_opinions]
        
        return Response(data)


class StatuteViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Statute model"""
    queryset = Statute.objects.all()
    serializer_class = StatuteSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['jurisdiction', 'jurisdiction_type', 'is_active']
    search_fields = ['title', 'section', 'text']
    ordering_fields = ['title', 'created_at']
    permission_classes = [AllowAny]


# ===================================
# AI Agent Endpoints
# ===================================

@api_view(['POST'])
@permission_classes([AllowAny])
def legal_research_query(request):
    """
    AI-powered legal research endpoint with semantic search
    Uses embeddings for intelligent case discovery
    """
    from .ai_services import legal_research_service
    
    serializer = LegalResearchQuerySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    question = serializer.validated_data['question']
    jurisdiction = serializer.validated_data.get('jurisdiction', '')
    case_type = serializer.validated_data.get('case_type', '')
    
    # Use AI-powered semantic search and analysis
    response_data = legal_research_service.research_question(
        question=question,
        jurisdiction=jurisdiction,
        case_type=case_type
    )
    
    response_serializer = LegalResearchResponseSerializer(response_data)
    return Response(response_serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def case_prediction(request):
    """
    AI-powered case outcome prediction
    Accepts case details and predicts likely outcome
    """
    case_type = request.data.get('case_type', '')
    jurisdiction = request.data.get('jurisdiction', '')
    judge_id = request.data.get('judge_id')
    brief_summary = request.data.get('brief_summary', '')
    
    # TODO: Implement actual ML-based prediction
    # For now, return a mock response
    
    # Calculate success rate for similar cases
    similar_cases = CaseOutcome.objects.filter(
        docket__nature_of_suit__icontains=case_type
    )[:10]
    
    similar_cases_data = [{
        'case_name': outcome.docket.case_name_short,
        'outcome': outcome.outcome_type,
        'similarity_score': 0.85,  # Mock score
    } for outcome in similar_cases]
    
    response_data = {
        'case_id': 0,
        'case_name': 'Prediction for new case',
        'predicted_outcome': 'favorable',
        'success_probability': 73.0,
        'factors': [
            {'factor': 'Judge historical grant rate', 'impact': 'positive', 'weight': 0.4},
            {'factor': 'Similar case precedents', 'impact': 'positive', 'weight': 0.35},
            {'factor': 'Jurisdiction trends', 'impact': 'neutral', 'weight': 0.25},
        ],
        'similar_cases': similar_cases_data,
    }
    
    serializer = CasePredictionSerializer(response_data)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def semantic_search(request):
    """
    Semantic search using vector embeddings (pgvector + OpenAI)
    Automatically falls back to keyword search if embeddings unavailable
    """
    from .ai_services import embedding_service
    
    serializer = SearchQuerySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    query = serializer.validated_data['query']
    max_results = serializer.validated_data.get('max_results', 50)
    
    # Use comprehensive semantic search across all entity types
    search_results = embedding_service.comprehensive_search(query, max_results)
    
    # Combine results
    all_results = []
    all_results.extend(search_results['opinions'])
    all_results.extend(search_results['cases'])
    all_results.extend(search_results['judges'])
    
    return Response({
        'query': query,
        'total_results': len(all_results),
        'results': all_results,
        'breakdown': {
            'opinions': len(search_results['opinions']),
            'cases': len(search_results['cases']),
            'judges': len(search_results['judges']),
        }
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def statistics(request):
    """Get overall platform statistics"""
    stats = {
        'total_judges': Judge.objects.count(),
        'total_cases': Docket.objects.count(),
        'total_opinions': Opinion.objects.count(),
        'total_citations': OpinionsCited.objects.count(),
        'total_courts': Court.objects.count(),
        'recent_cases': Docket.objects.filter(
            date_filed__gte=datetime.now() - timedelta(days=30)
        ).count(),
    }
    
    return Response(stats)


# ===================================
# Enhanced Endpoints for Frontend
# ===================================

@api_view(['POST'])
@permission_classes([AllowAny])
def legal_research_advanced(request):
    """
    Advanced legal research with comprehensive filters
    Supports: jurisdiction, court level, date range, judge name
    """
    from .ai_services import legal_research_service, embedding_service
    
    query = request.data.get('query', '')
    filters = request.data.get('filters', {})
    
    if not query:
        return Response({'error': 'Query is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Parse filters
    jurisdiction = filters.get('jurisdiction', 'all')  # 'federal', 'state', 'all'
    court_level = filters.get('court_level', 'all')  # 'supreme', 'circuit', 'district', 'all'
    date_from = filters.get('date_from', '')
    date_to = filters.get('date_to', '')
    judge_name = filters.get('judge_name', '')
    
    # Build query filter
    opinion_query = Opinion.objects.select_related('cluster__docket__court', 'author').all()
    
    # Apply jurisdiction filter
    if jurisdiction == 'federal':
        opinion_query = opinion_query.filter(cluster__docket__court__jurisdiction='F')
    elif jurisdiction == 'state':
        opinion_query = opinion_query.filter(cluster__docket__court__jurisdiction='S')
    
    # Apply court level filter
    if court_level == 'supreme':
        opinion_query = opinion_query.filter(
            Q(cluster__docket__court__court_id='scotus') | 
            Q(cluster__docket__court__name__icontains='Supreme Court')
        )
    elif court_level == 'circuit':
        opinion_query = opinion_query.filter(cluster__docket__court__position='Appellate')
    elif court_level == 'district':
        opinion_query = opinion_query.filter(cluster__docket__court__position='District')
    
    # Apply date filters
    if date_from:
        opinion_query = opinion_query.filter(date_filed__gte=date_from)
    if date_to:
        opinion_query = opinion_query.filter(date_filed__lte=date_to)
    
    # Apply judge filter
    if judge_name:
        opinion_query = opinion_query.filter(author__full_name__icontains=judge_name)
    
    # Perform semantic search within filtered results
    try:
        # Get embedding for query
        relevant_opinions = embedding_service.semantic_search_opinions(query, max_results=20)
        
        # Filter by our criteria
        opinion_ids = [op['id'] for op in relevant_opinions]
        filtered_opinions = opinion_query.filter(opinion_id__in=opinion_ids)[:10]
    except Exception as e:
        # Fallback to keyword search
        logger.warning(f"Semantic search failed: {str(e)}, falling back to keyword search")
        filtered_opinions = opinion_query.filter(
            Q(plain_text__icontains=query) | 
            Q(cluster__case_name_short__icontains=query)
        )[:10]
    
    # Format results with key authorities
    cases = []
    for opinion in filtered_opinions:
        # Get citations for this opinion
        citing_count = opinion.cited_by.count()
        cites_to_count = opinion.cites_to.count()
        
        cluster = opinion.cluster
        docket = cluster.docket if cluster else None
        
        cases.append({
            'case_name': cluster.case_name_short if cluster else 'Unknown',
            'citation': f"{opinion.opinion_id}",
            'court': docket.court.name if docket and docket.court else 'Unknown',
            'date_filed': opinion.date_filed,
            'excerpt': opinion.plain_text[:500] if opinion.plain_text else '',
            'judge': opinion.author.full_name if opinion.author else 'Unknown',
            'citations': {
                'cited_by': citing_count,
                'cites_to': cites_to_count
            },
            'url': f"/api/opinions/{opinion.opinion_id}/"
        })
    
    # Generate AI summary
    try:
        research_result = legal_research_service.research_question(
            question=query,
            jurisdiction=jurisdiction,
            case_type=''
        )
        summary = research_result.get('summary', '')
        analysis = research_result.get('analysis', '')
    except:
        summary = f"Found {len(cases)} relevant cases matching your query."
        analysis = "Analysis unavailable - please check OpenAI API configuration."
    
    return Response({
        'query': query,
        'filters_applied': filters,
        'summary': summary,
        'analysis': analysis,
        'key_authorities': cases[:5],
        'all_cases': cases,
        'total_results': len(cases),
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def judge_case_history(request, judge_id):
    """
    Complete case history for a judge with filters
    Supports: case_type, status, date_from, date_to
    """
    try:
        judge = Judge.objects.get(judge_id=judge_id)
    except Judge.DoesNotExist:
        return Response({'error': 'Judge not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get filters
    case_type = request.query_params.get('case_type', '')
    case_status = request.query_params.get('status', '')  # 'active', 'closed'
    date_from = request.query_params.get('date_from', '')
    date_to = request.query_params.get('date_to', '')
    
    # Get all opinions by this judge
    opinions = judge.authored_opinions.select_related('cluster__docket__court').all()
    
    # Apply filters
    if case_type:
        opinions = opinions.filter(cluster__docket__nature_of_suit__icontains=case_type)
    
    if case_status == 'closed':
        opinions = opinions.filter(cluster__docket__date_terminated__isnull=False)
    elif case_status == 'active':
        opinions = opinions.filter(cluster__docket__date_terminated__isnull=True)
    
    if date_from:
        opinions = opinions.filter(date_filed__gte=date_from)
    if date_to:
        opinions = opinions.filter(date_filed__lte=date_to)
    
    # Format case history
    cases = []
    for opinion in opinions.order_by('-date_filed'):
        cluster = opinion.cluster
        if not cluster:
            continue
        docket = cluster.docket
        if not docket:
            continue
        
        # Get citations
        citing_count = opinion.cited_by.count()
        cites_to_count = opinion.cites_to.count()
        
        # Calculate duration
        duration_days = None
        if docket.date_filed and docket.date_terminated:
            duration_days = (docket.date_terminated - docket.date_filed).days
        elif docket.date_filed:
            duration_days = (datetime.now().date() - docket.date_filed).days
        
        # Get parties
        parties = []
        try:
            if docket.parties:
                parties_data = json.loads(docket.parties) if isinstance(docket.parties, str) else docket.parties
                parties = parties_data if isinstance(parties_data, list) else []
        except:
            pass
        
        # Determine precedent value based on citations
        if citing_count > 100:
            precedent_value = 'High'
        elif citing_count > 20:
            precedent_value = 'Medium'
        else:
            precedent_value = 'Low'
        
        cases.append({
            'docket_id': docket.docket_id,
            'case_number': docket.docket_number or 'N/A',
            'case_name': docket.case_name_short or docket.case_name,
            'case_type': docket.nature_of_suit or 'Unknown',
            'court': docket.court.name if docket.court else 'Unknown',
            'date_filed': docket.date_filed,
            'date_decided': docket.date_terminated or opinion.date_filed,
            'duration_days': duration_days,
            'status': 'Closed' if docket.date_terminated else 'Active',
            'parties': parties,
            'opinion_excerpt': opinion.plain_text[:300] if opinion.plain_text else '',
            'citations': {
                'cites_to': cites_to_count,
                'cited_by': citing_count,
                'total': cites_to_count + citing_count
            },
            'precedent_value': precedent_value,
        })
    
    # Calculate statistics
    total_cases = len(cases)
    closed_cases = len([c for c in cases if c['status'] == 'Closed'])
    active_cases = total_cases - closed_cases
    avg_duration = sum([c['duration_days'] for c in cases if c['duration_days']]) / len([c for c in cases if c['duration_days']]) if cases else 0
    
    return Response({
        'judge': {
            'judge_id': judge.judge_id,
            'full_name': judge.full_name,
        },
        'statistics': {
            'total_cases': total_cases,
            'closed_cases': closed_cases,
            'active_cases': active_cases,
            'avg_decision_days': round(avg_duration, 0),
        },
        'cases': cases,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def citation_network(request, opinion_id):
    """
    Get citation network for a specific opinion
    Shows what it cites and what cites it
    """
    try:
        opinion = Opinion.objects.get(opinion_id=opinion_id)
    except Opinion.DoesNotExist:
        return Response({'error': 'Opinion not found'}, status=status.HTTP_404_NOT_FOUND)
    
    depth = int(request.query_params.get('depth', 1))  # Citation depth (1 or 2 levels)
    
    # Get direct citations (what this case cites)
    cites_to = []
    for citation in opinion.cites_to.select_related('cited_opinion', 'cited_opinion__cluster__docket').all()[:50]:
        if citation.cited_opinion and citation.cited_opinion.cluster and citation.cited_opinion.cluster.docket:
            cites_to.append({
                'opinion_id': citation.cited_opinion.opinion_id,
                'case_name': citation.cited_opinion.cluster.docket.case_name_short,
                'date_filed': citation.cited_opinion.date_filed,
                'citation_count': citation.cited_opinion.cited_by.count(),
            })
    
    # Get citing cases (what cites this case)
    cited_by = []
    for citation in opinion.cited_by.select_related('citing_opinion', 'citing_opinion__cluster__docket').all()[:50]:
        if citation.citing_opinion and citation.citing_opinion.cluster and citation.citing_opinion.cluster.docket:
            cited_by.append({
                'opinion_id': citation.citing_opinion.opinion_id,
                'case_name': citation.citing_opinion.cluster.docket.case_name_short,
                'date_filed': citation.citing_opinion.date_filed,
                'citation_count': citation.citing_opinion.cited_by.count(),
            })
    
    # Calculate influence score (0-100)
    influence_score = min(100, (len(cited_by) * 2) + (len(cites_to) * 0.5))
    
    return Response({
        'primary_case': {
            'opinion_id': opinion.opinion_id,
            'case_name': opinion.cluster.docket.case_name_short if opinion.cluster and opinion.cluster.docket else 'Unknown',
            'date_filed': opinion.date_filed,
            'court': opinion.cluster.docket.court.name if opinion.cluster and opinion.cluster.docket and opinion.cluster.docket.court else 'Unknown',
        },
        'cites_to': cites_to,
        'cited_by': cited_by,
        'statistics': {
            'cites_to_count': len(cites_to),
            'cited_by_count': len(cited_by),
            'influence_score': round(influence_score, 1),
        },
        'network_depth': depth,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def most_influential_cases(request):
    """
    Get most influential cases based on citation counts
    Supports filters: time_period, category
    """
    time_period = request.query_params.get('time_period', '1950-2024')
    category = request.query_params.get('category', '')
    
    # Parse time period
    try:
        year_from, year_to = time_period.split('-')
        year_from = int(year_from)
        year_to = int(year_to)
    except:
        year_from = 1950
        year_to = 2024
    
    # Get opinions with citation counts
    opinions = Opinion.objects.select_related('cluster__docket', 'cluster__docket__court', 'author').annotate(
        citation_count=Count('cited_by')
    ).filter(
        date_filed__year__gte=year_from,
        date_filed__year__lte=year_to
    )
    
    # Apply category filter
    if category:
        opinions = opinions.filter(cluster__docket__nature_of_suit__icontains=category)
    
    # Get top 50 most cited
    influential_cases = []
    for opinion in opinions.order_by('-citation_count')[:50]:
        if not opinion.cluster or not opinion.cluster.docket:
            continue
        
        # Calculate influence percentage (relative to max citations)
        max_citations = 15000  # Approximate max for normalization
        influence_pct = min(100, (opinion.citation_count / max_citations) * 100)
        
        influential_cases.append({
            'opinion_id': opinion.opinion_id,
            'case_name': opinion.cluster.docket.case_name_short or opinion.cluster.docket.case_name,
            'year': opinion.date_filed.year if opinion.date_filed else None,
            'court': opinion.cluster.docket.court.name if opinion.cluster.docket.court else 'Unknown',
            'description': opinion.plain_text[:200] if opinion.plain_text else '',
            'citation_count': opinion.citation_count,
            'influence_score': round(influence_pct, 0),
            'judge': opinion.author.full_name if opinion.author else 'Unknown',
            'category': opinion.cluster.docket.nature_of_suit or 'Unknown',
        })
    
    return Response({
        'time_period': f"{year_from}-{year_to}",
        'category': category or 'All',
        'total_cases': len(influential_cases),
        'cases': influential_cases,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def case_prediction_advanced(request):
    """
    Advanced case outcome prediction
    Returns success probability, factors, and similar cases
    """
    case_type = request.data.get('case_type', '')
    jurisdiction = request.data.get('jurisdiction', '')
    judge_id = request.data.get('judge_id')
    brief_summary = request.data.get('brief_summary', '')
    
    # Calculate base success rate for this case type
    similar_outcomes = CaseOutcome.objects.filter(
        docket__nature_of_suit__icontains=case_type
    )
    
    total_outcomes = similar_outcomes.count()
    favorable_outcomes = similar_outcomes.filter(
        Q(outcome_type__icontains='grant') | 
        Q(outcome_type__icontains='favor')
    ).count()
    
    base_success_rate = (favorable_outcomes / total_outcomes * 100) if total_outcomes > 0 else 50.0
    
    # Adjust for judge if provided
    judge_adjustment = 0
    judge_data = {}
    if judge_id:
        try:
            judge = Judge.objects.get(judge_id=judge_id)
            judge_relations = JudgeDocketRelation.objects.filter(judge=judge)
            judge_grants = judge_relations.filter(outcome__icontains='grant').count()
            judge_total = judge_relations.exclude(outcome='').count()
            judge_grant_rate = (judge_grants / judge_total * 100) if judge_total > 0 else 50.0
            
            # Adjust prediction based on judge's history
            judge_adjustment = (judge_grant_rate - base_success_rate) * 0.3
            
            judge_data = {
                'judge_id': judge.judge_id,
                'full_name': judge.full_name,
                'grant_rate': round(judge_grant_rate, 1),
                'total_cases': judge_total,
            }
        except Judge.DoesNotExist:
            pass
    
    # Calculate final prediction
    predicted_success_rate = min(95, max(5, base_success_rate + judge_adjustment))
    
    # Determine outcome category
    if predicted_success_rate >= 75:
        outcome_category = 'Very Favorable'
    elif predicted_success_rate >= 60:
        outcome_category = 'Favorable'
    elif predicted_success_rate >= 40:
        outcome_category = 'Challenging'
    else:
        outcome_category = 'Difficult'
    
    # Get similar cases
    similar_cases = []
    for outcome in similar_outcomes.select_related('docket', 'docket__court')[:10]:  # CaseOutcome.docket is correct
        if outcome.docket:
            similar_cases.append({
                'case_name': outcome.docket.case_name_short,
                'outcome': outcome.outcome_type,
                'court': outcome.docket.court.name if outcome.docket.court else 'Unknown',
                'date': outcome.docket.date_filed,
                'similarity_score': 0.85,  # Mock similarity
            })
    
    # Analysis factors
    factors = [
        {
            'factor': 'Historical case type success rate',
            'impact': 'positive' if base_success_rate > 60 else 'negative',
            'weight': 0.4,
            'value': f"{round(base_success_rate, 1)}%"
        }
    ]
    
    if judge_data:
        factors.append({
            'factor': 'Judge historical grant rate',
            'impact': 'positive' if judge_adjustment > 0 else 'negative',
            'weight': 0.35,
            'value': f"{judge_data['grant_rate']}%"
        })
    
    factors.append({
        'factor': 'Jurisdiction trends',
        'impact': 'neutral',
        'weight': 0.25,
        'value': 'Average'
    })
    
    return Response({
        'prediction': {
            'success_probability': round(predicted_success_rate, 1),
            'outcome_category': outcome_category,
            'confidence': 87.3,  # Mock confidence
        },
        'judge': judge_data if judge_data else None,
        'factors': factors,
        'similar_cases': similar_cases,
        'historical_data': {
            'total_similar_cases': total_outcomes,
            'favorable_outcomes': favorable_outcomes,
            'base_success_rate': round(base_success_rate, 1),
        },
    })
