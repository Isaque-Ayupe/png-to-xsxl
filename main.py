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
import argparse
import shutil
import urllib.request
from openpyxl import Workbook
from PIL import Image

# Define uma constante com diretório base na raiz do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Cria/configura o diretório tessdata local
TESSDATA_DIR = os.path.join(BASE_DIR, 'tessdata')
os.environ['TESSDATA_PREFIX'] = TESSDATA_DIR

# Configura caminho para o Tesseract (apenas para Windows)
if sys.platform == 'win32':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Configuração do OCR
custom_config = r'--oem 3 --psm 6'  # Tenta ler como parágrafos organizados

# Função para baixar arquivo
def baixar_arquivo(url, caminho_destino):
    try:
        print(f"Baixando {os.path.basename(caminho_destino)}...")
        urllib.request.urlretrieve(url, caminho_destino)
        print(f"✓ Download concluído: {os.path.basename(caminho_destino)}")
        return True
    except Exception as e:
        print(f"✗ Erro ao baixar {url}: {str(e)}")
        return False

# Função para verificar e baixar os arquivos de idioma
def verificar_e_baixar_idiomas(forcar_download=False):
    idiomas = {
        'eng': 'https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata',
        'por': 'https://github.com/tesseract-ocr/tessdata/raw/main/por.traineddata',
        'osd': 'https://github.com/tesseract-ocr/tessdata/raw/main/osd.traineddata'  # Orientação e detecção de script
    }
    
    os.makedirs(TESSDATA_DIR, exist_ok=True)
    
    idiomas_ok = True
    for idioma, url in idiomas.items():
        arquivo_destino = os.path.join(TESSDATA_DIR, f"{idioma}.traineddata")
        
        # Se o arquivo não existe localmente ou força o download
        if not os.path.exists(arquivo_destino) or forcar_download:
            # Primeiro tenta copiar do Tesseract instalado
            if sys.platform == 'win32' and not forcar_download:
                caminho_sistema = os.path.join(r'C:\Program Files\Tesseract-OCR\tessdata', f"{idioma}.traineddata")
                if os.path.exists(caminho_sistema):
                    try:
                        shutil.copy2(caminho_sistema, arquivo_destino)
                        print(f"✓ Idioma {idioma} copiado da instalação do sistema.")
                        continue
                    except Exception as e:
                        print(f"✗ Erro ao copiar {idioma} do sistema: {str(e)}")
            
            # Se não conseguiu copiar, baixa diretamente
            sucesso = baixar_arquivo(url, arquivo_destino)
            if not sucesso:
                idiomas_ok = False
    
    return idiomas_ok

# Função para processar uma imagem
def processar_imagem(caminho_imagem, nome_arquivo, idioma='por'):
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
        
        # Verifica se o arquivo de idioma existe
        arquivo_idioma = os.path.join(TESSDATA_DIR, f"{idioma}.traineddata")
        if not os.path.exists(arquivo_idioma):
            print(f"Arquivo de idioma {idioma} não encontrado. Tentando usar 'eng'...")
            idioma = 'eng'
            arquivo_idioma = os.path.join(TESSDATA_DIR, "eng.traineddata")
            if not os.path.exists(arquivo_idioma):
                print("Erro: Arquivos de idioma não encontrados.")
                print("Execute 'python main.py --baixar-idiomas' para baixar os modelos de idioma.")
                return None
        
        # OCR com o idioma selecionado
        text = pytesseract.image_to_string(thresh, lang=idioma, config=custom_config)
        
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
    # Configurar argumentos de linha de comando
    parser = argparse.ArgumentParser(description='Converte texto em imagens para arquivos Excel')
    parser.add_argument('--idioma', type=str, default='por', choices=['por', 'eng'],
                        help='Idioma para OCR: por (português) ou eng (inglês)')
    parser.add_argument('--baixar-idiomas', action='store_true', 
                        help='Baixa automaticamente os arquivos de idioma necessários')
    parser.add_argument('--forcar-download', action='store_true',
                        help='Força o download dos arquivos de idioma mesmo se já existirem')
    
    args = parser.parse_args()
    
    # Se solicitado, baixa os idiomas e sai
    if args.baixar_idiomas or args.forcar_download:
        print("Verificando e baixando modelos de idioma...")
        if verificar_e_baixar_idiomas(args.forcar_download):
            print("\n✅ Todos os modelos de idioma foram configurados com sucesso!")
        else:
            print("\n⚠️ Alguns modelos de idioma não puderam ser baixados automaticamente.")
            print("Por favor, baixe manualmente e coloque na pasta 'tessdata'.")
        return
    
    # Verifica se os arquivos de idioma existem antes de prosseguir
    if not os.path.exists(os.path.join(TESSDATA_DIR, f"{args.idioma}.traineddata")):
        print(f"Modelo de idioma '{args.idioma}' não encontrado.")
        print("Tentando baixar automaticamente...")
        verificar_e_baixar_idiomas()
    
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
    print(f"\nIniciando processamento com idioma: {args.idioma}")
    arquivos_processados = 0
    for caminho_imagem, nome_arquivo in arquivos_imagem:
        print(f"\nProcessando: {nome_arquivo}")
        resultado = processar_imagem(caminho_imagem, nome_arquivo, args.idioma)
        if resultado:
            arquivos_processados += 1
    
    print(f"\n✅ Processamento concluído: {arquivos_processados} de {len(arquivos_imagem)} imagens convertidas com sucesso!")

if __name__ == "__main__":
    main()
