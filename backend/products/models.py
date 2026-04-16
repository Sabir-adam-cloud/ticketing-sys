from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=250, verbose_name='Nom')
    description = models.TextField(verbose_name='Description')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Prix')
    stock = models.PositiveIntegerField(default=0, verbose_name='quantité en stock')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products', verbose_name='catégorie')
    image = models.ImageField(null=True, upload_to='products/', verbose_name='Image')

    def __str__(self):
        return self.name
