from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings

from . import views

urlpatterns = [
    url(r'^yearbook$', views.yearbook, name='yearbook'),    
    #url(r'^$', views.index, name='index'),
    url(r'^logout/$', views.userlogout, name='logout'),
    url(r'^changePassword$', views.changePassword, name='changePassword'),
    url(r'^profile$', views.profile, name='profile'),
    url(r'^answer$', views.answerMyself, name='answer'),
    url(r'^poll$', views.poll, name='poll'),
    url(r'^comment$', views.comment, name='comment'),
    url(r'^otherComment$', views.otherComment, name='otherComment'),
    url(r'^$', views.index,  name='login'),
    url(r'^auth$', views.authenticate, name='otherComment'),
    # url(r'^yearbook/$', views.yearbook, name='yearbook'),    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
