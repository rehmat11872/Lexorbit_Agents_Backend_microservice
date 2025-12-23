from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    CourtViewSet, JudgeViewSet, DocketViewSet,
    OpinionViewSet, OpinionsCitedViewSet,
    legal_research_query, case_prediction, semantic_search,
    legal_research_advanced, statistics, citation_network,
    most_influential_cases, judge_details_profile,
    judge_case_history_v2, judge_prediction_view,
    general_case_prediction, case_type_analysis_view
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'courts', CourtViewSet, basename='court')
router.register(r'judges', JudgeViewSet, basename='judge')
router.register(r'cases', DocketViewSet, basename='case')
router.register(r'opinions', OpinionViewSet, basename='opinion')
router.register(r'citations', OpinionsCitedViewSet, basename='citation')

urlpatterns = [
    # JWT Authentication
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # AI Agent Endpoints (Basic)
    path('agents/legal-research/', legal_research_query, name='legal_research'),
    path('agents/case-prediction/', case_prediction, name='case_prediction'),
    path('agents/semantic-search/', semantic_search, name='semantic_search'),
    
    # Enhanced Judge Analytics Endpoints
    path('judges/<int:judge_id>/profile/', judge_details_profile, name='judge_profile'),
    path('judges/<int:judge_id>/case-history/', judge_case_history_v2, name='judge_case_history'),
    path('judges/<int:judge_id>/predict/', judge_prediction_view, name='judge_predict'),
    
    # General Case Analysis
    path('cases/predict/', general_case_prediction, name='general_case_prediction'),
    path('cases/type-analysis/', case_type_analysis_view, name='case_type_analysis'),
    
    # Enhanced Frontend Endpoints
    path('legal-research-advanced/', legal_research_advanced, name='legal_research_advanced'),
    path('citation-network/<int:opinion_id>/', citation_network, name='citation_network'),
    path('cases/most-influential/', most_influential_cases, name='most_influential_cases'),
    
    # Statistics
    path('statistics/', statistics, name='statistics'),

    # Router URLs (Keep at the bottom to avoid shadowing)
    path('', include(router.urls)),
]
