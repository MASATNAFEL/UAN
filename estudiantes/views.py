from django.http import HttpResponse
from .models import Estudiante
from django.views.generic import UpdateView
from .forms import FormularioEstudiante
from django.db.models import Q
from django.shortcuts import get_object_or_404,render,redirect


def index(request):
    lista_Estudiantes = Estudiante.objects.filter(activo=True).order_by('nombre')
    context = {"lista_Estudiantes":lista_Estudiantes}
    return render(request,"estudiantes/index.html",context)

def index1(request):
    return render(request,"estudiantes/index1.html")

def informacion(request,cedula_ciudadania):
    estudiante=get_object_or_404(Estudiante,pk=cedula_ciudadania)
    return render(request,"estudiantes/informacion.html", {"estudiante":estudiante})

def buscar(request):
    consulta_nombre=request.GET.get("n","")
    consulta_cedula=request.GET.get("c","")
    resultado=Estudiante.objects.filter(activo=True).order_by("nombre")

    if consulta_nombre:
        resultado=resultado.filter(Q(nombre__icontains=consulta_nombre))

    if consulta_cedula:
        resultado=resultado.filter(Q(cedula_ciudadania=consulta_cedula))

    context={"consulta_nombre":consulta_nombre,"consulta_cedula":consulta_cedula,"resultado":resultado}
    return render(request,"estudiantes/buscar.html",context)

def editar(request,cedula_ciudadania):
    estudiante = get_object_or_404(Estudiante, pk=cedula_ciudadania)
    
    if request.method == 'POST':
        form = FormularioEstudiante(request.POST, instance=estudiante)
        if form.is_valid():
            form.save()
            return redirect('informacion', estudiante.cedula_ciudadania)
    else:
        form = FormularioEstudiante(instance=estudiante)
        
    return render(request, 'estudiantes/editar.html', {'form': form, 'estudiante': estudiante})

def addestudiante(request):
    if request.method=="POST":
        form= FormularioEstudiante(request.POST)
        if form.is_valid():
            form.save()
            return redirect("index")
    else:
        form=FormularioEstudiante()
    return render(request,"estudiantes/registro.html",{"form":form})

def eliminar(request, cedula_ciudadania):
    if request.method == 'POST':
        # Busca el estudiante por cédula
        estudiante = get_object_or_404(Estudiante, cedula_ciudadania=cedula_ciudadania)
        
        # En lugar de eliminar, solo cambiamos su estado a False
        estudiante.activo = False
        estudiante.save()
        
        # Redirige al listado principal
        return redirect('index')
