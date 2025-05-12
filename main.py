import os
import sys

# Impede a criação de um arquivo .pyc
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
os.environ['PYTHONUNBUFFERED'] = '1'
sys.dont_write_bytecode = True

# Importações
import pytesseract
import cv2
import pandas as pd
from openpyxl import Workbook
from PIL import Image

# Define uma constante com diretório base na raiz do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configura caminho para o Tesseract (apenas para Windows)
if sys.platform == 'win32':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Configuração do OCR
custom_config = r'--oem 3 --psm 6'  # Tenta ler como parágrafos organizados

# Função para processar uma imagem
def processar_imagem(caminho_imagem, nome_arquivo):
    try:
        # Carregar a imagem
        img = cv2.imread(caminho_imagem)
        
        if img is None:
            print(f"Erro ao carregar a imagem: {caminho_imagem}")
            return None
            
        # Opcional: Girar a imagem se necessário
        # img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        
        # Converter para escala de cinza
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Binarização adaptativa para melhorar o OCR
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                                       cv2.THRESH_BINARY, 15, 10)
        
        # OCR
        text = pytesseract.image_to_string(thresh, lang='por', config=custom_config)
        
        # Processar o texto
        linhas = [linha.split() for linha in text.split('\n') if linha.strip()]
        
        if not linhas:
            print(f"Nenhum texto extraído de: {caminho_imagem}")
            return None
            
        df = pd.DataFrame(linhas)
        
        # Exportar para Excel
        nome_excel = f"{os.path.splitext(nome_arquivo)[0]}.xlsx"
        caminho_excel = os.path.join(BASE_DIR, nome_excel)
        df.to_excel(caminho_excel, index=False, header=False)
        print(f"Arquivo Excel gerado com sucesso: {nome_excel}")
        
        return caminho_excel
    
    except Exception as e:
        print(f"Erro ao processar {caminho_imagem}: {str(e)}")
        return None

def main():
    # Verifica os diretórios para as imagens
    diretorios_img = [
        os.path.join(BASE_DIR, 'data'),
        os.path.join(BASE_DIR, 'data', 'png')
    ]
    
    # Lista para guardar todos os arquivos de imagem encontrados
    arquivos_imagem = []
    
    # Extensões de imagem suportadas
    extensoes = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    
    # Procura imagens em todos os diretórios possíveis
    for diretorio in diretorios_img:
        if os.path.exists(diretorio):
            for arquivo in os.listdir(diretorio):
                caminho_completo = os.path.join(diretorio, arquivo)
                if os.path.isfile(caminho_completo):
                    ext = os.path.splitext(arquivo)[1].lower()
                    if ext in extensoes:
                        arquivos_imagem.append((caminho_completo, arquivo))
    
    if not arquivos_imagem:
        print("Nenhuma imagem encontrada nos diretórios 'data' ou 'data/png'!")
        return
    
    # Processar cada imagem encontrada
    arquivos_processados = 0
    for caminho_imagem, nome_arquivo in arquivos_imagem:
        print(f"Processando: {nome_arquivo}")
        resultado = processar_imagem(caminho_imagem, nome_arquivo)
        if resultado:
            arquivos_processados += 1
    
    print(f"\nProcessamento concluído: {arquivos_processados} de {len(arquivos_imagem)} imagens convertidas com sucesso!")

if __name__ == "__main__":
    main()
