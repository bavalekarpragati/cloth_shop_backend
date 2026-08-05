from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    api_login_view, api_signup_view, api_logout_view, api_current_user_view,
    ProductViewSet, CategoryViewSet, SizeViewSet, ColorViewSet, SaleViewSet,
    AnalyticsView, ExportReportView,
)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'sizes', SizeViewSet, basename='size')
router.register(r'colors', ColorViewSet, basename='color')
router.register(r'sales', SaleViewSet, basename='sale')

urlpatterns = [
    # Auth
    path('auth/login/', api_login_view, name='api_login'),
    path('auth/signup/', api_signup_view, name='api_signup'),
    path('auth/logout/', api_logout_view, name='api_logout'),
    path('auth/me/', api_current_user_view, name='api_current_user'),

    # REST viewsets
    path('', include(router.urls)),

    # Analytics & Reports
    path('analytics/', AnalyticsView.as_view(), name='api_analytics'),
    path('reports/export/', ExportReportView.as_view(), name='api_export_report'),
]