from django.contrib import admin
from django.urls import path
from real_estate import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.house_list, name = 'house_list'),
    path('generate/', views.generate_new_data, name = 'generate_new_data'),
]
