# cinema/models.py
from __future__ import annotations
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone


# ──────────────────────────────── GENÉRICOS ────────────────────────────────
class TimeStampedModel(models.Model):
    """Añade campos 'created' y 'updated' a las tablas."""
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ('-created',)


# ───────────────────────────── CINE Y SALAS ───────────────────────────────
class Cinema(TimeStampedModel):
    """Multicines o complejos cinematográficos (sucursales)."""
    name          = models.CharField(max_length=150)
    address       = models.CharField(max_length=250)
    city          = models.CharField(max_length=100)
    state         = models.CharField(max_length=100)
    phone         = models.CharField(max_length=30, blank=True)
    is_active     = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


class Auditorium(TimeStampedModel):
    """Sala física dentro de un complejo."""
    cinema        = models.ForeignKey(Cinema, on_delete=models.CASCADE, related_name='auditoriums')
    name          = models.CharField(max_length=50)
    total_rows    = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(50)])
    total_cols    = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(50)])

    class Meta:
        unique_together = (('cinema', 'name'),)

    def __str__(self) -> str:
        return f'{self.cinema} · {self.name}'


class Seat(models.Model):
    """Asiento fijo; se crea automáticamente a partir del layout."""
    auditorium    = models.ForeignKey(Auditorium, on_delete=models.CASCADE, related_name='seats')
    row           = models.PositiveSmallIntegerField()
    col           = models.PositiveSmallIntegerField()
    seat_type     = models.CharField(max_length=20, default='standard')  # ej. VIP, 4DX…

    class Meta:
        unique_together = (('auditorium', 'row', 'col'),)
        ordering = ('row', 'col')

    def __str__(self) -> str:
        return f'{self.auditorium} R{self.row}C{self.col}'


# ──────────────────────────────── PELÍCULAS ───────────────────────────────
class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Movie(TimeStampedModel):
    """Información básica de la película."""
    title         = models.CharField(max_length=200)
    original_title= models.CharField(max_length=200, blank=True)
    synopsis      = models.TextField(blank=True)
    duration_min  = models.PositiveSmallIntegerField(help_text='Duración en minutos')
    release_date  = models.DateField()
    rating        = models.CharField(max_length=10, help_text='Clasificación, p. ej. PG-13')
    poster        = models.ImageField(upload_to='posters/', blank=True)
    trailer_url   = models.URLField(blank=True)
    genres        = models.ManyToManyField(Genre, related_name='movies')
    is_active     = models.BooleanField(default=True)

    def __str__(self):
        return self.title


# ─────────────────────────── CARTELERA & FUNCIONES ────────────────────────
class Showtime(TimeStampedModel):
    """Una función individual (día-hora) para una película en cierta sala."""
    movie         = models.ForeignKey(Movie, on_delete=models.PROTECT, related_name='showtimes')
    auditorium    = models.ForeignKey(Auditorium, on_delete=models.PROTECT, related_name='showtimes')
    start_time    = models.DateTimeField()
    language      = models.CharField(max_length=20, choices=[('SUB', 'Subtitulada'), ('DUB', 'Doblada')])
    format        = models.CharField(max_length=10, choices=[('2D', '2D'), ('3D', '3D'), ('IMAX', 'IMAX')])
    base_price    = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        indexes = [models.Index(fields=('start_time',))]
        unique_together = (('auditorium', 'start_time'),)

    def __str__(self):
        return f'{self.movie} · {self.start_time:%d/%m %H:%M} · {self.auditorium}'

    @property
    def is_past(self) -> bool:
        return self.start_time < timezone.now()


# ─────────────────────── USUARIOS & PERFILES DE CLIENTE ───────────────────
class Customer(TimeStampedModel):
    """Perfil extendido para clientes (extiende AUTH_USER_MODEL)."""
    user         = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer')
    phone        = models.CharField(max_length=20, blank=True)
    loyalty_pts  = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


# ───────────────────────────── BOLETOS & ASIENTOS ─────────────────────────
class ReservationStatus(models.TextChoices):
    RESERVED = 'RES', 'Reservado'
    PAID     = 'PAI', 'Pagado'
    CANCELED = 'CAN', 'Cancelado'


class Ticket(TimeStampedModel):
    """Boletos individuales (1 asiento)."""
    showtime      = models.ForeignKey(Showtime, on_delete=models.PROTECT, related_name='tickets')
    seat          = models.ForeignKey(Seat, on_delete=models.PROTECT)
    customer      = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    status        = models.CharField(max_length=3, choices=ReservationStatus.choices, default=ReservationStatus.RESERVED)
    price         = models.DecimalField(max_digits=6, decimal_places=2)
    qr_code       = models.ImageField(upload_to='tickets/qr/', blank=True)  # opcional

    class Meta:
        unique_together = (('showtime', 'seat'),)  # evita doble venta
        ordering = ('showtime', 'seat')

    def __str__(self):
        return f'{self.showtime} · {self.seat}'


# ───────────────────────── SISTEMA DE COMIDAS / COMBOS ────────────────────
class SnackCategory(models.Model):
    name = models.CharField(max_length=80)
    def __str__(self): return self.name


class SnackItem(TimeStampedModel):
    category      = models.ForeignKey(SnackCategory, on_delete=models.PROTECT, related_name='items')
    name          = models.CharField(max_length=100)
    description   = models.TextField(blank=True)
    price         = models.DecimalField(max_digits=6, decimal_places=2)
    image         = models.ImageField(upload_to='snacks/', blank=True)
    is_available  = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# ────────────────────────────── COMPRAS ───────────────────────────────────
class PaymentMethod(models.TextChoices):
    CASH     = 'CSH', 'Efectivo'
    CARD     = 'CRD', 'Tarjeta'
    WALLET   = 'WLT', 'Wallet'
    POINTS   = 'PNT', 'Puntos'


class Order(TimeStampedModel):
    """Una orden puede incluir boletos y / o comida."""
    customer      = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, related_name='orders')
    payment_method= models.CharField(max_length=3, choices=PaymentMethod.choices)
    total_amount  = models.DecimalField(max_digits=8, decimal_places=2)
    paid_at       = models.DateTimeField(null=True, blank=True)

    class Status(models.TextChoices):
        PENDING  = 'PEN', 'Pendiente'
        PAID     = 'PAI', 'Pagada'
        CANCELED = 'CAN', 'Cancelada'
    status        = models.CharField(max_length=3, choices=Status.choices, default=Status.PENDING)

    def __str__(self):
        return f'Orden #{self.id} ({self.get_status_display()})'


class OrderTicket(models.Model):
    """Relación N:M entre Order y Ticket (tickets incluidos)."""
    order   = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_tickets')
    ticket  = models.OneToOneField(Ticket, on_delete=models.CASCADE)  # un ticket sólo puede pertenecer a una orden

    def __str__(self):
        return f'{self.order} · {self.ticket}'


class OrderSnack(models.Model):
    """Línea de productos de comida en la orden."""
    order   = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_snacks')
    snack   = models.ForeignKey(SnackItem, on_delete=models.PROTECT)
    qty     = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    price   = models.DecimalField(max_digits=6, decimal_places=2)  # precio momento de compra

    class Meta:
        unique_together = (('order', 'snack'),)

    def line_total(self):
        return self.qty * self.price

    def __str__(self):
        return f'{self.qty} × {self.snack} ({self.order})'