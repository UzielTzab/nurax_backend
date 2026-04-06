# Generated migration for Client.active field
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_avatar_url_user_name_user_role'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    """
                    DO $$ 
                    BEGIN
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                        WHERE table_name = 'client' AND column_name = 'active') THEN
                            ALTER TABLE "client" ADD COLUMN "active" boolean NOT NULL DEFAULT true;
                        END IF;
                    END $$;
                    """,
                    reverse_sql="-- Reverse not needed"
                )
            ],
            state_operations=[
                migrations.AddField(
                    model_name='client',
                    name='active',
                    field=models.BooleanField(default=True, help_text='Estado del cliente'),
                ),
            ],
        ),
    ]
