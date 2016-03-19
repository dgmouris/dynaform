from django.contrib import admin
from .models import LegalQuestionaire,Questions,LegalDocuments,LegalTemplates
# Register your models here.
admin.site.register(LegalQuestionaire)
admin.site.register(Questions)
admin.site.register(LegalDocuments)
admin.site.register(LegalTemplates)