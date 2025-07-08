# Automail AI 🤖📧

Bem-vindo ao **Automail AI**, sua ferramenta inteligente para categorizar e responder e-mails de forma rápida e eficiente! Com o Automail AI, você pode classificar o conteúdo de e-mails como "Produtivo" ou "Improdutivo" e receber uma sugestão de resposta automática, otimizando seu fluxo de trabalho.

## ✨ Visão Geral e Funcionalidades

O Automail AI é uma aplicação web que utiliza inteligência artificial (IA) para analisar o conteúdo de e-mails. Ele oferece duas maneiras principais de inserir o conteúdo para análise:

* **Inserção Direta de Texto:** Digite ou cole o corpo do e-mail diretamente em um campo de texto.
* **Upload de Arquivo:** Carregue o conteúdo do e-mail por meio de arquivos do tipo `.txt` ou `.pdf`.

Após a inserção, a aplicação classifica o e-mail e gera uma resposta automática sugerida.

## 🚀 Tecnologias Utilizadas

Este projeto é construído com as seguintes tecnologias:

**Frontend:**
* **HTML5:** Estrutura da aplicação web.
* **CSS3:** Estilização responsiva, incluindo ajustes para mobile.
* **JavaScript:** Lógica de interação, comunicação com o backend e manipulação do DOM.

**Backend (API):**
* **Python:** Linguagem principal do backend.
* **Flask:** Microframework web para a construção da API RESTful.
* **scikit-learn:** Utilizado para os modelos de Machine Learning para classificação e sugestão de resposta.
* **pandas:** Para manipulação e análise de dados (provavelmente no contexto da IA).
* **numpy:** Para operações numéricas de alto desempenho (base para `pandas` e `scikit-learn`).
* **PyPDF2:** Para extrair texto de arquivos PDF.
* **python-dotenv:** Para gerenciamento seguro de variáveis de ambiente.

## ⚙️ Como Configurar e Rodar o Projeto

Siga os passos abaixo para configurar e rodar o Automail AI em seu ambiente local.

### Pré-requisitos

Certifique-se de ter o seguinte software instalado em sua máquina:

* Python (versão 3.8 ou superior recomendada)
* pip (gerenciador de pacotes do Python)
* Git

### 1. Clonar o Repositório

Primeiro, clone o repositório do GitHub para sua máquina local:

```bash
git clone [https://github.com/C4io-Rosa/Automail-AI.git](https://github.com/C4io-Rosa/Automail-AI.git)
cd Automail-AI
