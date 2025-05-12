#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Conversor de imagens com texto para arquivos Excel.
Utiliza OCR para extrair texto de imagens e salva em formato XLSX.
"""

import os
import sys
import pytesseract

# Importar os módulos da estrutura modularizada
from src.config.settings import (
    TESSERACT_CMD_WINDOWS, 
    IMAGE_DIRS,
    SUPPORTED_EXTENSIONS, 
    TESSDATA_DIR
)
from src.utils.language_manager import verificar_e_baixar_idiomas, verificar_idioma_disponivel
from src.utils.image_processor import processar_imagem, encontrar_imagens
from src.utils.cli import configurar_argumentos

def configurar_ambiente():
    """Configura o ambiente de execução."""
    # Configura caminho para o Tesseract (apenas para Windows)
    if sys.platform == 'win32':
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD_WINDOWS

def main():
    """Função principal do programa."""
    # Configurar o ambiente
    configurar_ambiente()
    
    # Processar argumentos da linha de comando
    args = configurar_argumentos()
    
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
    if not verificar_idioma_disponivel(args.idioma):
        print(f"Modelo de idioma '{args.idioma}' não encontrado.")
        print("Tentando baixar automaticamente...")
        verificar_e_baixar_idiomas()
        
        # Verifica novamente após tentativa de download
        if not verificar_idioma_disponivel(args.idioma):
            print(f"Não foi possível utilizar o idioma '{args.idioma}'.")
            print("Tente executar 'python main.py --baixar-idiomas' e tente novamente.")
            return
    
    # Encontrar imagens para processar
    arquivos_imagem = encontrar_imagens(IMAGE_DIRS, SUPPORTED_EXTENSIONS)
    
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
