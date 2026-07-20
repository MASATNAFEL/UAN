from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, render
from .models import Estudiante


def detalles(request,cedula):
    estudiante=get_object_or_404(Estudiante, pk=cedula)
    return render(request, "estudiantes/detalles.html", {"estudiante": estudiante})

def index(request):
    lista_estudiantes=Estudiante.objects.all()
    template= loader.get_template("estudiantes/index.html")
    context= {"lista_estudiantes":lista_estudiantes}
    return HttpResponse(template.render(context,request))