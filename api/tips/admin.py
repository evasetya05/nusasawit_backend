from django.contrib import admin
from .models import Tip, TipContributor, TipDiscussion

admin.site.register(Tip)
admin.site.register(TipContributor)
admin.site.register(TipDiscussion)