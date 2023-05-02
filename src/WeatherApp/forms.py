from django import forms
from WeatherApp.models import City


class AddCityForm(forms.ModelForm):
    def clean(self):
        data = super().clean()
        data['name'] = data['name'].title()
        return data

    class Meta:
        model = City
        fields = ('name',)
