from django.urls import path
from .views import dialog_window_view

app_name = "messenger"
urlpatterns = [
    path(
        'dialog_window/<int:chat_id>/',
        dialog_window_view, 
        name='dialog_window_view'
    ),
]
