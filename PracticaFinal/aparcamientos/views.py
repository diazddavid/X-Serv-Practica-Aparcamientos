from django.shortcuts import render

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from aparcamientos.models import Parking, Comment, User, Colour, AggregatedParking
from aparcamientos.xmlParser import xmlParser
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.template.loader import get_template
from django.template import Context
from django.contrib.auth.views import logout
from django.contrib.auth import authenticate, login
from django.views.static import serve

import django.contrib.auth.models as modelsAuth
import urllib


def getLenguage(request):
    if request.META['HTTP_ACCEPT_LANGUAGE'].startswith("es"):
        return "spanish"
    else:
        return "english"

def update(request):
    urlToParse = "http://datos.munimadrid.es/portal/site/egob/menuitem.ac6193"
    urlToParse += "3d6ee3c31cae77ae7784f1a5a0/?vgnextoid=00149033f2201410VgnVC"
    urlToParse += "M100000171f5a0aRCRD&format=xml&file=0&filename=202625-0-apar"
    urlToParse += "camientos-publicos&mgmtid=26e6cc885fcd3410VgnVCM1000000b205a0aRCRD&preview=full"
    xmlToParse = urllib.request.urlopen(urlToParse)
    xmlParser(xmlToParse)
    return HttpResponseRedirect("/")

@csrf_exempt
def myLogout(request):
    logout(request)
    return HttpResponseRedirect("/")

