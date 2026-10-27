from django.contrib.auth.models import User, Group

# 1. Asegurar que los grupos existan
grupo_super, _ = Group.objects.get_or_create(name="Super")
grupo_medio, _ = Group.objects.get_or_create(name="Medio")
grupo_consulta, _ = Group.objects.get_or_create(name="Consulta")

# 2. Al superusuario existente "Administrador" solo le asignamos el grupo Super (sin tocar su contraseña)
try:
    admin_user = User.objects.get(username='Administrador')
    admin_user.groups.add(grupo_super)
    print("Grupo 'Super' asignado al superusuario 'Administrador'.")
except User.DoesNotExist:
    print("El usuario 'Administrador' no existe.")

# 3. Crear o actualizar el usuario: admin (Grupo Medio, clave: prueba)
admin_medio, created = User.objects.get_or_create(username='admin')
admin_medio.set_password('prueba')
admin_medio.is_staff = True  # Para que pueda entrar al panel de administración si lo requiere
admin_medio.save()
admin_medio.groups.set([grupo_medio])
print(f"Usuario 'admin' {'creado' if created else 'actualizado'} en grupo 'Medio'.")

# 4. Crear o actualizar el usuario: modprueba (Grupo Consulta, clave: prueba)
user_consulta, created = User.objects.get_or_create(username='modprueba')
user_consulta.set_password('prueba')
user_consulta.save()
user_consulta.groups.set([grupo_consulta])
print(f"Usuario 'modprueba' {'creado' if created else 'actualizado'} en grupo 'Consulta'.")