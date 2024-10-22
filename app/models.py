from django.db import models

from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

ESTADO_OPCIONES = [
    ('POR_HACER', 'Por Hacer'),
    ('EN_PROGRESO', 'En Progreso'),
    ('COMPLETADA', 'Completada'),
]

class Tarea(models.Model):
    
    titulo = models.CharField(max_length=200,null=False,blank=False)#se actualizo null a false igual que blank
    descripcion = models.TextField(null=False, blank=False)#se actualizo blank False 
    criterios_aceptacion = models.TextField(blank=True, null=True)
    prioridad = models.IntegerField(validators=[MinValueValidator(0)])
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_OPCIONES,
        default='POR_HACER',
    )
    esfuerzo_estimado = models.IntegerField(validators=[MinValueValidator(0)])
    responsable = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    sprint_asignado = models.ForeignKey('Sprint', null=True, blank=True, on_delete=models.SET_NULL)
    fecha_creacion = models.DateTimeField(auto_now_add=True,null=False)#se asigno null a false
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    dependencias = models.ManyToManyField('self', symmetrical=False, blank=True)
    bloqueadores = models.TextField(blank=True, null=True)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(prioridad__gte=0), name='prioridad_no_negativa'),
            models.CheckConstraint(check=models.Q(esfuerzo_estimado__gte=0), name='esfuerzo_estimado_no_negativo'),
            models.CheckConstraint(check=models.Q(estado__in=['POR_HACER','EN_PROGRESO','COMPLETADA']), name='estado_valido_tarea'),
        ]

    def __str__(self):
        return self.titulo


class Sprint(models.Model):
    nombre = models.CharField(max_length=200,blank=False,null=False)# se asigno blanck a false igual que null
    objetivo = models.TextField(blank=False, null=False)# se asigno blank a False y null tambien
    fecha_inicio = models.DateField(blank=False,null=False)# se asigno blanck a false igual que null
    fecha_fin = models.DateField(blank=False,null=False)# se asigno blanck a false igual que null
    velocidad = models.IntegerField(validators=[MinValueValidator(0)])
    scrum_master = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='scrum_master')
    equipo_desarrollo = models.ManyToManyField(User, blank=False ,related_name='equipo_desarrollo')#se asigno blank a false
    backlog_sprint = models.ManyToManyField(Tarea, blank=False)#se cambio blank 
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(fecha_fin__gte=models.F('fecha_inicio')), name='fecha_fin_posterior'),
            models.CheckConstraint(check=models.Q(velocidad__gte=0), name='velocidad_no_negativa'),
        ]

    def __str__(self):
        return self.nombre



class Epica(models.Model):
    
    nombre = models.CharField(max_length=200 ,null=False,blank=False)#se actualizo null a false igual que blank
    descripcion = models.TextField(blank=False, null=False)#se actualizo null a false igual que blank
    criterios_aceptacion = models.TextField(blank=True, null=True)
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_OPCIONES,
        default='POR_HACER',
    )
    responsable = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    tareas_asociadas = models.ManyToManyField(Tarea, blank=False)# se cambio blank false 
    esfuerzo_estimado_total = models.IntegerField(validators=[MinValueValidator(0)])
    fecha_inicio = models.DateField(null=False, blank=False)#se cambio null y blank a false
    fecha_fin = models.DateField(null=False, blank=False)#se cambio null y blank a false
    progreso = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    dependencias = models.ManyToManyField('self', symmetrical=False, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(esfuerzo_estimado_total__gte=0), name='esfuerzo_total_no_negativo'),
            models.CheckConstraint(check=models.Q(progreso__gte=0) & models.Q(progreso__lte=1), name='progreso_valido'),
            models.CheckConstraint(check=models.Q(estado__in=['POR_HACER','EN_PROGRESO','COMPLETADA']), name='estado_valido_epica'),
            models.CheckConstraint(check=models.Q(fecha_fin__gte=models.F('fecha_inicio')), name='fecha_fin_posterior_epica'),
        ]

    def __str__(self):
        return self.nombre
