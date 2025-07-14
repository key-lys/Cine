from django.urls import path
from .views import CancelOrderView, HomeView, ShowtimeDetailView, SnackListView, SnackDetailView, SeatSelectionView, OrderConfirmView, OrderSuccessView, OrderListView, TicketPDFView


urlpatterns = [
   path("", HomeView.as_view(), name="home"),
   path("showtime/<int:pk>/", ShowtimeDetailView.as_view(), name="showtime_detail"),
   path("snacks/", SnackListView.as_view(), name="snack_list"),
   path("snacks/<int:pk>/", SnackDetailView.as_view(), name="snack_detail"),
   path("showtime/<int:pk>/seats/",SeatSelectionView.as_view(),name="seat_selection"),


   path('showtime/<int:pk>/select/',SeatSelectionView.as_view(),name='select_seats'),
   path('order/<int:order_id>/confirm/',OrderConfirmView.as_view(),name='order_confirm'),
   path('order/<int:order_id>/success/',OrderSuccessView.as_view(),name='order_success'),
   path('orders/', OrderListView.as_view(), name='orders_list'),
   path('orders/', OrderListView.as_view(), name='orders_list'),
   path('order/<int:order_id>/ticket.pdf',TicketPDFView.as_view(),name='ticket_pdf'),

   path('order/<int:order_id>/cancel/',CancelOrderView.as_view(),name='order_cancel'),

]
