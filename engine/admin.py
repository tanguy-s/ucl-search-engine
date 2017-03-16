from django.contrib import admin

from engine.models import WebPage

# Register your models here.
@admin.register(WebPage)
class WebPageAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    fields = ()
