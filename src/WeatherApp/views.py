import os
import requests
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import FormMixin, DeleteView
from dotenv import load_dotenv

from .forms import AddCityForm
from .models import City


load_dotenv()
API_KEY = str(os.getenv('API_KEY'))


class CityWeather(ListView, FormMixin):
    template_name = 'WeatherApp/weather.html'
    model = City
    form_class = AddCityForm

    # def __init__(self, *args, **kwargs):
    #     super(CityWeather, self).__init__(*args, **kwargs)
    #     self.object_list = self.get_queryset()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        cities = City.objects.all()
        weather_data = []
        for city in cities:
            url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&lang=ru&units=metric&appid={API_KEY}'
            r = requests.get(url).json()
            city_weather = {
                'city': city,
                'temperature': r['main']['temp'],
                'desc': r['weather'][0]['description'],
                'icon': r['weather'][0]['icon']
            }
            weather_data.append(city_weather)
        context['weather'] = weather_data
        return context

    def get_success_url(self):
        return reverse_lazy('weather')

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        city = form.save(commit=False)
        url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}'
        r = requests.get(url).json()

        if r['cod'] == '404':
            raise ValidationError('Города с таким названием не существует')
        elif City.objects.filter(name=form.cleaned_data['name'].title()):
            raise ValidationError('Город с таким городом уже добавлен в список отслеживаемых')
        elif form.is_valid():
            form.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class DeleteCity(DeleteView):
    model = City
    success_url = reverse_lazy('weather')
