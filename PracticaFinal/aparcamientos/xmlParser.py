from aparcamientos.models import Parking
from django.views.decorators.csrf import csrf_exempt
import xml.etree.ElementTree as ET

@csrf_exempt
def xmlParser(xmlToParse):
    tree = ET.parse(xmlToParse)
    contenidos = tree.getroot()
    for contenido in contenidos.findall('contenido'):
        for atributos in contenido.findall('atributos'):
            for atributo in atributos.findall('atributo'):
                if atributo.get('nombre') == "NOMBRE":
                    name = atributo.text
                    continue
                if atributo.get('nombre') == "DESCRIPCION":
                    descrip = atributo.text
                    continue
                if atributo.get('nombre') == "ACCESIBILIDAD":
                    access = atributo.text
                    continue
                if atributo.get('nombre') == "CONTENT-URL":
                    url = atributo.text
                    continue
                if atributo.get('nombre') == "LOCALIZACION":
                    for subAtributo in atributo.findall('atributo'):
                        if subAtributo.get('nombre') == "NOMBRE-VIA":
                            address = subAtributo.text
                            continue
                        if subAtributo.get('nombre') == "CLASE-VIAL":
                            address += ", "
                            address += subAtributo.text
                            continue
                        if subAtributo.get('nombre') == "NUM":
                            address += ", "
                            address += subAtributo.text
                            continue
                        if subAtributo.get('nombre') == "LOCALIDAD":
                            city = subAtributo.text
                            continue
                        if subAtributo.get('nombre') == "BARRIO":
                            neighborhood = subAtributo.text
                            continue
                        if subAtributo.get('nombre') == "DISTRITO":
                            district = subAtributo.text
                            continue
                        if subAtributo.get('nombre') == "LATITUD":
                            latitude = subAtributo.text
                            continue
                        if subAtributo.get('nombre') == "LONGITUD":
                            longitude = subAtributo.text
                            continue
                    continue
                if atributo.get('nombre') == "DATOSCONTACTOS":
                    email = "No proporcionado"
                    tlf = "No proporcionado"
                    for subAtributo in atributo.findall('atributo'):
                        if subAtributo.get('nombre') == "TELEFONO":
                            tlf = subAtributo.text
                            continue
                        if subAtributo.get('nombre') == "EMAIL":
                            email = subAtributo.text
                            continue
                    continue
            parking = Parking(name = name, neighborhood = neighborhood, district = district, email = email,
                                address = address, tlf = tlf, city = city, latitude = latitude, longitude = longitude,
                                url = url, Ncomments = 0, access = access, points = 0, descrip = descrip)
            parking.save()
