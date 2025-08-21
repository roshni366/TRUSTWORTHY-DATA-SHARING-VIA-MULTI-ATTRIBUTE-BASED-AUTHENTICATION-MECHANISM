from django.urls import path

from . import views

urlpatterns = [path("index.html", views.index, name="index"),
	       path('AdminLogin.html', views.AdminLogin, name="AdminLogin"), 
	       path('UserLogin.html', views.UserLogin, name="UserLogin"),
	       path('UserLoginAction', views.UserLoginAction, name="UserLoginAction"),	
	       path('AdminLoginAction', views.AdminLoginAction, name="AdminLoginAction"), 
	       path('Register.html', views.Register, name="Register"),
	       path('RegisterAction', views.RegisterAction, name="RegisterAction"),	
	       path('AddOwner.html', views.AddOwner, name="AddOwner"),
	       path('AddOwnerAction', views.AddOwnerAction, name="AddOwnerAction"),
	       path('ViewOwner', views.ViewOwner, name="ViewOwner"),
	       path('DownloadFileDataRequest', views.DownloadFileDataRequest, name="DownloadFileDataRequest"),
	       path('ViewRequester', views.ViewRequester, name="ViewRequester"),
	       path('AccessData', views.AccessData, name="AccessData"),
	       path('Graph', views.Graph, name="Graph"),
]
