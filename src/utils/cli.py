import argparse
from src.config.settings import DEFAULT_LANGUAGE

def configurar_argumentos():
    """
    Configura e processa os argumentos de linha de comando.
    
    Returns:
        argparse.Namespace: Objeto contendo os argumentos processados
    """
    parser = argparse.ArgumentParser(
        description='Converte texto em imagens para arquivos Excel'
    )
    
    parser.add_argument(
        '--idioma', 
        type=str, 
        default=DEFAULT_LANGUAGE, 
        choices=['por', 'eng'],
        help='Idioma para OCR: por (português) ou eng (inglês)'
    )
    
    parser.add_argument(
        '--baixar-idiomas', 
        action='store_true',
        help='Baixa automaticamente os arquivos de idioma necessários'
    )
    
    parser.add_argument(
        '--forcar-download', 
        action='store_true',
        help='Força o download dos arquivos de idioma mesmo se já existirem'
    )
    
    return parser.parse_args() 