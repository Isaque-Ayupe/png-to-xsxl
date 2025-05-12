# PNG para XLSX - Conversor de Imagens para Excel

Um conversor que extrai texto de imagens usando OCR (Reconhecimento Óptico de Caracteres) e salva os dados em planilhas Excel.

## 📋 Descrição

Este projeto foi desenvolvido para transformar texto contido em imagens (como tabelas, cotações ou listas) em planilhas Excel (.xlsx) organizadas. O programa utiliza técnicas de processamento de imagem para melhorar a precisão do OCR e é otimizado para texto em português.

## 🛠️ Tecnologias Utilizadas

- **Python**: Linguagem principal
- **OpenCV**: Processamento e manipulação de imagens
- **Tesseract OCR**: Extração de texto das imagens
- **Pandas**: Manipulação de dados
- **OpenPyXL**: Criação de arquivos Excel

## 🔧 Requisitos

- Python 3.6 ou superior
- Tesseract OCR instalado no sistema
  - Windows: [Tesseract-OCR para Windows](https://github.com/UB-Mannheim/tesseract/wiki)
  - Linux: `sudo apt install tesseract-ocr`
  - macOS: `brew install tesseract`
- Pacotes Python listados em `requirements.txt`

## ⚙️ Instalação

1. Clone este repositório:

   ```bash
   git clone git@github.com:Isaque-Ayupe/png-to-xsxl.git
   ```

2. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

3. Certifique-se de que o Tesseract OCR está instalado corretamente no seu sistema.

## 📂 Estrutura do Projeto

```text
png-to-xlsx/
│
├── main.py          # Script principal
├── requirements.txt # Dependências do projeto
├── README.md        # Documentação
│
└── data/            # Diretório para imagens de entrada
    └── png/         # Subdiretório alternativo para imagens
```

## 🚀 Como Usar

1. Coloque suas imagens na pasta `data/` ou `data/png/`
   - Formatos suportados: JPG, JPEG, PNG, BMP, TIFF

2. Execute o script principal:

   ```bash
   python main.py
   ```

3. Os arquivos Excel serão gerados na pasta raiz do projeto, com nomes correspondentes aos arquivos de imagem originais.

## ✨ Características

- Processamento de múltiplas imagens em lote
- Conversão automática para escala de cinza e binarização para melhorar resultados
- Suporte para diferentes formatos de imagem
- Tratamento de erros robusto
- Feedback detalhado do processo de conversão

## 📝 Notas

- A qualidade do OCR depende muito da qualidade da imagem original
- Para melhores resultados, use imagens com texto claro e com bom contraste
- O programa está configurado para reconhecer texto em português por padrão

## 🤝 Contribuições

Contribuições são bem-vindas!

- [Isaque Ayupe](https://github.com/Isaque-Ayupe)
