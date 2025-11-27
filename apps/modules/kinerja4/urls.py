from django.urls import path
from . import views

app_name = 'kinerja4'

urlpatterns = [
    path('dashboard/', views.kinerja4, name='dashboard'),

    path('kpi/', views.KPIListView.as_view(), name='kpi_list'),
    path('kpi/new/', views.KPICreateView.as_view(), name='kpi_create'),
    path('kpi/<int:kpi_id>/', views.KPIDetailView.as_view(), name='kpi_detail'),
    path('kpi/<int:kpi_id>/submit/', views.kpi_submit, name='kpi_submit'),
    path('kpi/<int:kpi_id>/edit/', views.KPIEditView.as_view(), name='kpi_edit'),
    path('kpi/<int:kpi_id>/approval/', views.KPIApprovalView.as_view(), name='kpi_approval'),
    path('kpi/<int:kpi_id>/period-input/', views.KPIPeriodInputView.as_view(), name='kpi_period_input'),
    path('evaluation/<int:eval_id>/approval/', views.KPIEvaluationApprovalView.as_view(), name='evaluation_approval'),

    path('cycle/new/', views.KPICycleCreateView.as_view(), name='cycle_create'),
    path('cycle/<int:id>/', views.KPICycleTemplateView.as_view(), name='cycle_detail'),
    path('cycle/period-grid/', views.get_period_grid, name='cycle_period_grid'),
]
