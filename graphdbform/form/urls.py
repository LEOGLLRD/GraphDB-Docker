from django.urls import path
from .views import ontoprepo_view, custom_ruleset_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('ontoprepo/', ontoprepo_view, name='ontoprepo'),
    path('customruleset/', custom_ruleset_view, name='customruleset'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
