from django.contrib import admin
from .models import Choice,Poll,Vote

admin.site.register(Choice)
admin.site.register(Poll)
admin.site.register(Vote)

