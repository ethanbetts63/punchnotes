from django.contrib import admin

from .models import Comedian, Video, Set, Line, Bit, Beat


@admin.register(Comedian)
class ComedianAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'joke_count', 'avg_punch_density', 'has_small_joke_book', 'has_medium_joke_book', 'has_large_joke_book')
    list_filter = ('has_small_joke_book', 'has_medium_joke_book', 'has_large_joke_book')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('joke_count', 'avg_punch_density', 'avg_tag_density', 'avg_bits_per_set', 'avg_beats_per_set')


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'number', 'date', 'bucket_pull_count', 'golden_ticket_count', 'regular_count')
    list_filter = ('date',)
    search_fields = ('title', 'video_id')
    filter_horizontal = ('guests',)
    readonly_fields = ('scraped_at', 'bucket_pull_count', 'golden_ticket_count', 'regular_count', 'large_joke_book_count')


@admin.register(Set)
class SetAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'video', 'comedian', 'set_number', 'attributes', 'punch_density', 'tag_density')
    search_fields = ('comedian__name', 'video__title')
    readonly_fields = ('punch_density', 'tag_density')
    raw_id_fields = ('video', 'comedian')


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
