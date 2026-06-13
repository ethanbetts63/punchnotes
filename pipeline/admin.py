from django.contrib import admin

from .models import Comedian, Episode, Set, Line, Bit, Beat


@admin.register(Comedian)
class ComedianAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'joke_count', 'avg_hit_ratio', 'has_small_joke_book', 'has_medium_joke_book', 'has_large_joke_book')
    list_filter = ('has_small_joke_book', 'has_medium_joke_book', 'has_large_joke_book')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('joke_count', 'avg_hit_ratio', 'avg_punchline_tag_ratio', 'avg_bits_per_set', 'avg_beats_per_set')


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('episode_title', 'episode_number', 'published_at', 'bucket_pull_count', 'golden_ticket_count', 'regular_count')
    list_filter = ('published_at',)
    search_fields = ('episode_title', 'video_id')
    filter_horizontal = ('guests',)
    readonly_fields = ('scraped_at', 'bucket_pull_count', 'golden_ticket_count', 'regular_count', 'large_joke_book_count')


@admin.register(Set)
class SetAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'episode', 'comedian', 'set_number', 'attributes', 'hit_ratio', 'punchline_tag_ratio')
    search_fields = ('comedian__name', 'episode__episode_title')
    readonly_fields = ('hit_ratio', 'punchline_tag_ratio')
    raw_id_fields = ('episode', 'comedian')


@admin.register(Line)
class LineAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'set', 'line_number', 'label', 'start_seconds')
    list_filter = ('label',)
    search_fields = ('text',)
    raw_id_fields = ('set',)


@admin.register(Bit)
class BitAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'set', 'bit_id', 'line_start', 'line_end')
    search_fields = ('bit_id', 'summary')
    raw_id_fields = ('set',)


@admin.register(Beat)
class BeatAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'bit', 'beat_id', 'joke_type', 'line_start', 'line_end')
    list_filter = ('joke_type',)
    search_fields = ('beat_id', 'premise')
    raw_id_fields = ('bit',)
