from django.urls import path
from django.urls.conf import include
from . import views
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

router = routers.DefaultRouter()
#router.register(r'users', api_views.UserSetApi)
router.register(r'groups', views.GroupSetApi)
router.register(r'links', views.LinkSetApi)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/api-token-auth/', obtain_auth_token),
    path('', views.HomeView.as_view(), name='main'),
    path('account/', views.AccountView.as_view(), name='cabinet'),
    path('account/register/', views.RegisterView.as_view(), name='register'),
    path('account/login/', views.LoginView.as_view(), name='login'),
    path('account/logout/', views.LogoutView.as_view(), name='logout'),
    path('account/links/', views.LinksView.as_view(), name='links'),
    path('account/links/create', views.LinkCreateView.as_view(), name='create_link'),
    path('<str:link>/', views.RedirectToView.as_view(), name='redirect'),
    path('<str:link>/delete/', views.DeleteRedirectView.as_view(), name='redirect_delete')
]