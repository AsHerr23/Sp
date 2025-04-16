"""
URL configuration for StockPred project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.contrib import admin
from django.urls import path
from .views import (
    loginview,
    authenticate_user,
    real_time_stocks,
    stock_recommendations_page,
    stock_prediction_view,
    fetch_stocks,
    stock_detail,
    index,
    stockpred,
    news,
    support,
    submit_ticket
)

urlpatterns = [
    path('', loginview, name="login"),
    path('admin/', admin.site.urls),
    path('index/',index,name="index"),
    path('authenticate/', authenticate_user, name='authenticate'),
    path("home/", real_time_stocks, name="home"),  
    path("main/", stock_recommendations_page, name="main_dashboard"),
    path("api/stock_predictions/", stock_prediction_view, name="stock_prediction"),
    path("stocks/", real_time_stocks, name="real_time_stocks"),
    path("fetch_stocks/", fetch_stocks, name="fetch_stocks"),
    path("stock/<str:symbol>/", stock_detail, name="stock_detail"),
    path("stockpred/", stockpred, name="stockpred"),
    path("news/",news, name ="news"),
    path('support/' ,support, name ="support"),
    path('submit_ticket/', submit_ticket, name='submit_ticket'),

    
  # Dynamic stock lookup # Fetch stock details dynamically
]
