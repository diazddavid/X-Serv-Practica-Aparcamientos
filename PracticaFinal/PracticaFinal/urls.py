"""PracticaFinal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from aparcamientos import views
from django.contrib.auth.views import login
from django.views.static import serve

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^updateParking', views.update, name = "Update Parking info"),
    url(r'^myLogin', views.myLogin),
    url(r'^logout', views.myLogout),
    url(r'^registro', views.regist),
    url(r'^about', views.serveAbout),

    # No usan view de aparcamientos.view, si no de views.static de django
    url(r'^css/(.*templatemo_style.css)$', serve, {'document_root': 'templates/page/css'}),
    url(r'^css/images/(.+)', serve, {'document_root': 'templates/page/images'}, name = "Serve Images"),
    url(r'^js/(.+)', serve, {'document_root': 'templates/page/js'}, name = "Serve javascript"), # JS visto en http://librosweb.es/libro/javascript/capitulo_1/como_incluir_javascript_en_documentos_xhtml.html

    url(r'^aparcamientos/id=(.+)', views.parkPage, name = "Page of each parking"),
    url(r'^aparcamientos(.*)', views.allPark, name = "All parkings"),

    url(r'^()$', views.home, name = "Home"),
    url(r'^(_accesible)$', views.home, name = "Home accesible"),
    
    url(r'^xml/top5(.*)$', views.homeXML, name = "Home Xml"),
    url(r'^(.+)/xml(.*)', views.userXML, name = "User Xml"),

    url(r'^distrito/(.*)', views.district, name = "Only district"),

    #Páginas Usuarios
    url(r'^changeFontSize/', views.changeSize, name = "Change the font size"),
    url(r'^changeColor/(.*)/(.*)', views.changeColor, name = "Change the background color"),
    url(r'^addPark/(.*)/(.*)', views.addParking, name = "Add parkings to a user page"),
    url(r'^setUserPage/(.*)', views.setUserPageName, name = "User Xml"),
    url(r'^(.+)/([0-9]+)(.*)', views.userPage, name = "User Page for more Parkings"),
    url(r'^(.+)()(.*)$', views.userPage, name = "User Page"),
]
