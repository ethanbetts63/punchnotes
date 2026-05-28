from django.urls import path
from . import views

urlpatterns = [
    path("killtony/episodes/", views.EpisodeListView.as_view()),
    path("killtony/episodes/<int:pk>/", views.EpisodeDetailView.as_view()),
    path("killtony/comedians/", views.ComedianListView.as_view()),
    path("killtony/comedians/<slug:slug>/", views.ComedianDetailView.as_view()),
    path("killtony/sets/<int:pk>/", views.SetDetailView.as_view()),
    path("killtony/jokes/", views.JokeListView.as_view()),
    path("killtony/bits/", views.BitListView.as_view()),
    path("killtony/topics/", views.TopicListView.as_view()),
]
