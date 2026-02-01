from django.db import models

class Class(models.Model):
    """
    Modelo de Clase/Lección dentro de un curso.
    """
    curso = models.ForeignKey(
        'course_app.Course', 
        on_delete=models.CASCADE, 
        related_name='clases',
        verbose_name="Curso"
    )
    titulo = models.CharField(max_length=255, verbose_name="Título de la Clase")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    orden = models.PositiveIntegerField(default=0, verbose_name="Orden")
    
    # Recursos de la clase
    video_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="URL de Video")
    imagen_portada = models.URLField(max_length=500, blank=True, null=True, verbose_name="Miniatura de Clase")
    
    # Metadata
    duracion_estimada = models.IntegerField(default=0, help_text="Duración en minutos")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'clase'
        verbose_name = 'Clase'
        verbose_name_plural = 'Clases'
        ordering = ['orden']
        app_label = 'class_app'

    def __str__(self):
        return f"{self.curso.titulo} - {self.titulo}"
