# from django.contrib import admin
from django.forms import TextInput, Textarea
from nested_inline.admin import *
from yoccore import models as m

class DefaultAdmin(NestedModelAdmin):
    list_display = ('id', '__unicode__')
    actions_on_top = True
    save_as = True
    save_on_top = True
    list_per_page = 30
    ordering = ['id']
    formfield_overrides = {
    models.CharField: {'widget': Textarea(attrs={'rows': 8, 'cols': 60})},
    models.TextField: {'widget': Textarea(attrs={'rows': 8, 'cols': 60})},
    models.DecimalField: {'widget': TextInput(attrs={'size': '10'})},
    }
    list_display_links = ('id', '__unicode__')

class DefaultViewer(NestedTabularInline):
    save_as = True
    save_on_top = True
    extra = 3
    ordering = ['id']
    formfield_overrides = {
    models.CharField: {'widget': Textarea(attrs={'rows': 4, 'cols': 60})},
    models.TextField: {'widget': Textarea(attrs={'rows': 8, 'cols': 60})},
    models.DecimalField: {'widget': TextInput(attrs={'size': '10'})},
    }

admin.site.register(m.Session, DefaultAdmin)
admin.site.register(m.Question, DefaultAdmin)
admin.site.register(m.Answer, DefaultAdmin)
admin.site.register(m.CleanedAnswer, DefaultAdmin)
