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
    JudgeDocketRelation, Statute
)
from .serializers import (
    CourtSerializer, JudgeSerializer, JudgeListSerializer,
    DocketSerializer, DocketListSerializer,
    OpinionClusterSerializer,
    OpinionSerializer, OpinionListSerializer,
    OpinionsCitedSerializer, CitationNetworkSerializer,
    JudgeDocketRelationSerializer, 
    JudgeProfileSerializer, CaseHistorySerializer,
    CasePredictionSerializer, GeneralCasePredictionSerializer,
    CaseTypeAnalysisSerializer, SearchQuerySerializer,
    LegalResearchQuerySerializer, LegalResearchResponseSerializer,
    StatuteSerializer
)
from .ai_services import judge_analytics_service, case_analysis_service


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
    
    def list(self, request, *args, **kwargs):
        """Custom list with search and default limit"""
        search = request.query_params.get('search', '')
        court = request.query_params.get('court', '')
        limit = int(request.query_params.get('limit', 3))
        
        judges_data = judge_analytics_service.get_judge_list(search_query=search, court=court, limit=limit)
        return Response(judges_data)

    @action(detail=True, methods=['get'])
    def profile(self, request, pk=None):
        """Get detailed judge profile including ruling and time patterns"""
        judge_data = judge_analytics_service.get_judge_profile(pk)
        if not judge_data:
            return Response({'error': 'Judge not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = JudgeProfileSerializer(judge_data)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def case_history_stats(self, request, pk=None):
        """Get case history for this judge"""
        filters = {
            'case_type': request.query_params.get('case_type'),
            'status': request.query_params.get('status')
        }
        history = judge_analytics_service.get_case_history(pk, filters)
        serializer = CaseHistorySerializer(history)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def predict(self, request, pk=None):
        """AI-powered outcome prediction for this judge"""
        prediction = judge_analytics_service.predict_outcome(pk, request.data)
        return Response(prediction)
    
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
        """Get COMPLETE judge profile with ALL related data for frontend"""
        judge = self.get_object()
        
        basic_info = {
            'judge_id': judge.judge_id,
            'full_name': judge.full_name,
            'gender': judge.gender,
            'race': judge.race,
            'date_birth': judge.date_birth,
            'biography': judge.biography,
        }
        
        education = judge.education if judge.education else []
        positions = judge.positions if judge.positions else []
        opinions = judge.authored_opinions.select_related('cluster__docket__court').all()
        
        cases = []
        for opinion in opinions:
            docket = opinion.cluster.docket if opinion.cluster else None
            if not docket: continue
            
            case_info = {
                'case_id': docket.docket_id,
                'case_name': docket.case_name_short,
                'court': docket.court.short_name if docket.court else 'Unknown',
                'date_filed': docket.date_filed,
                'outcome_status': docket.outcome_status,
                'nature_of_suit': docket.nature_of_suit,
            }
            cases.append(case_info)
        
        response_data = {
            'basic_info': basic_info,
            'education': education,
            'positions': positions,
            'statistics': {
                'total_cases': len(cases),
                'total_opinions': opinions.count(),
            },
            'all_cases': cases,
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


class OpinionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Opinion model"""
    queryset = Opinion.objects.select_related('cluster__docket', 'author').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'author']
    search_fields = ['plain_text', 'cluster__docket__case_name']
    ordering_fields = ['date_filed', 'created_at']
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return OpinionListSerializer
        return OpinionSerializer


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


# ===================================
# AI Agent Endpoints
# ===================================

@api_view(['POST'])
@permission_classes([AllowAny])
def legal_research_query(request):
    """AI-powered legal research endpoint with advanced filters"""
    from .ai_services import legal_research_service
    
    # Extract filters from request
    filters = {
        'jurisdiction': request.data.get('jurisdiction'), # federal, state, all
        'court_level': request.data.get('court_level'),   # supreme, circuit, district, all
        'date_from': request.data.get('date_from'),
        'date_to': request.data.get('date_to'),
        'judge_name': request.data.get('judge_name'),
    }
    
    question = request.data.get('question', '')
    if not question:
        return Response({'error': 'Question is required'}, status=status.HTTP_400_BAD_REQUEST)
        
    response_data = legal_research_service.research_question(question=question, filters=filters)
    
    serializer = LegalResearchResponseSerializer(response_data)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def case_prediction(request):
    """AI-powered case outcome prediction"""
    case_type = request.data.get('case_type', '')
    similar_dockets = Docket.objects.filter(nature_of_suit__icontains=case_type).exclude(outcome_status='')
    total = similar_dockets.count()
    granted = similar_dockets.filter(outcome_status__icontains='grant').count()
    success_rate = (granted / total * 100) if total > 0 else 50.0
    
    return Response({
        'predicted_outcome': 'favorable' if success_rate > 50 else 'challenging',
        'success_probability': round(success_rate, 1),
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def semantic_search(request):
    """Semantic search using vector embeddings"""
    from .ai_services import embedding_service
    query = request.data.get('query', '')
    search_results = embedding_service.comprehensive_search(query)
    return Response(search_results)


@api_view(['GET'])
@permission_classes([AllowAny])
def statistics(request):
    """Get overall platform statistics"""
    return Response({
        'total_judges': Judge.objects.count(),
        'total_cases': Docket.objects.count(),
        'total_opinions': Opinion.objects.count(),
        'total_statutes': Statute.objects.count(),
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def legal_research_advanced(request):
    """Alias for legal_research_query with more verbose implementation if needed"""
    return legal_research_query(request._request)

@api_view(['GET'])
def judge_case_history(request, judge_id):
    """Case history for a specific judge"""
    try:
        judge = Judge.objects.get(judge_id=judge_id)
        opinions = judge.authored_opinions.select_related('cluster__docket').all()
        cases = [{
            'case_name': op.cluster.docket.case_name_short if op.cluster else 'Unknown',
            'date_filed': op.date_filed,
            'outcome': op.cluster.docket.outcome_status if op.cluster else '',
        } for op in opinions]
        return Response({'judge': judge.full_name, 'cases': cases})
    except Judge.DoesNotExist:
        return Response({'error': 'Judge not found'}, status=404)

@api_view(['GET'])
def citation_network(request, opinion_id):
    """Citation network for an opinion"""
    try:
        opinion = Opinion.objects.get(opinion_id=opinion_id)
        cites_to = OpinionsCited.objects.filter(citing_opinion=opinion).count()
        cited_by = OpinionsCited.objects.filter(cited_opinion=opinion).count()
        return Response({'opinion_id': opinion_id, 'cites_to': cites_to, 'cited_by': cited_by})
    except Opinion.DoesNotExist:
        return Response({'error': 'Opinion not found'}, status=404)

@api_view(['GET'])
def most_influential_cases(request):
    """Most influential cases based on citation count"""
    opinions = Opinion.objects.annotate(count=Count('cited_by')).order_by('-count')[:10]
    data = [{
        'case_name': op.cluster.docket.case_name_short if op.cluster else 'Unknown',
        'citations': op.count
    } for op in opinions]
    return Response(data)

@api_view(['POST'])
def case_prediction_advanced(request):
    """Advanced outcome prediction"""
    return case_prediction(request._request)

@api_view(['GET'])
@permission_classes([AllowAny])
def judge_details_profile(request, judge_id):
    """Standalone view for judge profile"""
    judge_data = judge_analytics_service.get_judge_profile(judge_id)
    if not judge_data:
        return Response({'error': 'Judge not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response(judge_data)

@api_view(['GET'])
@permission_classes([AllowAny])
def judge_case_history_v2(request, judge_id):
    """Standalone view for judge case history"""
    filters = {
        'case_type': request.query_params.get('case_type'),
        'status': request.query_params.get('status')
    }
    history = judge_analytics_service.get_case_history(judge_id, filters)
    return Response(history)

@api_view(['POST'])
@permission_classes([AllowAny])
def judge_prediction_view(request, judge_id):
    """Standalone view for judge outcome prediction"""
    prediction = judge_analytics_service.predict_outcome(judge_id, request.data)
    return Response(prediction)

@api_view(['POST'])
@permission_classes([AllowAny])
def general_case_prediction(request):
    """View for general case analysis and outcome prediction"""
    prediction = case_analysis_service.analyze_case(request.data)
    serializer = GeneralCasePredictionSerializer(prediction)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def case_type_analysis_view(request):
    """View for global case type success statistics"""
    stats = case_analysis_service.get_case_type_statistics()
    serializer = CaseTypeAnalysisSerializer(stats, many=True)
    return Response(serializer.data)
