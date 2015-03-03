from django.db import models
from django.contrib import admin
from django.forms import TextInput, Textarea
from yoccore import models as m

class DefaultAdmin(admin.ModelAdmin):
    list_display = ('id', '__unicode__')
    actions_on_top = True
    save_as = True
    save_on_top = True
    list_per_page = 40
    ordering = ['id']
    formfield_overrides = {
    models.CharField: {'widget': Textarea(attrs={'rows': 8, 'cols': 60})},
    models.TextField: {'widget': Textarea(attrs={'rows': 8, 'cols': 60})},
    models.DecimalField: {'widget': TextInput(attrs={'size': '10'})},
    }
    list_display_links = list_display
    search_fields = list_display

class DefaultViewer(admin.TabularInline):
    save_as = True
    save_on_top = True
    extra = 3
    ordering = ['id']
    formfield_overrides = {
    models.CharField: {'widget': Textarea(attrs={'rows': 4, 'cols': 60})},
    models.TextField: {'widget': Textarea(attrs={'rows': 8, 'cols': 60})},
    models.DecimalField: {'widget': TextInput(attrs={'size': '10'})},
    }


class CleanedAnswerInLine(DefaultViewer):
    model = m.CleanedAnswer
    extra = 0

class AnswerInLine(DefaultViewer):
    model = m.Answer
    extra = 0


class QuestionAdmin(DefaultAdmin):
    list_display = ('id', 'question_text', 'question_type', 'question_page', 'question_number')
    list_display_links = list_display
    search_fields = ['question_text']
    list_filter = ['question_type']
    inlines = [AnswerInLine]

class AnswerAdmin(DefaultAdmin):

    list_display = ('id', 'question', 'answer_text', 'session', 'get_user_initials', 'get_submit_time')
    list_display_links = list_display
    inlines = [CleanedAnswerInLine]
    search_fields = ('id', 'question__question_text', 'session__user_initials', 'session__session_key')
    list_filter = ['session__user_initials', 'question__question_type']

    def get_user_initials(self, obj):
        return obj.session.user_initials

    get_user_initials.short_description = 'User'
    get_user_initials.admin_order_field = 'session__user_initials'

    def get_submit_time(self, obj):
        return obj.session.submit_time

    get_submit_time.short_description = 'submit_time'
    get_submit_time.admin_order_field = 'session__submit_time'

admin.site.register(m.Session, DefaultAdmin)
admin.site.register(m.Question, QuestionAdmin)
admin.site.register(m.Answer, AnswerAdmin)
admin.site.register(m.CleanedAnswer, DefaultAdmin)
