from django.urls import path

from tickets import views as v

urlpatterns = [
    path("", v.request_root),
    # Маршрут откликов идёт до <int:request_id>, иначе "responses"
    # попробует разобраться как число и вернёт 404
    path("responses/<int:reply_id>/", v.decide_reply),
    path("<int:request_id>/", v.request_detail),
    path("<int:request_id>/status/", v.update_status),
    path("<int:request_id>/responses/", v.create_reply),
    path("<int:request_id>/assignee/<int:member_id>/", v.assign_member),
]
