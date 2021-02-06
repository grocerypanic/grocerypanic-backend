# Generated by Django 3.0.12 on 2021-02-06 19:59

import django.core.validators
from django.db import migrations, models
import kitchen.models.validators.transaction


class Migration(migrations.Migration):

  dependencies = [
      ('kitchen', '0002_transaction_20210205_2049'),
  ]

  operations = [
      migrations.AddField(
          model_name='item',
          name='has_partial_quantities',
          field=models.BooleanField(default=False),
      ),
      migrations.AlterField(
          model_name='item',
          name='expired',
          field=models.FloatField(
              default=0,
              validators=[
                  django.core.validators.MinValueValidator(0),
                  django.core.validators.MaxValueValidator(10000)
              ]
          ),
      ),
      migrations.AlterField(
          model_name='item',
          name='next_expiry_quantity',
          field=models.FloatField(
              default=0,
              validators=[
                  django.core.validators.MinValueValidator(0),
                  django.core.validators.MaxValueValidator(10000)
              ]
          ),
      ),
      migrations.AlterField(
          model_name='item',
          name='quantity',
          field=models.FloatField(
              default=0,
              validators=[
                  django.core.validators.MinValueValidator(0),
                  django.core.validators.MaxValueValidator(10000)
              ]
          ),
      ),
      migrations.AlterField(
          model_name='transaction',
          name='quantity',
          field=models.FloatField(
              validators=[
                  kitchen.models.validators.transaction.
                  TransactionQuantityValidator(10000)
              ]
          ),
      ),
      migrations.AlterModelOptions(
          name='shelf',
          options={'verbose_name_plural': 'Shelves'},
      ),
  ]