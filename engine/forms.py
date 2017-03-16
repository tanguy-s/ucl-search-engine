# -*- coding: utf-8 -*-
import hashlib
from django import forms

from engine.models import WebPage


class WebPageForm(forms.ModelForm):

    class Meta:
        model = WebPage
        fields = [
            'raw_html',
            'content_type',
            'status'
        ]

    def save(self, commit=True):
        page = super(WebPageForm, self).save(commit=False)
        page.crawled = True
        # m = hashlib.md5()
        # m.update(page.url.encode('utf-8'))
        # page.url_hash = m.hexdigest()
        if commit:
            page.save()  
        return page