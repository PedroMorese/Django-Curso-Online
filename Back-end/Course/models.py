from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Course(models.Model):
    """
    Modelo de Curso para la plataforma de educación online.
    
    Representa un curso creado por un profesor que contiene múltiples clases.
    Solo usuarios con rol PROFESOR o ADMIN pueden crear cursos.
    """
    
    NIVEL_CHOICES = [
        ('PRINCIPIANTE', 'Principiante'),
        ('INTERMEDIO', 'Intermedio'),
        ('AVANZADO', 'Avanzado'),
    ]
    
    # Información básica del curso
    titulo = models.CharField(max_length=255, verbose_name="Título del Curso")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    imagen_portada = models.URLField(max_length=500, blank=True, null=True, verbose_name="URL de Imagen de Portada")
    
    # Relación con el profesor creador
    profesor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cursos_creados',
        verbose_name="Profesor"
    )
    
    # Metadata del curso
    fecha_creacion = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    publicado = models.BooleanField(default=False, verbose_name="Publicado")
    nivel = models.CharField(
        max_length=20,
        choices=NIVEL_CHOICES,
        default='PRINCIPIANTE',
        verbose_name="Nivel"
    )
    duracion_estimada = models.IntegerField(
        blank=True,
        null=True,
        help_text="Duración estimada en minutos",
        verbose_name="Duración Estimada (min)"
    )
    
    class Meta:
        db_table = 'curso'
        app_label = 'course_app'
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['profesor']),
            models.Index(fields=['publicado']),
            models.Index(fields=['-fecha_creacion']),
        ]
    
    def __str__(self):
        return f"{self.titulo} - {self.profesor.email if hasattr(self.profesor, 'email') else self.profesor.username}"
    
    @property
    def total_clases(self):
        """Retorna el número total de clases asociadas a este curso"""
        return self.clases.count()
    
    @property
    def esta_publicado(self):
        """Verifica si el curso está publicado"""
        return self.publicado
    
    def publicar(self):
        """Publica el curso"""
        self.publicado = True
        self.save(update_fields=['publicado'])
    
    def despublicar(self):
        """Despublica el curso"""
        self.publicado = False
        self.save(update_fields=['publicado'])
