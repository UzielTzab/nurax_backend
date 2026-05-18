from django.db import migrations, models


def populate_sale_number(apps, schema_editor):
    Sale = apps.get_model('sales', 'Sale')
    store_ids = (
        Sale.objects.order_by()
        .values_list('store_id', flat=True)
        .distinct()
    )

    for store_id in store_ids:
        sales = Sale.objects.filter(store_id=store_id).order_by('created_at', 'id')
        for index, sale in enumerate(sales, start=1):
            sale.sale_number = index
            sale.save(update_fields=['sale_number'])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0004_sale_sale_type_salepayment_cashier_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='sale_number',
            field=models.PositiveBigIntegerField(
                blank=True,
                db_index=True,
                help_text='Folio incremental visible de la venta (por tienda)',
                null=True,
            ),
        ),
        migrations.RunPython(populate_sale_number, noop_reverse),
        migrations.AlterField(
            model_name='sale',
            name='sale_number',
            field=models.PositiveBigIntegerField(
                db_index=True,
                help_text='Folio incremental visible de la venta (por tienda)',
            ),
        ),
        migrations.AddConstraint(
            model_name='sale',
            constraint=models.UniqueConstraint(
                fields=('store', 'sale_number'),
                name='sale_unique_number_per_store',
            ),
        ),
    ]
