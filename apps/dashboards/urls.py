from django.urls import path
from . import views

app_name = "dashboards"

urlpatterns = [
    path("analytics/", views.AnalyticsDashboardView.as_view(), name="analytics"),
]
