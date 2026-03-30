from django.core.management.base import BaseCommand
from bloom.models import Banner

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        Banner.objects.filter(page="furniture").update(image="banners/furniture.jpg")
        Banner.objects.filter(page="bath").update(image="banners/accessories.jpg")
        Banner.objects.filter(page="walldecor").update(image="banners/wall.jpg")
        Banner.objects.filter(page="kitchen").update(image="banners/kitchen.jpg")
        Banner.objects.filter(page="lighting").update(image="banners/light.jpg")
        self.stdout.write("Banners fixed!")