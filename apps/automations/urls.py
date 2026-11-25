from django.urls import path
from . import views

app_name = "automations"

urlpatterns = [
    path("", views.AutomationControlView.as_view(), name="control_panel"),
    path("trigger/<str:job_type>/", views.TriggerJobManualView.as_view(), name="trigger_manual"),
]
