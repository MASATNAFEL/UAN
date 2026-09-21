from django.db import models

class Estudiante(models.Model):
	"""
    Representa un estudiante registrado en el sistema.

    Los estudiantes no se eliminan físicamente de la base de datos.
    El campo 'activo' permite realizar una eliminación lógica:
    los registros inactivos dejan de mostrarse en la plataforma,
    pero permanecen disponibles para administración desde Django Admin.
    """
	cedula_ciudadania= models.CharField(max_length=15, primary_key=True)
	nombre=models.CharField(max_length=30)
	tipocc=models.CharField(max_length=20)
	rdoc = models.BooleanField(default=False)
	programa=models.CharField(max_length=30)
	contacto=models.CharField(max_length=15)
	email=models.EmailField(blank=True, null=True)
	fecha_registro = models.DateTimeField(auto_now_add=True)
	fecha_actualizacion = models.DateTimeField(auto_now=True)
	activo = models.BooleanField(default=True)

	def __str__(self):
    		return f"{self.nombre} - {self.cedula_ciudadania}"

	def get_fields(self):
		ocultar = ["fecha_registro", "fecha_actualizacion", "activo"]
		return [
            {
                'name': field.name,
                'verbose_name': field.verbose_name.title(),
                'value': getattr(self, field.name),
            }
            for field in self._meta.fields
            if field.name not in ocultar
        ]
class Carpeta(models.Model):
	"""
    Representa la carpeta documental asociada a un estudiante.

    Una carpeta debe pertenecer a un estudiante existente. La relación
    utiliza PROTECT para evitar la eliminación física de un estudiante
    cuando existen carpetas asociadas a él.
    """
	codcarpeta=models.IntegerField(primary_key=True)
	estudiante=models.ForeignKey(Estudiante, on_delete=models.PROTECT,related_name="carpetas")
	year_start = models.CharField(max_length=4)
	year_end = models.CharField(max_length=4, blank=True, null=True)
	notas = models.BooleanField(default=False)
	mat_sem = models.BooleanField(default=False)
	rec_pago = models.BooleanField(default=False)
	folio = models.IntegerField(default=0)
	modelo = models.BooleanField(default=True)
	observa = models.TextField(blank=True, null=True)
	activo = models.BooleanField(default=True) 
	fecha_registro = models.DateTimeField(auto_now_add=True)
	fecha_actualizacion = models.DateTimeField(auto_now=True)

	def __str__(self):
    		return f"{self.codcarpeta}"
	def get_fields(self):
			ocultar = ["fecha_registro", "fecha_actualizacion", "activo"]
			return [
				{
					'name': field.name,
					'verbose_name': field.verbose_name.title(),
					'value': getattr(self, field.name),
				}
				for field in self._meta.fields
				if field.name not in ocultar
			]
	