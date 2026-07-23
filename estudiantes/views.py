from django.http import HttpResponse
from .models import Estudiante
from django.db.models import Q
from django.shortcuts import get_object_or_404,render

def index(request):
    lista_Estudiantes = Estudiante.objects.all()
    context = {"lista_Estudiantes":lista_Estudiantes}
    return render(request,"estudiantes/index.html",context)
    
def informacion(request,cedula_ciudadania):
    estudiante=get_object_or_404(Estudiante,pk=cedula_ciudadania)
    return render(request,"estudiantes/informacion.html", {"estudiante":estudiante})

def buscar(request):
    consulta_nombre=request.GET.get("n","")
    consulta_cedula=request.GET.get("c","")
    resultado=Estudiante.objects.all()

    if consulta_nombre:
        resultado=resultado.filter(Q(nombre__icontains=consulta_nombre))

    if consulta_cedula:
        resultado=resultado.filter(Q(cedula_ciudadania=consulta_cedula))

    context={"consulta_nombre":consulta_nombre,"consulta_cedula":consulta_cedula,"resultado":resultado}
    return render(request,"estudiantes/buscar.html",context)
