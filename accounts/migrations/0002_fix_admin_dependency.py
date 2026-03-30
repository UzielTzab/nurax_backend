# Generated manually to fix migration order inconsistency in production
# Issue: admin.0001_initial was applied before accounts.0001_initial
# This empty migration ensures admin executes first, resolving the dependency

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('admin', '0001_initial'),  # ← Force admin to execute before subsequent migrations
    ]

    operations = [
        # No schema changes - this is a dependency fix only
    ]
