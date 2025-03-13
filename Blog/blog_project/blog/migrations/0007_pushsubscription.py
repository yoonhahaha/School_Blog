# Generated manually for web push notifications

from django.conf import settings
import django.utils.timezone
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('blog', '0006_notification'),
    ]

    operations = [
        migrations.CreateModel(
            name='PushSubscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subscription_info', models.JSONField(verbose_name='구독 정보')),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='생성일')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='push_subscriptions', to=settings.AUTH_USER_MODEL, verbose_name='사용자')),
            ],
            options={
                'verbose_name': '푸시 구독',
                'verbose_name_plural': '푸시 구독',
            },
        ),
    ]