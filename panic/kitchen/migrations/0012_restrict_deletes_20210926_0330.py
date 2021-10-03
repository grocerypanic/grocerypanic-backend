# Generated by Django 3.2.7 on 2021-09-26 18:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

  dependencies = [
      ('kitchen', '0011_alter_item_shelf_20210907_1746'),
  ]

  operations = [
      migrations.AlterField(
          model_name='item',
          name='shelf',
          field=models.ForeignKey(
              blank=True,
              null=True,
              on_delete=django.db.models.deletion.RESTRICT,
              to='kitchen.shelf'
          ),
      ),
      migrations.AlterField(
          model_name='preferredstore',
          name='store',
          field=models.ForeignKey(
              on_delete=django.db.models.deletion.RESTRICT, to='kitchen.store'
          ),
      ),
  ]