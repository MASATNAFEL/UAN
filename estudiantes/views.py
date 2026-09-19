from django.http import HttpResponse
from .models import Estudiante,Carpeta
from .forms import FormularioEstudiante, FormularioCarpeta
from django.db.models import Q
from django.shortcuts import get_object_or_404,render,redirect

def index(request):
    lista_Estudiantes = Estudiante.objects.filter(activo=True).order_by("nombre")
    lista_Carpetas = Carpeta.objects.filter(activo=True).order_by("codcarpeta")
    context = {"lista_Estudiantes":lista_Estudiantes, "lista_Carpetas":lista_Carpetas}
    return render(request,"estudiantes/index.html",context)
    
def informacion(request,cedula_ciudadania):
    listado=get_object_or_404(Estudiante,pk=cedula_ciudadania)
    return render(request,"estudiantes/informacion.html", {"listado":listado, "url_borrar":"borrar"})
def inforcarpeta(request,codcarpeta):
    listado=get_object_or_404(Carpeta,pk=codcarpeta)
    return render(request,"estudiantes/informacion.html", {"listado":listado, "url_borrar":"eliminar"})

def editar(request,cedula_ciudadania):
    print(request.method)
    estudiante = get_object_or_404(Estudiante, pk=cedula_ciudadania)

    if request.method =='POST' :
        form = FormularioEstudiante(request.POST, instance=estudiante)
        if form.is_valid():
            form.save()
            return redirect('informacion',estudiante.pk)
    else:
        form = FormularioEstudiante(instance=estudiante)
    return render(request, 'estudiantes/editar.html', {'form': form,'estudiante':estudiante})

def modificar(request,codcarpeta):
    print(request.method)
    carpeta = get_object_or_404(Carpeta, pk=codcarpeta)

    if request.method =='POST' :
        form = FormularioCarpeta(request.POST, instance=carpeta)
        if form.is_valid():
            form.save()
            return redirect('informacion',carpeta.pk)
    else:
        form = FormularioCarpeta(instance=carpeta)
    return render(request, 'estudiantes/editar.html', {'form': form,'carpeta':carpeta})
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

def consultar(request):
    consulta_codcarpeta=request.GET.get("a","")
    resultado=Carpeta.objects.order_by("codcarpeta")

    if consulta_codcarpeta:
        resultado=resultado.filter(Q(codcarpeta__icontains=consulta_codcarpeta))

    context={"consulta_codcarpeta":consulta_codcarpeta,"resultado":resultado}
    return render(request,"estudiantes/buscar.html",context)

def addestudiante(request):
    if request.method=="POST":
        form = FormularioEstudiante(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form=FormularioEstudiante()
    return render(request,"estudiantes/registro.html",{"form":form})
def addcarpeta(request):
    if request.method=="POST":
        form = FormularioCarpeta(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form=FormularioCarpeta()
    return render(request,"estudiantes/registro.html",{"form":form})

def borrar(request, cedula_ciudadania):
    if request.method=="POST":
        estudiante=get_object_or_404(Estudiante,pk=cedula_ciudadania)
        estudiante.activo=False
        estudiante.save()
        return redirect("index")
def eliminar(request, codcarpeta):
    if request.method=="POST":
        carpeta=get_object_or_404(Carpeta,pk=codcarpeta)
        carpeta.activo=False
        carpeta.save()
        return redirect("index")
def prueba(request):
   filtros = [{
            "name": "a",
            "campo": "codcarpeta",
            "label": "Código carpeta",
        },
    ]
   columnas = [
        ("codcarpeta", "Código carpeta"),
        ("activo", "Activo"),
    ]
   for filtro in filtros:
        valor = request.GET.get(filtro["name"], "")

        filtro["value"] = valor

        if valor:
            resultado = resultado.filter(
                **{
                    f'{filtro["campo"]}__icontains': valor
                }
            )
            context = {
        "resultado": resultado,
        "filtros": filtros,
        "columnas": [
            {
                "campo": campo,
                "label": label,
            }
            for campo, label in columnas
        ],
    }
            return render(
        request,
        "estudiantes/consultar.html",
        context
    )
