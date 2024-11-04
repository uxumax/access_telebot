# Commands

You can execute Django management commands (`python3 manage.py`) directly from the Docker host without needing to access the web container's shell. Simply use the script `docker/manage.sh <command>`. For example:

```bash
docker/manage.sh generate_field_encryption_key
```

## Accesser
- `get_chat_info <chat_id>` - Retrieves all available information about a specified chat
- `ban_chat_member <chat_id> <user_id>` - Ban chat memeber with his invite links
- `unban_chat_member <chat_id> <user_id>` - Unban chat member and his invite links (do nothing if not banned)

## Main
- `generate_field_encryption_key` - Generate correct FIELD_ENCRYPTION_KEY from .env config
- `run_all_workers` - System command not for run manually
- `run_worker <app_name> <worker_filename_py>` -  Debug command not for dev 
- `workers_stat` - Debug commad

## Messenger
- `make_translations <translation_name> [--delete_old_transaltions]` - Update bot message translations; set inactive translations
- `call_command <customer_id> <reply_name>` - Call command reply straigh way for debugging
- `call_inline_reply <customer_id> <app_name> <reply_name> <args_line>` - Call callback reply straigh way for debugging
- `export_export <translation_name>` - Export translations to a JSON file in a specific format
- `import_translation <translation_name>` - Import translations from a JSON file
