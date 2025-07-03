from django.urls import path
from .views import HomeView, ShowtimeDetailView, SnackListView, SnackDetailView, SeatSelectionView


urlpatterns = [
   path("", HomeView.as_view(), name="home"),
   path("showtime/<int:pk>/", ShowtimeDetailView.as_view(), name="showtime_detail"),
   path("snacks/", SnackListView.as_view(), name="snack_list"),
   path("snacks/<int:pk>/", SnackDetailView.as_view(), name="snack_detail"),
   path("showtime/<int:pk>/seats/",SeatSelectionView.as_view(),name="seat_selection"),



]
