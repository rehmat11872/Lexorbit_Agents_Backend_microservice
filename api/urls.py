from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    CourtViewSet, JudgeViewSet, DocketViewSet,
    OpinionViewSet, OpinionsCitedViewSet, StatuteViewSet,
    legal_research_query, case_prediction, semantic_search, statistics,
    legal_research_advanced, judge_case_history, citation_network,
    most_influential_cases, case_prediction_advanced, judges_search,
    judge_analytics_summary, judge_analytics_overview
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'courts', CourtViewSet, basename='court')
router.register(r'judges', JudgeViewSet, basename='judge')
router.register(r'cases', DocketViewSet, basename='case')
router.register(r'opinions', OpinionViewSet, basename='opinion')
router.register(r'citations', OpinionsCitedViewSet, basename='citation')
router.register(r'statutes', StatuteViewSet, basename='statute')

urlpatterns = [
    # JWT Authentication
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Judge Analytics (BEFORE router)
    path('judge-analytics/summary/', judge_analytics_summary, name='judge_analytics_summary'),
    path('judge-analytics/overview/', judge_analytics_overview, name='judge_analytics_overview'),
    path('judges/search/', judges_search, name='judges_search'),
    
    # Enhanced Frontend Endpoints
    path('legal-research-advanced/', legal_research_advanced, name='legal_research_advanced'),
    path('judges/<int:judge_id>/case-history/', judge_case_history, name='judge_case_history'),
    path('citation-network/<int:opinion_id>/', citation_network, name='citation_network'),
    path('cases/most-influential/', most_influential_cases, name='most_influential_cases'),
    path('case-prediction-advanced/', case_prediction_advanced, name='case_prediction_advanced'),
    
    # AI Agent Endpoints
    path('agents/legal-research/', legal_research_query, name='legal_research'),
    path('agents/case-prediction/', case_prediction, name='case_prediction'),
    path('agents/semantic-search/', semantic_search, name='semantic_search'),
    
    # Statistics
    path('statistics/', statistics, name='statistics'),
    
    # Router URLs (LAST)
    path('', include(router.urls)),
]

