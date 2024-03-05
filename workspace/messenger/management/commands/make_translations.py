from django.core.management.base import BaseCommand, CommandError
import typing
from django.db import transaction
from django.db.utils import IntegrityError

from messenger.models import Translation
from .utils import MessageToTranslateParser


class Command(BaseCommand):
    help = 'Update bot message translations; set inactive translations'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'translation_name',
            type=str, 
            help='Name for translation'
        )
        parser.add_argument(
            '--delete-old-translations',  # Use double dashes for optional arguments
            action='store_true',  # This means if the flag is specified, the value is True, otherwise False
            help='Remove old translations with the same name before creating a new one',
            dest='delete_old_transaltions',  # Corrected the destination variable name to match your code usage
        )   

    def handle(self, *args, **options):
        self.translation_name = options["translation_name"]
        delete_old_transaltions = options["delete_old_transaltions"]

        if delete_old_transaltions:
            self._delete_old_translation_with_same_name()

        with transaction.atomic():
            self.parsed_texts = self._parse_all_text_for_translate()
            self._set_inactive_translations()
            print("Making empty translations...")
            self._create_new_translations()

        self.stdout.write(
            self.style.SUCCESS(
                f"Translation {self.translation_name} has been made" 
            )
        )

    def _delete_old_translation_with_same_name(self):
        name = self.translation_name
        Translation.objects.filter(
            name=name                                                                
        ).delete()
        print(
            f"Old translation with name {name} has been deleted"
        )
    
    def _set_inactive_translations(self):
        translations = Translation.objects.filter(
            name=self.translation_name,
            active=True
        ).all()
        for translation in translations:
            if translation.from_text not in self.parsed_texts:
                print(
                    f"Translation {translation} not using in app/replies.py. "
                    "Please remove if no need anymore"
                )
                translation.active = False
                translation.save()

    def _create_new_translations(self):
        for text in self.parsed_texts:
            if self._is_translation_already_exists(text):
                continue
            self._create_empty_translation(text)

    def _is_translation_already_exists(self, text: str):
        return Translation.objects.filter(
            name=self.translation_name,
            from_text=text
        ).exists()

    def _create_empty_translation(self, text: str):
        try:
            Translation.objects.create(
                name=self.translation_name,
                from_text=text,
            )
        except IntegrityError as error:
            raise CommandError(
                f"{error}\n"
                "Check admin messenger.Translations"
            )
                                
    def _parse_all_text_for_translate(self) -> typing.List[str]:
        return MessageToTranslateParser.parse()
        
