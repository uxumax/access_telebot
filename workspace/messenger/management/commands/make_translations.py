from django.core.management.base import BaseCommand, CommandError
import typing
from django.db import transaction
from django.db.utils import IntegrityError
from messenger.models import Translation
from subprocess import Popen, PIPE
import os
import re


class Command(BaseCommand):
    help = 'Create new messages translation'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'translation_name',
            type=str, 
            help='Name for translation'
        )
        parser.add_argument(
            '--delete-old-translation',  # Use double dashes for optional arguments
            action='store_true',  # This means if the flag is specified, the value is True, otherwise False
            help='Remove old translation with the same name before creating a new one',
            dest='delete_old_transaltion',  # Corrected the destination variable name to match your code usage
        )   

    def handle(self, *args, **options):
        self.translation_name = options["translation_name"]
        delete_old_transaltion = options["delete_old_transaltion"]

        if delete_old_transaltion:
            self._delete_old_translation_with_same_name()

        with transaction.atomic():
            texts: list = self._parse_all_text_for_translate()
            print("Making empty translations...")
            self._create_translations(texts)

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

    def _create_translations(self, texts: typing.List[str]): 
        for text in texts:
            # print(text)
            self._create_empty_translation(text)

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
        collected_strings = []
        for dirpath, filename in self._get_filenames():
            file_path = os.path.join(dirpath, filename)
            strings = self._parse_file(file_path)
            collected_strings.extend(strings)
        # Удаление дубликатов
        unique_msgids = list(set(collected_strings))
        return unique_msgids

    def _get_filenames(self) -> typing.List[str]:
        files = []
        for dirpath, dirnames, filenames in os.walk('.'):
            for filename in filenames:
                if filename.endswith('.py'):
                    files.append(
                        (dirpath, filename)
                    )
        return files

    def _parse_file(self, file_path: str):
        process = Popen(
            [
                "xgettext", 
                "--language=Python", 
                "--keyword=_:1,2",
                "--from-code=UTF-8", 
                "-o-", 
                file_path,
            ], 
            stdout=PIPE
        )
        output, errors = process.communicate()
        if errors:
            self.stdout.write(errors.decode('utf-8'), self.style.ERROR)
        msgstr_list = self._parse_msgstr(output)
        return msgstr_list

    @classmethod
    def _parse_msgstr(cls, output) -> typing.List[str]:
        parsed_list = []
        if output:
            blocks = re.findall(
                r'msgid\s+((?:".*?"\n?)+)(?=msgstr|\Z)', 
                output.decode('utf-8'), 
                re.DOTALL
            )
            for block in blocks:
                msgstr = cls._clear_msgstr(block)
                if msgstr:
                    parsed_list.append(msgstr)

        return parsed_list
    
    @staticmethod
    def _clear_msgstr(msgstr: str) -> str:
        # Remove leading and trailing quotes
        msgstr = re.sub(r'(?<!\\)"', '', msgstr)
        
        # Remove leading and trailing whitespace
        msgstr = msgstr.strip()
        
        # Replace multiple spaces with a single space
        msgstr = re.sub(r'\s+', ' ', msgstr)
        
        # Normalize line endings to Unix-style (LF) for consistency across different platforms
        msgstr = msgstr.replace("\r\n", "\n").replace("\r", "\n")
        
        return msgstr

