from django.urls import path
from django.contrib.auth import views as auth_views


# Para forzar POST en logout, creamos una subclase:
class LogoutPostOnly(auth_views.LogoutView):
   http_method_names = ['post']


urlpatterns = [
   path('login/',
        auth_views.LoginView.as_view(
            template_name='login.html'
        ),
        name='login'),
   path('logout/',
        LogoutPostOnly.as_view(),
        name='logout'),
]


