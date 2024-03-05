import typing
import os
import re
from subprocess import Popen, PIPE


class MessageToTranslateParser:
    
    @classmethod
    def parse(cls) -> typing.List[str]:
        collected_strings = []
        for dirpath, filename in cls._get_filenames():
            file_path = os.path.join(dirpath, filename)
            strings = cls._parse_file(file_path)
            collected_strings.extend(strings)
        # Удаление дубликатов
        unique_msgids = list(set(collected_strings))
        return unique_msgids
    
    def _get_filenames() -> typing.List[str]:
        files = []
        for dirpath, dirnames, filenames in os.walk('.'):
            for filename in filenames:
                if filename.endswith('.py'):
                    files.append(
                        (dirpath, filename)
                    )
        return files
    
    @classmethod
    def _parse_file(cls, file_path: str):
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
            raise Exception(
                "Error while using xgettext\n",
                f"{errors.decode('utf-8')}" 
            )
        msgstr_list = cls._parse_msgstr(output)
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


    
