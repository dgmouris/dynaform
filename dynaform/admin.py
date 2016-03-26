from django.contrib import admin
from .models import LegalQuestionaire,Questions,LegalDocuments,LegalTemplates,FormBaseLevel,FormLevelOne,FormLevelTwo,FormLevelThree
# Register your models here.
admin.site.register(LegalQuestionaire)
admin.site.register(Questions)
admin.site.register(LegalDocuments)
admin.site.register(LegalTemplates)
admin.site.register(FormBaseLevel)
admin.site.register(FormLevelOne)
admin.site.register(FormLevelTwo)
admin.site.register(FormLevelThree)