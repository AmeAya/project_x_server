from django.urls import path
from .views import *


urlpatterns = [
    path('records_detail/<int:record_id>', RecordsDetailView.as_view()),
    path('phone', PhoneConfirmationApiView.as_view()),
    path('phone/reg', RegistrationApiView.as_view()),
    path('this_user_detail', UserSelfApiView.as_view()),
    path('all_user_detail', UserApiView.as_view()),
    path('records', RecordsApiView.as_view()),
    path('logout', LogOutView.as_view()),
    path('object_blocks/<int:object_id>', ObjectBlockView.as_view()),
    path('mark_materials/<int:material_id>', MarkMaterialView.as_view()),
    path('object', ObjectApiView.as_view()),
    path('material', MaterialViewSets.as_view()),
    path('mark', MarkViewSets.as_view()),
    path('block', BlockViewSets.as_view()),
    path('floor', FloorApiView.as_view()),
    path('constructive', ConstructiveViewSets.as_view()),
    path('unit', UnitViewSets.as_view()),
    path('provider', ProviderViewSets.as_view()),
    path('position', PositionApiView.as_view()),
    path('records/download', download_file),
]
