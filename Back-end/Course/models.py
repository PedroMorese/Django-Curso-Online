import uuid
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
    pdf_adjuntos = models.TextField(
        blank=True,
        null=True,
        default='[]',
        help_text="Lista de URLs de PDFs adjuntos en formato JSON",
        verbose_name="PDFs Adjuntos"
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


# ─────────────────────────────────────────────────────────────────────────────
# Certificate
# ─────────────────────────────────────────────────────────────────────────────

class Certificate(models.Model):
    """
    Certificado de participación emitido cuando un cliente completa un curso.

    Se emite una sola vez por (usuario, curso). Si el usuario llega a la última
    clase y hace clic en "Complete Course", se crea o recupera el registro.
    """

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='certificados',
        verbose_name='Usuario',
    )
    curso = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='certificados',
        verbose_name='Curso',
    )
    fecha_emision = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de Emisión',
    )
    codigo_verificacion = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        verbose_name='Código de Verificación',
    )

    class Meta:
        db_table = 'certificado'
        app_label = 'course_app'
        verbose_name = 'Certificado'
        verbose_name_plural = 'Certificados'
        # Un usuario solo puede tener un certificado por curso
        unique_together = [('usuario', 'curso')]

    def __str__(self):
        return f'Certificado: {self.usuario} — {self.curso.titulo}'

    @property
    def codigo_display(self):
        """UUID formateado en mayúsculas para mostrarlo en el template."""
        return str(self.codigo_verificacion).upper()


# ─────────────────────────────────────────────────────────────────────────────
# CourseView  —  conteo único de espectadores por curso
# ─────────────────────────────────────────────────────────────────────────────

class CourseView(models.Model):
    """
    Registra que un usuario con membresía activa vio un curso.

    Reglas de negocio:
    - Un solo registro por par (usuario, curso).
    - Solo se crea si el usuario está autenticado Y tiene membresía activa.
    - Se usa get_or_create, por lo que nunca duplica.
    - El profesor puede consultar el total de viewers únicos de sus cursos.
    """

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='curso_views',
        verbose_name='Usuario',
    )
    curso = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='views',
        verbose_name='Curso',
    )
    primera_vista = models.DateTimeField(
        default=timezone.now,
        verbose_name='Primera Visita',
    )

    class Meta:
        db_table = 'course_view'
        app_label = 'course_app'
        verbose_name = 'Vista de Curso'
        verbose_name_plural = 'Vistas de Cursos'
        unique_together = [('usuario', 'curso')]
        indexes = [
            models.Index(fields=['curso']),
            models.Index(fields=['usuario']),
        ]

    def __str__(self):
        return f'{self.usuario.email} → {self.curso.titulo}'
