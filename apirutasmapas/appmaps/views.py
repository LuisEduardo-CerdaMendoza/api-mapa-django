from django.shortcuts import render
from django.http import JsonResponse
import json
import requests

api_key = "AIzaSyB-a4eE0pXGufV3vD1rhmZByGSLFvzrUFQ"  # Reemplaza con tu API Key de Google Maps

def index(request):
    return render(request, 'index.html')

def obtener_distancia_y_tiempo(origen, destino, api_key):
    try:
        url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origen}&destinations={destino}&key={api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            if 'rows' in result and len(result['rows']) > 0 and 'elements' in result['rows'][0] and len(result['rows'][0]['elements']) > 0:
                element = result['rows'][0]['elements'][0]
                if 'distance' in element and 'duration' in element:
                    return element['distance']['value'], element['duration']['value']
                else:
                    print(f"Error: 'distance' o 'duration' no encontrada en la respuesta de la API para {origen} a {destino}")
                    return None, None
            else:
                print(f"Respuesta inesperada de la API: {result}")
                return None, None
        else:
            print(f"Error al obtener distancia: {response.status_code}, {response.text}")
            return None, None
    except Exception as e:
        print(f"Excepción al obtener distancia entre {origen} y {destino}: {e}")
        return None, None

def calcular_distancia_y_tiempo_total(ciudades, api_key):
    total_distancia = 0
    total_tiempo = 0
    for i in range(len(ciudades) - 1):
        distancia, tiempo = obtener_distancia_y_tiempo(ciudades[i], ciudades[i+1], api_key)
        if distancia is None or tiempo is None:
            return None, None
        total_distancia += distancia
        total_tiempo += tiempo
    return total_distancia, total_tiempo

def calcular_costo_casetas(distancia_total, distancia_entre_casetas=100000, costo_por_caseta=50):
    numero_casetas = distancia_total // distancia_entre_casetas
    return numero_casetas * costo_por_caseta

def genetico(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        ciudades = data['ciudades']

        distancia_total, tiempo_total = calcular_distancia_y_tiempo_total(ciudades, api_key)
        if distancia_total is None or tiempo_total is None:
            return JsonResponse({'error': 'Error al calcular la distancia y tiempo total'}, status=400)

        consumo_gasolina = 0.1  # Litros por km
        precio_gasolina = 20  # Precio por litro

        gasolina_consumida = distancia_total / 1000 * consumo_gasolina  # Convertir a km y multiplicar por el consumo
        costo_gasolina = gasolina_consumida * precio_gasolina
        costo_casetas = calcular_costo_casetas(distancia_total)

        return JsonResponse({
            "distancia_total": distancia_total,
            "tiempo_total": tiempo_total,
            "gasolina_consumida": gasolina_consumida,
            "costo_gasolina": costo_gasolina,
            "costo_casetas": costo_casetas
        })

    return JsonResponse({'error': 'Método no permitido'}, status=405)
