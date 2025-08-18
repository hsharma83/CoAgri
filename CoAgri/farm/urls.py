# farm/urls.py
from django.urls import path
from . import views

app_name = 'farm'

urlpatterns = [
    path('plans/', views.FarmPlanListView.as_view(), name='plan_list'),
    path('plan/new/', views.FarmPlanCreateView.as_view(), name='plan_create'),
    path('plan/<int:pk>/', views.FarmPlanDetailView.as_view(), name='plan_detail'),
    path('activity/add/', views.DailyActivityCreateView.as_view(), name='activity_add'),
    path('get-plan-steps/<int:plot_id>/', views.get_plan_steps, name='get_plan_steps'),
    path('farmlands/', views.FarmlandListView.as_view(), name='farmland_list'),
    path('farmland/<int:pk>/', views.FarmlandDetailView.as_view(), name='farmland_detail'),
    path('farm/<int:farm_pk>/finances/', views.FarmFinanceView.as_view(), name='farm_finances'),
    path('farm/<int:farm_pk>/expense/add/', views.ExpenseCreateView.as_view(), name='expense_add'),
    path('farm/<int:farm_pk>/cashin/add/', views.CashInCreateView.as_view(), name='cashin_add'),
    path('farm/<int:farm_pk>/sale/add/', views.SaleCreateView.as_view(), name='sale_add'),
    path('farm/<int:farm_pk>/stock/add/', views.InventoryMovementCreateView.as_view(), name='stock_add'),
    path('farm/<int:farm_pk>/stock/', views.StockRegisterView.as_view(), name='stock_register'),
    path('farm/<int:farm_pk>/finances/export/', views.FarmFinanceExportView.as_view(), name='finance_export'),
    path('item/add/', views.ItemCreateView.as_view(), name='item_add'),
    path('crop/add/', views.CropCreateView.as_view(), name='crop_add'),
    path('farm/<int:farm_pk>/produce/add/', views.CropProduceCreateView.as_view(), name='produce_add'),
]