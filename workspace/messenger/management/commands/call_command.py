from django.core.management.base import BaseCommand, CommandError
from messenger.routers import build_command_reply
import main.models


class Command(BaseCommand):
    help = 'Call command reply straigh way for debugging'

    def add_arguments(self, parser):
        parser.add_argument('customer_id', type=int, help='ID of customer that send to')
        parser.add_argument('reply_name', type=str, help='Name of ReplyBuilder')

    def handle(self, *args, **options):
        _customer_id = options['customer_id']
        
        customer = self._get_customer(_customer_id)
        reply_name = options['reply_name']
        
        build_command_reply(
            customer,
            reply_name=reply_name,
        )

        print("Callback Reply has been called")


    @staticmethod
    def _get_customer(customer_id):
        return main.models.Customer.objects.get(pk=customer_id)


