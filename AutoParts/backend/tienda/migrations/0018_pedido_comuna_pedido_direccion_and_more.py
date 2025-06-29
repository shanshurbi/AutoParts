# Generated by Django 5.0.6 on 2025-06-22 23:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tienda', '0017_carritoitem_precio'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='comuna',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='pedido',
            name='direccion',
            field=models.CharField(blank=True, max_length=225, null=True),
        ),
        migrations.AddField(
            model_name='pedido',
            name='envio_domicilio',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pedido',
            name='region',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='pedido',
            name='retiro_en_tienda',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='perfilusuario',
            name='telefono',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
