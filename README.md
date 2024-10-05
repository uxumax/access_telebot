
# Commands

## Accesser
- `get_chat_info <chat_id>` - Retrieves all available information about a specified chat
- `kick_chat_member <chat_id> <user_id>` - Kick member

## Main
- `generate_field_encryption_key` - 
- `run_all_workers` -
- `run_worker <app_name> <worker_filename_py>` - 
- `setup_webhook` - 
- `workers_stat` -

## Messenger
- `call_command <customer_id> <reply_name>` - Call command reply straigh way for debugging
- `call_inline_reply <customer_id> <app_name> <reply_name> <args_line>` - Call callback reply straigh way for debugging
- `export_export <translation_name>` - Export translations to a JSON file in a specific format
- `import_translation <translation_name>` - Import translations from a JSON file
- `make_translations <translation_name> [--delete_old_transaltions]` - Update bot message translations; set inactive translations
- `skip_bot_upodates` - Clears all pending updates for the Telegram bot
