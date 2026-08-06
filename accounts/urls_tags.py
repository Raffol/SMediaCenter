from django.urls import path

from accounts import views_tags as v

urlpatterns = [
    path("", v.tag_list),
    path("manage/", v.tag_list_manage),
    path("my/service-types/", v.my_service_types),
    path("assign/<int:user_id>/", v.assign_tags),
    path("<int:tag_id>/", v.tag_detail),
]
