from django.urls import path

from accounts import views_members as v

urlpatterns = [
    path("", v.member_list),
    path("manage/all/", v.member_list_manage),
    path("me/profile/", v.update_my_profile),
    path("me/avatar/", v.upload_my_avatar),
    path("<int:user_id>/", v.member_detail),
]
