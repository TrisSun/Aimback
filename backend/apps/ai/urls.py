from django.urls import path

from . import views

app_name = "ai"

urlpatterns = [
    path("matches/search", views.MatchSearchView.as_view(), name="match-search"),
    path(
        "matches/<int:pk>/feedback",
        views.MatchFeedbackView.as_view(),
        name="match-feedback",
    ),
    path(
        "posts/<int:pk>/matches",
        views.PostMatchListView.as_view(),
        name="post-matches",
    ),
]
