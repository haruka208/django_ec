from django.db import models
from cloudinary_storage.storage import MediaCloudinaryStorage

# Create your models here.

class Product(models.Model):
  sku = models.CharField(verbose_name='商品管理コード', max_length=20, unique=True)
  name = models.CharField(verbose_name='商品名', max_length=255)
  price = models.PositiveIntegerField(verbose_name='価格')
  description = models.TextField(verbose_name='商品説明', blank=True)
  image = models.ImageField(verbose_name='イメージ画像', null=True, blank=True, upload_to='products/', storage=MediaCloudinaryStorage)
  stock = models.PositiveIntegerField(verbose_name='在庫', null=True, blank=True)
  created_at = models.DateTimeField(verbose_name='登録日時', auto_now_add=True)

  def __str__(self): # オブジェクトを文字列として表現するときにどう表示するか を決めるもの
    return f'{self.name} / {self.price}円'
  
  class Meta:
    db_table = 'product'
