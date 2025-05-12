import os
import sys
import time
import shutil
import urllib.request
from src.config.settings import (
    TESSDATA_DIR, 
    LANGUAGE_MODELS, 
    DOWNLOAD_RETRY_DELAY, 
    MAX_DOWNLOAD_RETRIES
)

def baixar_arquivo(urls, caminho_destino):
    """
    Tenta baixar um arquivo de múltiplas URLs com mecanismo de retry.
    
    Args:
        urls (list): Lista de URLs para tentar baixar
        caminho_destino (str): Caminho completo onde o arquivo será salvo
    
    Returns:
        bool: True se o download foi bem-sucedido, False caso contrário
    """
    nome_arquivo = os.path.basename(caminho_destino)
    print(f"Baixando {nome_arquivo}...")
    
    for url in urls:
        for tentativa in range(1, MAX_DOWNLOAD_RETRIES + 1):
            try:
                print(f"  Tentativa {tentativa} de {MAX_DOWNLOAD_RETRIES} - URL: {url}")
                urllib.request.urlretrieve(url, caminho_destino)
                print(f"✓ Download concluído: {nome_arquivo}")
                return True
            except Exception as e:
                erro = str(e)
                print(f"✗ Erro na tentativa {tentativa}: {erro}")
                
                # Se não é última tentativa e não é a última URL, aguarda antes de tentar novamente
                if tentativa < MAX_DOWNLOAD_RETRIES or url != urls[-1]:
                    print(f"  Aguardando {DOWNLOAD_RETRY_DELAY} segundos antes de tentar novamente...")
                    time.sleep(DOWNLOAD_RETRY_DELAY)
    
    print(f"❌ Falha no download de {nome_arquivo} após tentar todas as URLs.")
    return False

def verificar_e_baixar_idiomas(forcar_download=False):
    """
    Verifica se os arquivos de idioma existem e os baixa se necessário.
    
    Args:
        forcar_download (bool): Se True, força o download mesmo se o arquivo já existir
    
    Returns:
        bool: True se todos os idiomas estão disponíveis, False caso contrário
    """
    os.makedirs(TESSDATA_DIR, exist_ok=True)
    
    idiomas_ok = True
    for idioma, urls in LANGUAGE_MODELS.items():
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
            sucesso = baixar_arquivo(urls, arquivo_destino)
            if not sucesso:
                idiomas_ok = False
    
    return idiomas_ok

def verificar_idioma_disponivel(idioma):
    """
    Verifica se um idioma específico está disponível.
    
    Args:
        idioma (str): Código do idioma (ex: 'por', 'eng')
    
    Returns:
        bool: True se o idioma está disponível, False caso contrário
    """
    return os.path.exists(os.path.join(TESSDATA_DIR, f"{idioma}.traineddata")) 