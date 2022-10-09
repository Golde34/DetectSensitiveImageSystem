from django.contrib import admin
from django.urls import path
from services.views import PredictView, RegisterAPI, LoginAPI
from knox import views as knox_views
import services.views as sviews

urlpatterns = [
    path('predict/', PredictView.as_view()),
    path('register/', RegisterAPI.as_view(), name='register'),
    path('login/', LoginAPI.as_view(), name='login'),
    path('logout/', knox_views.LogoutView.as_view(), name='logout'),
    path('generateManageAccount/', sviews.GenerateManageAccount.as_view(), name='generatemanageaccount'),
    path('getManageAccount/', sviews.GetManageAccount.as_view(), name='getmanageaccount'),
    path('deleteManageAccount/', sviews.DeleteManageAccount.as_view(), name='deletemanageaccount'),
    path('checkManageAccount/', sviews.CheckManageAccount.as_view(), name='checkmanageaccount'),
    path('getAllNotification/', sviews.NotificationViews.as_view(), name='getAllNotification'),
    path('getDomainStatistic/', sviews.StatisticView.as_view(), name='getDomainStatistic'),
    path('updateChildAccount/', sviews.UpdateChildAccount.as_view(), name='updatechildaccount'),
]
