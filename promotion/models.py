from django.db import models

# Create your models here.
class PromotionCode(models.Model):
  code = models.CharField(verbose_name='プロモーションコード', max_length=7, unique=True)
  discount_amount = models.PositiveIntegerField(verbose_name='割引額')
  is_used = models.BooleanField(verbose_name='使用済み', default=False)
  updated_at = models.DateTimeField(verbose_name='更新日',auto_now=True)

  def __str__(self):
    return f"{self.code} ({self.discount_amount}円引き)"