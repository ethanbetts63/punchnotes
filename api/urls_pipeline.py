from django.urls import path

from api.views.pipeline import (
    AnnotatedSetBatchView,
    AnnotatedSetView,
    AudioHistoryView,
    ComedianAliasesView,
    ComedianCandidatesView,
    MissingSetImagesView,
    SegmentEmbeddingsView,
    SetImageBatchView,
    UnsegmentedBeatSegmentsView,
    VideoScrapeQueueView,
    VideoScrapeResultView,
)

urlpatterns = [
    path("annotated-set/", AnnotatedSetView.as_view()),
    path("annotated-set-batch/", AnnotatedSetBatchView.as_view()),
    path("audio-history/", AudioHistoryView.as_view()),
    path("comedian-candidates/", ComedianCandidatesView.as_view()),
    path("comedian-aliases/", ComedianAliasesView.as_view()),
    path("missing-set-images/", MissingSetImagesView.as_view()),
    path("set-images-batch/", SetImageBatchView.as_view()),
    path("unsegmented-beat-segments/", UnsegmentedBeatSegmentsView.as_view()),
    path("segment-embeddings/", SegmentEmbeddingsView.as_view()),
    path("videos-to-scrape/", VideoScrapeQueueView.as_view()),
    path("video-scrape-result/", VideoScrapeResultView.as_view()),
]
