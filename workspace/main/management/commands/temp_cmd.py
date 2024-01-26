from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Some fast temp cmd"

    def handle(self, *args, **options):
        pass