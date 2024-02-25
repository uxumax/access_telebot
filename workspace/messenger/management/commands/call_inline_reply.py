from django.core.management.base import BaseCommand, CommandError
from messenger.routers import CallbackInlineRouter, Callback
import main.models


class Command(BaseCommand):
    help = 'Call callback reply straigh way for debugging'

    def add_arguments(self, parser):
        parser.add_argument('customer_id', type=int, help='ID of customer that send to')
        parser.add_argument('app_name', type=str, help='Name of app')
        parser.add_argument('reply_name', type=str, help='Name of ReplyBuilder')
        parser.add_argument(
            'args_line', 
            type=str, 
            nargs='?', 
            default=None, 
            help='Args in one line separated by ":" (optional)'
        )

    def handle(self, *args, **options):
        _customer_id = options['customer_id']
        _args_line = options['args_line']
        
        customer = self._get_customer(_customer_id)
        app_name = options['app_name']
        reply_name = options['reply_name']
        if _args_line is not None:
            args = self._split_args(_args_line)
        
        callback = Callback(
            id=1,
            app_name=app_name,
            reply_name=reply_name,
            args=args,
        )

        CallbackInlineRouter(
            customer, callback
        ).route()

        print("Callback Reply has been called")


    @staticmethod
    def _get_customer(customer_id):
        return main.models.Customer.objects.get(pk=customer_id)

    @staticmethod
    def _split_args(args_line) -> list:
        return args_line.split(":")



