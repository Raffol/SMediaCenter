from django.urls import path

from posts import views as v

urlpatterns = [
    path("", v.post_root),
    # Служебные пути идут до <slug>, иначе "manage" будет разобран как слаг
    path("manage/all/", v.post_list_manage),
    path("<int:post_id>/", v.post_manage),
    path("<int:post_id>/cover/", v.post_cover),
    path("<slug:slug>/", v.post_detail_public),
]
