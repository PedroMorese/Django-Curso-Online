import uuid
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_app', '0002_course_pdf_adjuntos'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_emision', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Fecha de Emisión')),
                ('codigo_verificacion', models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='Código de Verificación')),
                ('curso', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='certificados',
                    to='course_app.course',
                    verbose_name='Curso',
                )),
                ('usuario', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='certificados',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Usuario',
                )),
            ],
            options={
                'verbose_name': 'Certificado',
                'verbose_name_plural': 'Certificados',
                'db_table': 'certificado',
                'unique_together': {('usuario', 'curso')},
            },
        ),
    ]
