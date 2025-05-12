import cv2
import pytesseract
import pandas as pd
from openpyxl import Workbook
from PIL import Image

# Caminho pro Tesseract se for Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Carregar e girar a imagem
img = cv2.imread('C:\conversor\entrada\imagem.jpg')  # Troca o nome se for diferente
if img is None:
    print("Erro ao carregar a imagem. Verifique o caminho!")

img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)

# Converter pra escala de cinza
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Binarização adaptativa
thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                               cv2.THRESH_BINARY, 15, 10)

# OCR
custom_config = r'--oem 3 --psm 6'  # Tenta ler como parágrafos organizados
text = pytesseract.image_to_string(thresh, lang='por', config=custom_config)

# Processar o texto
linhas = [linha.split() for linha in text.split('\n') if linha.strip()]
df = pd.DataFrame(linhas)

# Exportar pro Excel
df.to_excel("cotacao_extraida.xlsx", index=False, header=False)
print("Arquivo Excel gerado com sucesso!")
