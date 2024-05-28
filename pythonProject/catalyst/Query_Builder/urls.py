from django.urls import path
from .views import register_view, login_view,profile,submit,upload_view,result_view,get_states,get_industries,get_cities,get_country,logout_view

urlpatterns = [
    path('', profile, name='login_view'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('upload/', upload_view, name='upload'),
    path('api/result/', result_view, name='result'),
    path('api/states/', get_states, name='get_states'),
    path('api/industries/', get_industries, name='get_industries'),
    path('api/country/', get_country, name='get_country'),
    path('api/cities/', get_cities, name='get_cities'),
    # path('confirmation/',confirmation, name='confirmation'),
    path('submit/',submit, name='submit'),

]