@csrf_exempt
def myLogin(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
    return HttpResponseRedirect('/')

@csrf_exempt
def regist(request):
    lenguage = getLenguage(request)
    template = get_template("page/" + lenguage + "/registration.html")
    myContext = Context({'user' : request.user,
                        'ref' : ""})
    if request.method == "GET":
        return HttpResponse(template.render(myContext))
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        try:
            user = modelsAuth.User.objects.get(username = username)
            myContext['NameError'] = True
            return HttpResponse(template.render(myContext))
        except ObjectDoesNotExist:
            user = modelsAuth.User.objects.create_user(username = username, password = password)
            colorObject = Colour.objects.get( colorName = "sinColor" )
            if user is not None:
                newUser = User(user = user, fontSize = 24, colour = colorObject, pageName = "Página de " + username)
                newUser.save()
                changeColor(request, username, "default")  #Para crear css por defecto para el usuario
    return HttpResponseRedirect("/")

def serveAbout(request):
    template = get_template("page/spanish/about.html")
    return HttpResponse(template.render(Context({'user': request.user})))

@csrf_exempt
def parkPage(request, id):
    point = False
    lenguage = getLenguage(request)
    if id.endswith("/+1"):  #Para hacer que id sea numero y poder sacar parking, y saber que hay que sumar un punto
        id = id.split("/")[0]
        point = True
    try:
        id = int(id)
        selectedPark = Parking.objects.get(id = id)
    except ObjectDoesNotExist:
        template = get_template("page/" + lenguage + "/error.html")
        return HttpResponse(template.render(Context({ 'user' : request.user,
          'NotFound' : "Not valid number of parking"})))
    except ValueError:
        template = get_template("page/" + lenguage + "/error.html")
        return HttpResponse(template.render(Context({ 'user' : request.user,
          'NotFound' : "Please use a correct direction"})))
    if request.method == "GET":
        template = get_template("page/" + lenguage + "/parking.html")
        myContext = Context({ 'user' : request.user,
                            'title': selectedPark.name,
                            'parking' : selectedPark,
                            'commentList' : Comment.objects.filter(parking = selectedPark)})
        myContext['cssName'] = request.user.username
        return HttpResponse(template.render(myContext))

    elif request.method == "POST":
        if point:    #Suma un punto
            selectedPark.points +=1
            selectedPark.save()
        else:    #Añade comentario
            newComment = request.POST["comment"]
            comment = Comment(comment = newComment, user = request.user, parking = selectedPark)
            comment.save()
            selectedPark.Ncomments +=1
            selectedPark.save()
        return HttpResponseRedirect("/aparcamientos/id=" + str(id))

def getDistricts():
    districts = []
    for park in Parking.objects.all():
        if park.district in districts:
            continue
        else:
            districts.append(park.district)
    return districts

@csrf_exempt
def allPark(request, onlyAccess):
    if request.META['HTTP_ACCEPT_LANGUAGE'].startswith("es"):
        lenguage = "spanish"
        title = "Todos los aparcamientos"
    else:
        lenguage = "english"
        title = "Every Parkings"
    myContext = Context({ 'user' : request.user,
                            'Title' : title,
                            'ref' : "aparcamientos",
                            'all' : True})
    if onlyAccess == "":
        selectedParkings = Parking.objects.all()
    else:
        selectedParkings = Parking.objects.exclude(access = 0)
        myContext['access'] = True
    myContext['parkings'] = selectedParkings
    myContext['districts'] = getDistricts()
    myContext['cssName'] = request.user.username
    template = get_template("page/" + lenguage + "/serveParkInfo.html")
    return HttpResponse(template.render(myContext))


@csrf_exempt
def home(request, onlyAccess):
    if request.META['HTTP_ACCEPT_LANGUAGE'].startswith("es"):
        lenguage = "spanish"
        title = "5 parkings más comentados"
    else:
        lenguage = "english"
        title = "Top 5 most commented parkings"
    myContext = Context({'user' : request.user,
                            'ref' : "",
                            'Title' : title,
                            'userList' : User.objects.all()})
    if onlyAccess == '':
        selectedParkings = Parking.objects.all()
    else:
        selectedParkings = Parking.objects.exclude(access = 0)
        myContext['access'] = True
    ref = request.get_host()
    topComment = selectedParkings.exclude(Ncomments = 0).order_by('-Ncomments')[:5]  #Obtenido de django girls
    myContext['cssName'] = request.user.username
    myContext['parkings'] = topComment
    template = get_template("page/" + lenguage + "/root.html")
    return HttpResponse(template.render(myContext))

def homeXML(request, onlyAccess):
    if onlyAccess == '':
        selectedParkings = Parking.objects.all()
    else:
        selectedParkings = Parking.objects.exclude(access = 0)
    topComment = selectedParkings.exclude(Ncomments = 0).order_by('-Ncomments')[:5]
    template = get_template("xml/parking.xml")
    return HttpResponse(template.render(Context({ 'top5' : True,
                                    'parkings' : topComment})), content_type='text/xml')

def userXML(request, user, onlyAccess):
    lenguage = getLenguage(request)
    try:
        selectedUser = modelsAuth.User.objects.get(username = user)
    except ObjectDoesNotExist:
        template = get_template("page/" + lenguage + "/error.html")
        return HttpResponse(template.render(Context({ 'user' : request.user,
          'NotFound' : "This user is not register"})))
    parkings = User.objects.get(user = selectedUser).parkings.all()
    if onlyAccess == "/_accesible":
        parkings = parkings.exclude( access = 0)
    template = get_template("xml/parkings.xml")
    return HttpResponse(template.render(Context({ 'user' : request.user,
                                    'parkings' : parkings})), content_type='text/xml')

@csrf_exempt
def district(request, district):
    lenguage = getLenguage(request)
    onlyAccess = ""
    if district.endswith("/_accesible"):
        onlyAccess = district.split("/")[1]
        district = district.split("/")[0]
    try:
        selectedPark = Parking.objects.filter(district = district)
        title = "Parkinds: " + district
        template = get_template("page/" + lenguage + "/serveParkInfo.html")
        myContext = Context({'user' : request.user,
                            'Title' : title})
        ref = ""
        if onlyAccess == "_accesible":
            selectedPark = selectedPark.exclude(access = 0 )
            ref = "distrito/"
            myContext['access'] = True
        myContext['ref'] = ref + district
        myContext['parkings'] = selectedPark
        myContext['districts'] = getDistricts()
        myContext['cssName'] = request.user.username
        return HttpResponse(template.render(myContext))
    except ObjectDoesNotExist:
        template = get_template("page/" + lenguage + "/error.html")
        return HttpResponse(template.render(Context({ 'user' : request.user,
          'NotFound' : "This district is not register"})))


@csrf_exempt
def changeUserValues(user, colorObject,  fontSize):
    selectedUser = modelsAuth.User.objects.get(username = user)
    theUser = User.objects.get(user = selectedUser)
    lines = []
    try:
        oldF = open("templates/page/css/" + user + "templatemo_style.css", 'r')
    except FileNotFoundError:
        oldF = open("templates/page/css/templatemo_style.css", 'r')
    for line in oldF:
        lines.append(line)
    oldF.close()
    theUser.fontSize = fontSize
    theUser.colour = colorObject
    theUser.save()
    newF = open("templates/page/css/" + user + "templatemo_style.css", 'w')
    for line in lines:
        if line.startswith("	background-color:"):
            if colorObject.colorName == "sinColor":
                line = "	background-color: #2a0b04;\n"
            else:
                line = "	background-color: " + colorObject.colorName + ";\n"
        if line.startswith("h2"):   #Cambio valor de h2 porque es el mas habitual
            if fontSize == 0:
                line = "h2 { font-size: 20px; margin: 0 0 20px 0; padding: 0; }\n"
            else:
                line = "h2 { font-size: " + str(fontSize) + "px; margin: 0 0 px 0; padding: 0; }\n"
        newF.write(line)
    newF.close()
    return

@csrf_exempt
def changeSize(request):
    if request.method == "POST":
        newSize = request.POST["newSize"]
        if newSize.isdigit():
            newSize = int(newSize)
            colorObject = User.objects.get(user = request.user).colour
            changeUserValues(request.user.username, colorObject, newSize)
    return HttpResponseRedirect("/" + request.user.username)

def changeColor(request, username, color):
    try:
        selectedUser = modelsAuth.User.objects.get(username = username)
        theUser = User.objects.get(user = selectedUser)
        colorObject = Colour.objects.get( colorName = color)
        oldColor = theUser.colour.colorName
        fontSize = theUser.fontSize
        if not oldColor == color:
            changeUserValues(username, colorObject, fontSize)
        return HttpResponseRedirect("/" + username)
    except ObjectDoesNotExist:
        return HttpResponseRedirect("/")

@csrf_exempt
def addParking(request, user, parking_id):
    try:
        parkToAdd = User.objects.get( aggregatedparking__parking_id = parking_id)
    except ObjectDoesNotExist:
        try:
            parkToAdd = Parking.objects.get( id = parking_id)
            userPage = User.objects.get(user = request.user)
            newAggregated = AggregatedParking(parking = parkToAdd, user = userPage)
            newAggregated.save()
        except ObjectDoesNotExist:
            template = get_template("page/english/error.html")
            return HttpResponse(template.render(Context({ 'user' : request.user,
                                                    'NotFound' : "Parking not found"})))
    return HttpResponseRedirect("/" + user)

@csrf_exempt
def setUserPageName(request, username):
    try:
        selectedUser = modelsAuth.User.objects.get(username = username)
        userPage = User.objects.get(user = selectedUser)
    except ObjectDoesNotExist:
        return HttpResponseRedirect("/")
    if request.method == "POST":
        newName = request.POST["newName"]
        userPage.pageName = newName
        userPage.save()
        return HttpResponseRedirect("/" + username)
    return HttpResponseRedirect("/")

@csrf_exempt
def userPage(request, user, NPage, onlyAccess):
    lenguage = getLenguage(request)
    if user.endswith("/_accesible"):
        onlyAccess = "/_accesible"
        user = user.split("/")[0]
    try:
        template = get_template("page/" + lenguage + "/user.html")
        selectedUser = modelsAuth.User.objects.get(username = user)
        userPage = User.objects.get(user = selectedUser)
    except ObjectDoesNotExist:
        template = get_template("page/" + lenguage + "/error.html")
        return HttpResponse(template.render(Context({ 'user' : request.user,
                                                'NotFound' : "This user is not register"})))
    userParkings = AggregatedParking.objects.filter(user = userPage)
    myContext = Context({ 'Title' : userPage.pageName,
                        'user' : request.user})
    ref = ""
    if onlyAccess == "/_accesible":
        userParkings = userParkings.exclude(parking__access = 0)
        myContext['access'] = True
    if NPage.isdigit():
        NPage = int(NPage)
        ref = "/"
    else:
        NPage = 1
    if len(userParkings) > 5 * NPage:
        nextInterval = 5 * NPage
    else:
        nextInterval = len(userParkings)
    parkings = userParkings[(NPage - 1) * 5: nextInterval]
    myContext['parkings'] = parkings
    myContext['ref'] = ref + user
    myContext['xml'] = True
    myContext['everyColors'] = Colour.objects.all()
    if len(userParkings) > 5 * NPage:
        nextPage = "/" + user + "/" + str(NPage + 1)
        myContext['nextPage'] = nextPage
    if request.user == selectedUser:
        myContext['setNamePage'] = True
        myContext['everyParks'] = Parking.objects.exclude( aggregatedparking__user = userPage )
    myContext['cssName'] = request.user.username
    return HttpResponse(template.render(myContext))
