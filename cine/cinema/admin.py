# cinema/admin.py
from __future__ import annotations
from django.contrib import admin
from django.db.models import Sum
from django.utils.timezone import now

from . import models


# ────────────────────────────── ACCIONES ──────────────────────────────
@admin.action(description='Marcar como activo')
def make_active(modeladmin, request, queryset):
    queryset.update(is_active=True)

@admin.action(description='Marcar como inactivo')
def make_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False)


# ─────────────────────────────── INLINES ───────────────────────────────
class SeatInline(admin.TabularInline):
    model = models.Seat
    extra = 0
    readonly_fields = ('row', 'col', 'seat_type')
    can_delete = False
    ordering = ('row', 'col')


class OrderTicketInline(admin.TabularInline):
    model = models.OrderTicket
    extra = 0
    autocomplete_fields = ('ticket',)
    readonly_fields = ('ticket',)


class OrderSnackInline(admin.TabularInline):
    model = models.OrderSnack
    extra = 0
    autocomplete_fields = ('snack',)
    readonly_fields = ('qty', 'price', 'line_total')
    fields = ('snack', 'qty', 'price', 'line_total')
    show_change_link = False


# ───────────────────────────── CINEMAS ────────────────────────────────
@admin.register(models.Cinema)
class CinemaAdmin(admin.ModelAdmin):
    list_display   = ('name', 'city', 'state', 'phone', 'is_active', 'created')
    list_filter    = ('state', 'is_active')
    search_fields  = ('name', 'city', 'state', 'address')
    actions        = (make_active, make_inactive)
    ordering       = ('name',)


@admin.register(models.Auditorium)
class AuditoriumAdmin(admin.ModelAdmin):
    list_display        = ('name', 'cinema', 'total_rows', 'total_cols', 'seat_count')
    list_filter         = ('cinema',)
    search_fields       = ('name',)
    list_select_related = ('cinema',)
    inlines             = (SeatInline,)
    ordering            = ('cinema__name', 'name')

    @admin.display(description='Asientos')
    def seat_count(self, obj):
        return obj.seats.count()


@admin.register(models.Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display        = ('auditorium', 'row', 'col', 'seat_type')
    list_filter         = ('auditorium__cinema', 'seat_type')
    search_fields       = (
        'auditorium__name',
        'auditorium__cinema__name',
        'row',
        'col',
    )
    autocomplete_fields = ('auditorium',)
    list_select_related = ('auditorium', 'auditorium__cinema')
    ordering            = ('auditorium__cinema__name', 'auditorium__name', 'row', 'col')


# ──────────────────────────── PELÍCULAS ─────────────────────────────
@admin.register(models.Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    ordering      = ('name',)


@admin.register(models.Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display        = ('title', 'rating', 'duration_min', 'release_date', 'is_active', 'created')
    list_filter         = ('rating', 'is_active', 'release_date', 'genres')
    search_fields       = ('title', 'original_title')
    filter_horizontal   = ('genres',)
    actions             = (make_active, make_inactive)
    date_hierarchy      = 'release_date'
    readonly_fields     = ('created', 'updated')
    ordering            = ('-release_date',)


# ─────────────────────────── CARTELERA ──────────────────────────────
@admin.register(models.Showtime)
class ShowtimeAdmin(admin.ModelAdmin):
    list_display        = ('movie', 'auditorium', 'start_time', 'language', 'format', 'base_price', 'tickets_sold', 'is_past')
    list_filter         = ('language', 'format', 'auditorium__cinema')
    search_fields       = ('movie__title',)
    list_select_related = ('movie', 'auditorium', 'auditorium__cinema')
    date_hierarchy      = 'start_time'
    autocomplete_fields = ('movie', 'auditorium')
    ordering            = ('-start_time',)

    @admin.display(description='Vendidos')
    def tickets_sold(self, obj):
        return obj.tickets.filter(status=models.ReservationStatus.PAID).count()

    @admin.display(boolean=True, description='En el pasado')
    def is_past(self, obj):
        return obj.start_time < now()


# ─────────────────────────── CLIENTES ───────────────────────────────
@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display        = ('user', 'phone', 'loyalty_pts', 'created')
    search_fields       = ('user__username', 'user__first_name', 'user__last_name', 'phone')
    list_filter         = ('created',)
    autocomplete_fields = ('user',)
    ordering            = ('-created',)


# ─────────────────────────── BOLETOS ───────────────────────────────
@admin.register(models.Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display        = ('showtime', 'seat', 'customer', 'status', 'price', 'created')
    list_filter         = ('status', 'showtime__auditorium__cinema')
    search_fields       = ('customer__user__username', 'showtime__movie__title')
    autocomplete_fields = ('showtime', 'seat', 'customer')
    list_select_related = ('showtime', 'seat', 'customer')
    date_hierarchy      = 'created'
    ordering            = ('-created',)


# ─────────────────────── SNACKS & CATEGORÍAS ───────────────────────
@admin.register(models.SnackCategory)
class SnackCategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    ordering      = ('name',)


@admin.register(models.SnackItem)
class SnackItemAdmin(admin.ModelAdmin):
    list_display        = ('name', 'category', 'price', 'is_available')
    list_filter         = ('category', 'is_available')
    search_fields       = ('name',)
    actions             = (make_active, make_inactive)
    autocomplete_fields = ('category',)
    list_editable       = ('price', 'is_available')
    ordering            = ('name',)


# ───────────────────────────── ÓRDENES ─────────────────────────────
@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display        = ('id', 'customer', 'total_amount', 'payment_method', 'status', 'paid_at', 'created')
    list_filter         = ('status', 'payment_method', 'created')
    search_fields       = ('id', 'customer__user__username')
    autocomplete_fields = ('customer',)
    inlines             = (OrderTicketInline, OrderSnackInline)
    date_hierarchy      = 'created'
    ordering            = ('-created',)

    @admin.display(description='Snacks totales')
    def snack_total(self, obj):
        return obj.order_snacks.aggregate(total=Sum('qty'))['total'] or 0


# ───────────────────── CONFIGURACIÓN GLOBAL ────────────────────────
admin.site.site_header = 'Cinema Management'
admin.site.site_title  = 'Cinema Admin'
admin.site.index_title = 'Panel de control'
