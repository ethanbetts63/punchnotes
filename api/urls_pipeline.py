from django.urls import path

from api.views.pipeline import (
    AnnotatedSetView,
    AudioHistoryView,
    ComedianAliasesView,
    ComedianCandidatesView,
    EmbeddingsView,
    EpMetaView,
    MissingSetImagesView,
    SetImagesView,
    UnembeddedBeatsView,
    VideoScrapeQueueView,
    VideoScrapeResultView,
)

urlpatterns = [
    path("annotated-set/", AnnotatedSetView.as_view()),
    path("audio-history/", AudioHistoryView.as_view()),
    path("comedian-candidates/", ComedianCandidatesView.as_view()),
    path("comedian-aliases/", ComedianAliasesView.as_view()),
    path("ep-meta/", EpMetaView.as_view()),
    path("missing-set-images/", MissingSetImagesView.as_view()),
    path("set-images/", SetImagesView.as_view()),
    path("unembedded-beats/", UnembeddedBeatsView.as_view()),
    path("embeddings/", EmbeddingsView.as_view()),
    path("videos-to-scrape/", VideoScrapeQueueView.as_view()),
    path("video-scrape-result/", VideoScrapeResultView.as_view()),
]
