# cinema/views.py
from django.views.generic import TemplateView, DetailView, ListView
from django.utils import timezone
from .models import Showtime, SnackItem
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.urls import reverse
from .models import Showtime, Ticket, Seat, ReservationStatus






class HomeView(TemplateView):
   template_name = "home.html"


   def get_context_data(self, **kwargs):
       ctx = super().get_context_data(**kwargs)


       # Cartelera: próximas 30 funciones ordenadas por hora
       ctx["showtimes"] = (
           Showtime.objects
           .select_related("movie", "auditorium", "auditorium__cinema")
           .filter(
               movie__is_active=True,
               auditorium__cinema__is_active=True,
           )
           .order_by("start_time")[:30]
       )


       # Snacks destacados: los 6 primeros disponibles (puedes cambiar el criterio)
       ctx["snacks"] = (
           SnackItem.objects
           .select_related("category")
           .filter(is_available=True)
           .order_by("-updated")[:6]
       )
       return ctx
   
class ShowtimeDetailView(DetailView):
   model = Showtime
   template_name = "showtime_detail.html"
   context_object_name = "showtime"


   def get_queryset(self):
       return (
           super()
           .get_queryset()
           .select_related("movie", "auditorium__cinema")
       )


class SnackListView(ListView):
   model = SnackItem
   template_name = "snack_list.html"
   context_object_name = "snacks"
   paginate_by = 12


   def get_queryset(self):
       return (
           SnackItem.objects
           .filter(is_available=True)
           .select_related("category")
           .order_by("name")
       )



class SnackDetailView(DetailView):
   model = SnackItem
   template_name = "snack_detail.html"
   context_object_name = "snack"

class SeatSelectionView(View):
   template_name = "seat_selection.html"


   def get(self, request, pk):
       showtime = get_object_or_404(
           Showtime.objects.select_related("auditorium__cinema", "movie"),
           pk=pk
       )
       aud = showtime.auditorium


       # Asientos “tomados”
       taken = set(
           showtime.tickets
           .filter(status__in=[ReservationStatus.RESERVED, ReservationStatus.PAID])
           .values_list("seat_id", flat=True)
       )


       # Obtener los asientos creados en BD
       seats_qs = aud.seats.all().order_by("row", "col")
       if not seats_qs.exists():
           return render(request, self.template_name, {
               "showtime": showtime,
               "no_seats": True
           })


       # Agrupamos por fila
       grid = {}
       for seat in seats_qs:
           grid.setdefault(seat.row, []).append(seat)


       return render(request, self.template_name, {
           "showtime": showtime,
           "grid": grid,
           "taken": taken,
       })
