from django.conf.urls import url

from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    url(r'^(?P<lq_id>\d+)/$', views.questionaire_view, name='questionaire'),
    url(r'^upload-templates/$',views.legal_template_upload_view,name="legal templates")
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)