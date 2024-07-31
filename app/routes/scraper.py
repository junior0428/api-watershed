from fastapi import APIRouter
import requests
from bs4 import BeautifulSoup
import pandas as pd

router = APIRouter()

@router.get("/scrape/")
async def scrape_website():
    url = "https://saihguadiana.com/E/DATOS"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Encuentra la tabla
    tabla = soup.find('table')  # Asegúrate de que este selector es correcto para tu sitio

    # Procesa cada fila de la tabla
    headers = [th.text.strip() for th in tabla.find('tr').find_all('th')]
    rows = []
    for row in tabla.find_all('tr')[1:]:  # Excluye el encabezado
        cols = [td.text.strip() for td in row.find_all('td')]
        rows.append(cols)
    
    # Opcionalmente convierte los datos a un DataFrame para manipularlos más fácilmente (si es necesario)
    df = pd.DataFrame(rows, columns=headers)

    # Convertir DataFrame a JSON
    result = df.to_dict(orient='records')  # Convierte el DataFrame a un diccionario de registros

    return {"data": result}
