from tabnanny import verbose
from django.db import models
from .publisher import Publisher
from .author import Author

class Book(models.Model):
    title = models.CharField(max_length=100, verbose_name='書名') #max_length 最多只可以輸入100個字，verbose_name 是顯示在界面的中文名字
    authors = models.ManyToManyField(Author, related_name='books',verbose_name='作者', blank=True, null=True)
    price = models.IntegerField(verbose_name='價格')
    stock = models.IntegerField(default=0, verbose_name='庫存') #default=0 是預設值，如果沒有輸入就是0
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, related_name='books', verbose_name='出版社', null=True, blank=True)

    class Meta:
        verbose_name = '書本資訊'
        verbose_name_plural = '書本資訊'

    def __str__(self):
        return self.title

