from django.urls import path

from . import views

app_name = 'tickets'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('nouveau/', views.create_ticket, name='create'),
    path('<int:pk>/', views.ticket_detail, name='detail'),
    path('<int:pk>/modifier/', views.update_ticket, name='update'),
    path('<int:pk>/<str:decision>/', views.ticket_decision, name='decision'),
]
