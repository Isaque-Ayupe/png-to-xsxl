import os
import sys

# Define uma constante com diretório base na raiz do projeto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Cria/configura o diretório tessdata local
TESSDATA_DIR = os.path.join(BASE_DIR, 'tessdata')

# Impede a criação de um arquivo .pyc
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
os.environ['PYTHONUNBUFFERED'] = '1'
sys.dont_write_bytecode = True

# Configura o diretório tessdata como variável de ambiente
os.environ['TESSDATA_PREFIX'] = TESSDATA_DIR

# Configuração do OCR
CUSTOM_CONFIG = r'--oem 3 --psm 6'  # Tenta ler como parágrafos organizados

# Tesseract OCR caminho para Windows
TESSERACT_CMD_WINDOWS = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Diretórios padrão para buscar imagens
IMAGE_DIRS = [
    os.path.join(BASE_DIR, 'data'),
    os.path.join(BASE_DIR, 'data', 'png')
]

# Extensões de imagem suportadas
SUPPORTED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']

# URLs para download dos modelos de idioma (com múltiplas fontes)
LANGUAGE_MODELS = {
    'eng': [
        'https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata',
        'https://github.com/tesseract-ocr/tessdata_best/raw/main/eng.traineddata',
        'https://tesseract-ocr.github.io/tessdata/4.00/eng.traineddata'
    ],
    'por': [
        'https://github.com/tesseract-ocr/tessdata/raw/main/por.traineddata',
        'https://github.com/tesseract-ocr/tessdata_best/raw/main/por.traineddata',
        'https://tesseract-ocr.github.io/tessdata/4.00/por.traineddata'
    ],
    'osd': [
        'https://github.com/tesseract-ocr/tessdata/raw/main/osd.traineddata',
        'https://github.com/tesseract-ocr/tessdata_best/raw/main/osd.traineddata',
        'https://tesseract-ocr.github.io/tessdata/4.00/osd.traineddata'
    ]
}

# Tempo em segundos para aguardar entre tentativas de download
DOWNLOAD_RETRY_DELAY = 2

# Número máximo de tentativas de download
MAX_DOWNLOAD_RETRIES = 3

# Idioma padrão para OCR
DEFAULT_LANGUAGE = 'por' 