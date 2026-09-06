from django.db import models

class Estudiante(models.Model):
	cedula_ciudadania= models.CharField(max_length=15, primary_key=True)
	nombre=models.CharField(max_length=30)
	tipocc=models.CharField(max_length=20)
	rdoc = models.BooleanField(default=False)
	programa=models.CharField(max_length=30)
	codcarpeta=models.CharField(max_length=15)
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
	codcarpeta=models.IntegerField(default=0,primary_key=True)
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

	def str(self):
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
	