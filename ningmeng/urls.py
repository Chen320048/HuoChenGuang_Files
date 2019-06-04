"""chenshi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.conf import settings

from apps.dashboard.views import *
from apps.dashboard.forms import MyAuthenticationForm

urlpatterns = [
    url(r'^ueditor/',include('DjangoUeditor.urls' )),

    url(r'^dashboard/', include('apps.dashboard.urls')),
    url(r'^account/', include('apps.account.urls')),
    url(r'^system/', include('apps.system.urls')),
    url(r'^class/', include('apps.classes.urls')),
    url(r'^activity/', include('apps.activity.urls')),
    url(r'^kinder/', include('apps.kindergarten.urls')),
    url(r'^attendance/', include('apps.attendance.urls')),
    # url(r'^order/', include('apps.order.urls')),
    # url(r'^news/', include('apps.news.urls')),
    # url(r'^store/', include('apps.store.urls')),
    # url(r'^finance/', include('apps.finance.urls')),
    # url(r'^advert/', include('apps.advert.urls')),
    # url(r'^api/', include('apps.api.urls')),

    url(r'^$', index, {'template_name':'dashboard/index.html'}),
    url(r'^login/?$', my_login,{'template_name':'dashboard/login.html', 'authentication_form':MyAuthenticationForm}),
    url(r'^logout/$', my_logout),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
