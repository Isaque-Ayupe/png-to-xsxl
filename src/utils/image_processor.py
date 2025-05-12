import os
import cv2
import numpy as np
import pandas as pd
import pytesseract
import re
from src.config.settings import TESSDATA_DIR, CUSTOM_CONFIG

def pre_processar_imagem(img):
    """
    Aplica técnicas de pré-processamento para melhorar a qualidade da imagem
    antes do OCR.
    
    Args:
        img: Imagem OpenCV carregada
        
    Returns:
        Imagem processada
    """
    # Converter para escala de cinza
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Aumentar resolução para melhorar OCR
    gray = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    
    # Aplicar limiarização adaptativa para melhorar contraste
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 10
    )
    
    # Aplicar operações morfológicas para remover ruído
    kernel = np.ones((1, 1), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    # Aumentar nitidez
    kernel_sharpening = np.array([[-1,-1,-1], 
                                  [-1, 9,-1],
                                  [-1,-1,-1]])
    thresh = cv2.filter2D(thresh, -1, kernel_sharpening)
    
    return thresh

def detectar_e_recortar_tabela(img):
    """
    Detecta a região da tabela na imagem e a recorta.
    
    Args:
        img: Imagem OpenCV carregada
        
    Returns:
        Região da imagem que contém a tabela
    """
    # Usar uma cópia da imagem
    img_copy = img.copy()
    height, width = img_copy.shape[:2]
    
    # Converter para escala de cinza
    gray = cv2.cvtColor(img_copy, cv2.COLOR_BGR2GRAY)
    
    # Aplicar threshold para destacar áreas escuras (texto e linhas)
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)
    
    # Dilatar linhas horizontais e verticais para detectar tabelas
    kernel_h = np.ones((1, 30), np.uint8)
    kernel_v = np.ones((30, 1), np.uint8)
    
    h_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel_h)
    v_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel_v)
    
    # Combinar linhas horizontais e verticais
    combined = cv2.add(h_lines, v_lines)
    
    # Encontrar contornos
    contours, _ = cv2.findContours(combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filtrar contornos por área
    contornos_validos = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 5000:  # Filtro de área mínima para tabelas
            contornos_validos.append(contour)
    
    # Se não encontrar contornos válidos, recortar a parte inferior da imagem
    # (geralmente onde está a tabela de cotação)
    if not contornos_validos:
        # Recortar 60% inferior da imagem
        y_start = int(height * 0.4)
        tabela_recortada = img_copy[y_start:height, 0:width]
        return tabela_recortada
    
    # Encontrar o contorno maior (provavelmente a tabela)
    maior_contorno = max(contornos_validos, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(maior_contorno)
    
    # Recortar a região da tabela, adicionando uma margem
    margin = 20
    x_start = max(0, x - margin)
    y_start = max(0, y - margin)
    x_end = min(width, x + w + margin)
    y_end = min(height, y + h + margin)
    
    tabela_recortada = img_copy[y_start:y_end, x_start:x_end]
    
    return tabela_recortada

def extrair_tabela_cotacao(img, idioma='por'):
    """
    Extrai dados de uma tabela de cotação com estrutura específica.
    
    Args:
        img: Imagem OpenCV processada
        idioma: Idioma para OCR
        
    Returns:
        DataFrame com dados estruturados da tabela
    """
    # Configuração específica para tabelas
    config_tabela = '--psm 6 --oem 3 -c preserve_interword_spaces=1'
    
    # Extrair texto completo
    text = pytesseract.image_to_string(img, lang=idioma, config=config_tabela)
    
    # Salvar texto extraído para debug
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    with open(os.path.join(base_dir, 'texto_extraido.txt'), 'w', encoding='utf-8') as f:
        f.write(text)
    
    # Extrair linhas de texto
    linhas = text.split('\n')
    
    # Lista para armazenar dados estruturados
    dados_estruturados = []
    
    # Expressão regular para encontrar o código do produto (geralmente está num formato específico)
    # Procurando padrões como: 10 (no início), RSCAT/7-/R, 94012090, etc.
    padrao_codigo = r'^\d+\s+|[A-Z0-9]+\/[A-Z0-9\-]+|[0-9]{7,8}'
    
    # Expressão regular para encontrar valores monetários
    padrao_valor = r'(\d+[.,]\d{2})'
    
    # Processamento linha a linha
    for linha in linhas:
        linha = linha.strip()
        
        # Pular linhas vazias ou muito curtas
        if not linha or len(linha) < 5:
            continue
        
        # Procurar por códigos de produto ou sequências
        match_codigo = re.search(padrao_codigo, linha)
        if not match_codigo:
            continue
        
        try:
            # Extrair sequência/código
            codigo = match_codigo.group().strip()
            
            # Remover o código da linha para extrair a descrição
            descricao_linha = linha[match_codigo.end():].strip()
            
            # Extrair descrição (texto até o próximo valor numérico)
            descricao = re.split(padrao_valor, descricao_linha)[0].strip() if re.search(padrao_valor, descricao_linha) else descricao_linha
            
            # Extrair valores monetários
            valores = re.findall(padrao_valor, linha)
            
            # Converter para float (formato brasileiro)
            valores_float = []
            for valor in valores:
                try:
                    valor_convertido = float(valor.replace('.', '').replace(',', '.'))
                    valores_float.append(valor_convertido)
                except ValueError:
                    continue
            
            # Se encontramos pelo menos um valor monetário
            if valores_float:
                # Ordenar valores (geralmente o maior valor é o valor unitário)
                valores_float.sort(reverse=True)
                
                # Adicionar à lista de dados estruturados
                dados_estruturados.append({
                    'Codigo': codigo,
                    'Descricao': descricao,
                    'Valor_Unitario': valores_float[0] if valores_float else None,
                    'Valores_Adicionais': valores_float[1:] if len(valores_float) > 1 else []
                })
        
        except Exception as e:
            print(f"Erro ao processar linha: {linha}. Erro: {str(e)}")
    
    # Criar DataFrame
    df = pd.DataFrame(dados_estruturados)
    
    return df

def processar_imagem(caminho_imagem, nome_arquivo, idioma='por'):
    """
    Processa uma imagem com OCR e cria uma planilha Excel.
    
    Args:
        caminho_imagem (str): Caminho completo para a imagem
        nome_arquivo (str): Nome do arquivo original
        idioma (str): Código do idioma para OCR (ex: 'por', 'eng')
    
    Returns:
        str ou None: Caminho do arquivo Excel gerado, ou None se falhou
    """
    try:
        # Carregar a imagem
        img = cv2.imread(caminho_imagem)
        
        if img is None:
            print(f"Erro ao carregar a imagem: {caminho_imagem}")
            return None
            
        # Detectar e recortar região da tabela
        print("Detectando região da tabela...")
        img_tabela = detectar_e_recortar_tabela(img)
        
        # Salvar imagem recortada para debug
        cv2.imwrite('tabela_recortada.jpg', img_tabela)
        
        # Pré-processar a imagem
        print("Aplicando pré-processamento...")
        img_processada = pre_processar_imagem(img_tabela)
        
        # Salvar imagem processada para debug
        cv2.imwrite('imagem_processada.jpg', img_processada)
        
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
        
        # Extrair tabela estruturada
        print("Extraindo dados da tabela...")
        df = extrair_tabela_cotacao(img_processada, idioma)
        
        if df.empty:
            print(f"Nenhum dado extraído de: {caminho_imagem}")
            return None
            
        # Exportar para Excel
        nome_excel = f"{os.path.splitext(nome_arquivo)[0]}_estruturado.xlsx"
        caminho_excel = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), nome_excel)
        df.to_excel(caminho_excel, index=False)
        print(f"Arquivo Excel gerado com sucesso: {nome_excel}")
        
        return caminho_excel
    
    except Exception as e:
        print(f"Erro ao processar {caminho_imagem}: {str(e)}")
        return None

def encontrar_imagens(diretorios, extensoes):
    """
    Encontra todas as imagens com extensões específicas nos diretórios fornecidos.
    
    Args:
        diretorios (list): Lista de diretórios para procurar
        extensoes (list): Lista de extensões de arquivo a considerar
    
    Returns:
        list: Lista de tuplas (caminho_completo, nome_arquivo)
    """
    arquivos_imagem = []
    
    for diretorio in diretorios:
        if os.path.exists(diretorio):
            for arquivo in os.listdir(diretorio):
                caminho_completo = os.path.join(diretorio, arquivo)
                if os.path.isfile(caminho_completo):
                    ext = os.path.splitext(arquivo)[1].lower()
                    if ext in extensoes:
                        arquivos_imagem.append((caminho_completo, arquivo))
    
    return arquivos_imagem 