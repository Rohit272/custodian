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
    path('policylogoutput/<int:id>', views.policy_log_output, name='policylogoutput'),
]