from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0015_alter_user_usertype'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupBuyCoupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num', models.IntegerField()),
                ('cost', models.FloatField(default=0.0)),
                ('code', models.CharField(max_length=20, unique=True)),
                ('status', models.IntegerField(default=0)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('used_at', models.DateTimeField(blank=True, null=True)),
                ('food', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.food')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.user')),
            ],
        ),
    ]
