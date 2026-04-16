from django.shortcuts import render
from .data import products


def product_list(request):
    return render(request, 'products/product_list.html', {
        'products': products,
    })
