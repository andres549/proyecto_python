from django.views.generic import TemplateView


class AnalyticsDashboardView(TemplateView):
    """
    Vista contenedora que incrusta los componentes reactivos de Dash.
    """
    template_name = "dashboards/analytics.html"
