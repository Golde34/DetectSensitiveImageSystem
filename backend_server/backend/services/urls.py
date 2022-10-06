from django.contrib import admin
from django.urls import path
from services.views import PredictView, RegisterAPI, LoginAPI
from knox import views as knox_views
import services.views as sviews

urlpatterns = [
    path('predict/', PredictView.as_view()),
    path('api/register/', RegisterAPI.as_view(), name='register'),
    path('api/login/', LoginAPI.as_view(), name='login'),
    path('api/logout/', knox_views.LogoutView.as_view(), name='logout'),
    path('api/generateManageAccount/', sviews.GenerateManageAccount.as_view(), name='generatemanageaccount'),
    path('api/getManageAccount/', sviews.GetManageAccount.as_view(), name='getmanageaccount'),
    path('api/deleteManageAccount/', sviews.DeleteManageAccount.as_view(), name='deletemanageaccount'),
    path('api/checkManageAccount/', sviews.CheckManageAccount.as_view(), name='checkmanageaccount'),
    path('api/getAllNotification/', sviews.NotificationViews.as_view(), name='getAllNotification'),
    path('api/getDomainStatistic/', sviews.StatisticView.as_view(), name='getDomainStatistic'),
    path('api/updateChildAccount/', sviews.UpdateChildAccount.as_view(), name='updatechildaccount'),
]
