from django.core.management.base import BaseCommand
import os
from django.db import transaction
import json
from messenger.models import Translation


class Command(BaseCommand):
    help = 'Import translations from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            'translation_name',
            type=str,
            help='Name for the translation'
        )
        parser.add_argument(
            'file_path',
            type=str,
            help='Path to the JSON file containing the translations'
        )

    def handle(self, *args, **options):
        self._set_import_data(options)

        if not self._validate_file_path():
            self.stdout.write(self.style.ERROR(f"File {self.file_path} does not exist"))
            return

        translations = self._load_translations_from_file()

        if translations:
            self._import_translations(translations)
        else:
            self.stdout.write(self.style.ERROR("No translations found in the file"))

    def _set_import_data(self, options):
        self.translation_name = options["translation_name"]
        self.file_path = options["file_path"]

    def _validate_file_path(self):
        return os.path.exists(self.file_path)

    def _load_translations_from_file(self):
        with open(self.file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def _import_translations(self, translations):
        with transaction.atomic():
            for trans_id, (from_text, to_text) in translations.items():
                try:
                    translation = Translation.objects.get(id=trans_id, name=self.translation_name)
                    translation.from_text = from_text
                    translation.to_text = to_text
                    translation.save()
                    self.stdout.write(self.style.SUCCESS(f"Successfully updated translation {trans_id}"))
                except Translation.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Translation {trans_id} not found and was skipped"))

