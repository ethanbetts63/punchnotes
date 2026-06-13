from django.urls import path
from . import views

urlpatterns = [
    path("killtony/episodes/", views.EpisodeListView.as_view()),
    path("killtony/episodes/<int:pk>/", views.EpisodeDetailView.as_view()),
    path("killtony/comedians/", views.ComedianListView.as_view()),
    path("killtony/comedians/<slug:slug>/", views.ComedianDetailView.as_view()),
    path("killtony/sets/", views.SetListView.as_view()),
    path("killtony/sets/<int:pk>/", views.SetDetailView.as_view()),
    path("killtony/jokes/", views.BeatListView.as_view()),
    path("killtony/bits/", views.BitListView.as_view()),
    path("killtony/search/", views.NavSearchView.as_view()),
]
