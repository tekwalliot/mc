from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('datareport/', views.data_rep, name='datarep'),
    path('fullreport/', views.full_rep, name='fullrep'),
    path('rwsrajasthan/', views.custlist, name='rwsrj'),
    path('openIds/<Rid>/', views.openId, name='iddb'),
    path('search/', views.search, name='searchid'),
    # path('5hpac/', views.ac5hprep, name='5hprep'),
    # path('3hpac/', views.ac3hprep, name='3hprep'),
    # path('datareport/', views.datarep, name='dailydata'),
    # path('datareport1/', views.datarep1, name='dailydata1'),
    # path('log', views.logoutpage, name='lo'),
    # path('GetInvDaysData/', views.GetInvDaysData, name='apiDayData'),
    # path('GetInvMonthData/', views.GetInvMonthData, name='apiMonthData'),
]