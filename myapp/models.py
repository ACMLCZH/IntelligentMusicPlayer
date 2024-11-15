from django.db import models
# Create your models here.
class Songs(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    duration = models.IntegerField()
    lyrics = models.CharField(max_length=2000)
    url = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = 'Songs'
        verbose_name_plural = verbose_name