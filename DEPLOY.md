# 🚀 Guia de Deploy - Núcleo Digital Dashboard

## Pré-requisitos
- Python 3.8+
- Acesso à internet (para instalar dependências)

## Configuração Inicial

1. **Instalar Dependências**
   Abra o terminal na pasta do projeto e execute:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar Variáveis de Ambiente**
   Certifique-se de que o arquivo `.env` está na raiz do projeto com as chaves:
   ```env
   TRELLO_API_KEY=sua_chave_aqui
   TRELLO_TOKEN=seu_token_aqui
   TRELLO_BOARD_ID=id_do_quadro
   ```

## Executando o Dashboard

### Opção 1: Via Script (Windows)
Basta clicar duas vezes no arquivo `run.bat`.

### Opção 2: Via Terminal
```bash
streamlit run app.py
```

## Estrutura do Projeto
- `app.py`: Ponto de entrada da aplicação
- `src/`: Código fonte (serviços, UI, lógica)
- `assets/`: Imagens e ícones
- `.streamlit/`: Configurações do framework

---
**Suporte:** Entre em contato com o time de dados do Núcleo Digital.
