from django.core.management.base import BaseCommand
import typing
import os
import json
from messenger.models import Translation

EXPORT_DIR = "export"


class Command(BaseCommand):
    help = 'Export translations to a JSON file in a specific format'

    def add_arguments(self, parser):
        parser.add_argument(
            'translation_name',
            type=str, 
            help='Name for the translation'
        )
    
    def handle(self, *args, **options):
        self._set_transaltions_data(options)
        
        if not self.translations.exists():
            self.stdout.write(
                self.style.ERROR(
                    f"No translations found with name {self.translation_name}"
                )
            )
            return
        
        tdict = self._build_translation_dict()
        self._export_file(tdict)    

    def _set_transaltions_data(self, options):
        self.translation_name = options["translation_name"]
        self.translations = Translation.objects.filter(
            name=self.translation_name
        )
        
    def _build_translation_dict(self):
        # Создание словаря данных в требуемом формате
        # data = {f"Translation.{trans.id}": [trans.from_text, trans.to_text] for trans in translations}
        dict_ = {}
        for translation in self.translations:
            dict_[translation.id] = ( 
                translation.from_text,
                translation.to_text if translation.to_text is not None else ""
            )
        return dict_

    def _export_file(
        self,
        translations: typing.Dict[str, tuple] 
    ):
        os.makedirs(EXPORT_DIR, exist_ok=True)
        file_path = os.path.join(
            EXPORT_DIR,
            f"{self.translation_name}_translation.json"
        )

        # Сохранение данных в JSON файл
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(
                translations, 
                file, 
                ensure_ascii=False, 
                indent=4
            )
        
        self.stdout.write(self.style.SUCCESS(f"Successfully exported translations to {file_path}"))
