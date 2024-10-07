# Workers

## Webhook Tunneler
`workspace/main/workers/webhook_tunneler.py`
This worker manages a Telegram bot webhook using either a static domain or a dynamically created Serveo tunnel. It includes a worker that periodically checks the webhook status and restarts it if necessary.
- Setting up the webhook: The worker determines the webhook type and sets up the webhook URL with the Telegram bot.
- Periodic checking: The worker periodically checks if the webhook is working.
- Restarting the webhook: If the webhook is not working, the worker restarts it by creating a new tunnel (if using Serveo) and setting up the webhook again.

## Tron Transaction Checker
`workspace/cashier/workers/tron_transaction_checker.py`
The primary purpose of this worker is to automate the process of verifying Tron cryptocurrency payments for invoices. It periodically checks the blockchain for transactions related to invoices and updates their status based on the number of confirmations. This ensures that invoices are marked as paid only after the transactions have been sufficiently confirmed on the Tron network.
- Automated Transaction Checking: The worker runs periodically, eliminating the need for manual intervention.
- Confirmation Tracking: It tracks the number of confirmations for each transaction, ensuring that payments are only considered valid after a sufficient number of confirmations.
- Invoice Status Updates: It automatically updates the status of invoices based on the confirmation status of their associated transactions.

## Invoice Expire Checker
`workspace/cashier/workers/invoice_expire_checker.py`
This worker ensures that expired invoices are handled appropriately, preventing them from cluttering the system and potentially leading to inaccurate financial records.
- Building Invoices: Invoices related to building payments. These are deleted if their expire_date is in the past.
- Crypto Invoices: Invoices paid with cryptocurrency. These are marked as "EXPIRED" if their expire_date is in the past and their status is "PAYING".

## Invoice Confirm Checker
`workspace/cashier/workers/invoice_confirm_checker.py`
This worker checks for cryptocurrency payments and sends messages to users when their payments are confirmed.
- Checking Payments: The worker looks for cryptocurrency payments that have been marked as "CONFIRMED".
- Sending Messages: When a confirmed payment is found, the worker sends a message to the user who made the payment. This message likely contains information about how to access something they purchased.

## Customer Access Revoker
`workspace/accesser/workers/customer_access_revoker.py`
This worker ensures that expired accesses are handled automatically, preventing unauthorized access to Telegram groups. The worker periodically checks for expired customer accesses in the system. When it finds an expired access, it:
- Revokes the access: Removes the customer from the relevant Telegram chat groups.
- Marks the access as inactive: Updates the database to reflect the access revocation.
- Notifies the customer: Sends a notification to the customer informing them about the revoked access.

## Chat Updater
`workspace/accesser/workers/chat_updater.py`
This worker periodically checks if the titles of Telegram chats stored in the database match the actual titles on Telegram. This ensures that the database remains accurate and up-to-date with the latest Telegram chat information. It does this by:
- Fetching all chats from the database.
- Retrieving the chat information from Telegram using the telebot library.
- Comparing the titles. If they differ, the database entry is updated with the correct title.
- Deleting chat entries from the database if the bot is no longer subscribed to the chat.

# Commands

## Accesser
- `get_chat_info <chat_id>` - Retrieves all available information about a specified chat
- `ban_chat_member <chat_id> <user_id>` - Ban chat memeber with his invite links
- `unban_chat_member <chat_id> <user_id>` - Unban chat member and his invite links (do nothing if not banned)

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
