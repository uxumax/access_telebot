from django.core.management.base import BaseCommand
import main.models
import main.workers
# from access_telebot.serveo_tunnel_maker import ServeoTunnelMaker
# import main.bot


class Command(BaseCommand):
    help = "Setup webhook manually"

    def handle(self, *args, **options):
        webhooker = main.workers.TelegramWebhooker
        
        url = webhooker.get_current_webhook_url()
        if url is not None:
            if webhooker.is_webhook_working(url):
                print(
                    f"Webhook url {url} still working"
                )
                return
                
        print(
            f"Webhook url {url} is not working. Make new one..."
        )

        new_url = webhooker.get_new_webhook_url()

        print(
            f"Has been made new webhook {new_url} and saved."
        )