from django.urls import path

from . import views

app_name = 'claims'

urlpatterns = [
    path('posts/<int:pk>/claim-questions', views.ClaimQuestionListView.as_view(), name='claim-questions'),
    path('posts/<int:pk>/claim', views.ClaimCreateView.as_view(), name='claim-create'),
    path('posts/<int:pk>/claims', views.PostClaimListView.as_view(), name='post-claims'),
    path('my-claims', views.MyClaimListView.as_view(), name='my-claims'),
    path('claims/<int:pk>', views.ClaimDetailView.as_view(), name='claim-detail'),
    path('claims/<int:pk>/approve', views.ClaimApproveView.as_view(), name='claim-approve'),
    path('claims/<int:pk>/reject', views.ClaimRejectView.as_view(), name='claim-reject'),
    path('claims/<int:pk>/cancel', views.ClaimCancelView.as_view(), name='claim-cancel'),
    path('claims/<int:pk>/confirm-handover', views.ClaimConfirmView.as_view(), name='claim-confirm'),
]
