from django import forms
from .models import  Vehiculo

class VehicleForm(forms.ModelForm):

    class Meta:
        model = Vehiculo

        fields = [
            "placa",
            "marca",
            "modelo",
            "color_vehiculo",
        ]

        labels = {
            'placa': "Número de placa",
            'marca': "Marca del vehículo",
            'modelo': "Modelo del vehículo",
            'color_vehiculo': "color del vehículo",
        }

        widgets = {
            'placa': forms.TextInput(attrs={"class": "form-control"}),
            'marca': forms.TextInput(attrs={"class": "form-control"}),
            'modelo': forms.TextInput(attrs={"class": "form-control"}),
            'color_vehiculo': forms.Select(attrs={"class": "form-control"}),
        }
