
from django.db import models

# Create your models here.


class Vehiculo(models.Model):
    COLORLIST=(
        ('1','ROJO'),
        ('2','AZUL'),
        ('3','VERDE'),
    )
    placa = models.CharField(max_length=10)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    color_vehiculo = models.CharField(max_length=1, choices=COLORLIST)
