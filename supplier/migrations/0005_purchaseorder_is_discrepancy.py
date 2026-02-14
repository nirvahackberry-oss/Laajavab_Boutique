from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supplier', '0004_purchaseorder_purchaseorderitem_secureorderlink_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseorder',
            name='is_discrepancy',
            field=models.BooleanField(default=False),
        ),
    ]
