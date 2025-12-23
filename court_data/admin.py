from django.contrib import admin
from .models import (
    Court, Judge, Docket, OpinionCluster, Opinion, OpinionsCited,
    JudgeDocketRelation
)


@admin.register(Court)
class CourtAdmin(admin.ModelAdmin):
    list_display = ['court_id', 'short_name', 'jurisdiction', 'court_type']
    list_filter = ['jurisdiction', 'court_type']
    search_fields = ['name', 'short_name', 'court_id']


@admin.register(Judge)
class JudgeAdmin(admin.ModelAdmin):
    list_display = ['judge_id', 'full_name', 'gender', 'date_birth']
    list_filter = ['gender', 'race']
    search_fields = ['full_name', 'name_last', 'name_first']


@admin.register(Docket)
class DocketAdmin(admin.ModelAdmin):
    list_display = ['docket_id', 'case_name_short', 'court', 'date_filed', 'nature_of_suit', 'outcome_status']
    list_filter = ['court', 'nature_of_suit', 'date_filed', 'outcome_status']
    search_fields = ['case_name', 'docket_number']
    date_hierarchy = 'date_filed'


@admin.register(OpinionCluster)
class OpinionClusterAdmin(admin.ModelAdmin):
    list_display = ['cluster_id', 'case_name_short', 'docket', 'date_filed', 'citation_count']
    list_filter = ['date_filed']
    search_fields = ['case_name', 'case_name_short']
    date_hierarchy = 'date_filed'


@admin.register(Opinion)
class OpinionAdmin(admin.ModelAdmin):
    list_display = ['opinion_id', 'cluster', 'author', 'type', 'date_filed']
    list_filter = ['type', 'date_filed']
    search_fields = ['cluster__case_name', 'plain_text']
    date_hierarchy = 'date_filed'


@admin.register(OpinionsCited)
class OpinionsCitedAdmin(admin.ModelAdmin):
    list_display = ['id', 'citing_opinion', 'cited_opinion', 'depth']
    list_filter = ['depth']
    search_fields = ['citing_opinion__cluster__case_name', 'cited_opinion__cluster__case_name']


@admin.register(JudgeDocketRelation)
class JudgeDocketRelationAdmin(admin.ModelAdmin):
    list_display = ['judge', 'docket', 'role', 'outcome']
    list_filter = ['role', 'outcome']
    search_fields = ['judge__full_name', 'docket__case_name']
