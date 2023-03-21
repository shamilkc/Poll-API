from django.urls import path
from . import views

urlpatterns = [
    path('',views.routes),
    path('poll/',views.polls_list),
    path('poll/mypolls/',views.list_by_user),
    path('poll/addpolls/',views.polls_add),
    path('poll/editpolls/<int:poll_id>/',views.polls_edit),
    path('poll/deletepolls/<int:poll_id>/',views.polls_delete),
    # path('poll/addchoices/<int:poll_id>/',views.add_choice),
    path('poll/editchoices/<int:poll_id>/',views.edit_choice),
    # path('poll/deletechoices/<int:poll_id>/',views.delete_choice),
    path('poll/vote/<int:poll_id>/',views.poll_vote),
]