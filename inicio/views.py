from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, render
from estudiantes.models import Estudiante



def index(request):
    template= loader.get_template("sgeiuan/index.html")
    return HttpResponse(template)