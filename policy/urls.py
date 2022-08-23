from django.urls import path
from .import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create, name='create'),
    path('create/addrecord/', views.addrecord, name='addrecord'),
    path('delete/<int:id>', views.delete, name='delete'),
    path('update/<int:id>', views.update, name='update'),
    path('update/updaterecord/<int:id>', views.updaterecord, name='updaterecord'),
    path('execute/<int:id>', views.execute_policy, name='execute'),
    path('output/dir/<int:id>', views.output_dir, name='output_dir'),
    path('output/dir/files/<str:subscription>/<str:directory>', views.output_files, name='output_files'),
    path('output/dir/files/download/<str:subscription>/<str:directory>/<str:filename>/', views.output_download, name='output_download'),
    path('sp/', views.authenticate_sp_form, name='authenticate_sp_form'),
    path('sp/authenticate/', views.authenticate_service_principal, name='authenticate'),
]