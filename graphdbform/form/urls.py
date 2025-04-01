from django.urls import path
from .views import ontoprepo_view, custom_ruleset_view

urlpatterns = [
    path('ontoprepo/', ontoprepo_view, name='ontoprepo'),
    path('customruleset/', custom_ruleset_view, name='customruleset'),
]
