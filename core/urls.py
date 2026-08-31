from django.urls import path
from .views import (
    PublicationViewSet, DeleteRequestViewSet, ActivityLogViewSet,
    reference_data,
)

publication_list = PublicationViewSet.as_view({'get': 'list', 'post': 'create'})
publication_detail = PublicationViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})
statistics_view = PublicationViewSet.as_view({'get': 'statistics'})
export_view = PublicationViewSet.as_view({'get': 'export'})
my_publications_view = PublicationViewSet.as_view({'get': 'my_publications'})
deleted_view = PublicationViewSet.as_view({'get': 'deleted'})
moderate_view = PublicationViewSet.as_view({'post': 'moderate'})
toggle_archive_view = PublicationViewSet.as_view({'post': 'toggle_archive'})
restore_view = PublicationViewSet.as_view({'post': 'restore'})
hard_delete_view = PublicationViewSet.as_view({'post': 'hard_delete'})
archive_old_view = PublicationViewSet.as_view({'post': 'archive_old_publications'})
delete_request_list = DeleteRequestViewSet.as_view({'get': 'list', 'post': 'create'})
delete_request_detail = DeleteRequestViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})
activity_log_list = ActivityLogViewSet.as_view({'get': 'list'})

urlpatterns = [
    path('reference/', reference_data, name='reference-data'),
    path('publications/statistics/', statistics_view, name='publication-statistics'),
    path('publications/export/', export_view, name='publication-export'),
    path('publications/my_publications/', my_publications_view, name='publication-my-publications'),
    path('publications/deleted/', deleted_view, name='publication-deleted'),
    path('publications/archive_old/', archive_old_view, name='publication-archive-old'),
    path('publications/', publication_list, name='publication-list'),
    path('publications/<pk>/', publication_detail, name='publication-detail'),
    path('publications/<pk>/moderate/', moderate_view),
    path('publications/<pk>/toggle_archive/', toggle_archive_view),
    path('publications/<pk>/restore/', restore_view),
    path('publications/<pk>/hard_delete/', hard_delete_view),
    path('delete-requests/', delete_request_list, name='delete-request-list'),
    path('delete-requests/<pk>/', delete_request_detail, name='delete-request-detail'),
    path('activity-logs/', activity_log_list, name='activity-log-list'),
]