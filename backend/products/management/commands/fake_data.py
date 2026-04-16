import random
from django.core.management.base import BaseCommand
from faker import Faker
from products.models import Category, Product


class Command(BaseCommand):
    help = 'Génère les données fictives pour les produits'

    def handle(self, *args, **options):
        faker = Faker('fr_FR')

        categories = []
        for _ in range(5):
            name = faker.word().capitalize()
            slug = faker.slug(name)
            category = Category.objects.create(name=name, slug=slug)
            categories.append(category)
            self.stdout.write(f'Catégorie créée avec succès: {name}')

        for i in range(8):
            Product.objects.create(
                name=faker.sentence(nb_words=4).replace('.', ''),
                description=faker.text(max_nb_chars=450),
                price=faker.random_number(digits=4),
                stock=faker.random_int(min=0, max=100),
                category=random.choice(categories),
            )
            self.stdout.write(f'Produit {i+1} créé avec succès')
