from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    PublicationViewSet, DeleteRequestViewSet, ActivityLogViewSet,
    DepartmentViewSet, ResultTypeViewSet, CitationDatabaseViewSet,
    PublicationTypeViewSet, PublicationScopeViewSet, AuthorStatusViewSet,
    ReportingPeriodViewSet, MonthViewSet, EntryStatusViewSet,
    ModerationStatusViewSet, PublisherViewSet
)

router = DefaultRouter()
router.register(r'publications', PublicationViewSet, basename='publication')
router.register(r'delete-requests', DeleteRequestViewSet, basename='delete-request')
router.register(r'activity-logs', ActivityLogViewSet, basename='activity-log')

# Роуты для справочников
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'result-types', ResultTypeViewSet, basename='result-type')
router.register(r'citation-databases', CitationDatabaseViewSet, basename='citation-database')
router.register(r'publication-types', PublicationTypeViewSet, basename='publication-type')
router.register(r'publication-scopes', PublicationScopeViewSet, basename='publication-scope')
router.register(r'author-statuses', AuthorStatusViewSet, basename='author-status')
router.register(r'reporting-periods', ReportingPeriodViewSet, basename='reporting-period')
router.register(r'months', MonthViewSet, basename='month')
router.register(r'entry-statuses', EntryStatusViewSet, basename='entry-status')
router.register(r'moderation-statuses', ModerationStatusViewSet, basename='moderation-status')
router.register(r'publishers', PublisherViewSet, basename='publisher')

urlpatterns = router.urls