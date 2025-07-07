from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests
import json
from werkzeug.utils import secure_filename
import tempfile
from pathlib import Path

# Importar seus módulos de utilidade
from utils.pdf_processor import extract_text_from_pdf
from utils.text_processor import preprocess_text # Mantido, mesmo que não usado diretamente no app.py atual

# Importar o cliente Groq
from groq import Groq 

load_dotenv()

app = Flask(__name__)
CORS(app) # Habilita CORS para todas as rotas - essencial para o frontend

# --- Configurações da API Groq para Geração de Texto ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY não encontrada nas variáveis de ambiente. Por favor, defina-a no seu arquivo .env")
GROQ_GENERATION_MODEL_ID = os.getenv("GROQ_GENERATION_MODEL_ID", "llama3-8b-8192") # Modelo padrão do Llama 3 8B Instruct

groq_client = Groq(api_key=GROQ_API_KEY) # Inicializa o cliente Groq

# --- Configurações da API Hugging Face para Classificação Zero-Shot ---
HF_API_TOKEN = os.getenv("HUGGING_FACE_API_TOKEN")
CLASSIFICATION_MODEL_ID = os.getenv("CLASSIFICATION_MODEL_ID", "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")
CLASSIFICATION_API_URL = f"https://api-inference.huggingface.co/models/{CLASSIFICATION_MODEL_ID}"
hf_headers = {"Authorization": f"Bearer {HF_API_TOKEN}"} if HF_API_TOKEN else {}

# Permitir uploads de arquivos em um diretório temporário
UPLOAD_FOLDER = tempfile.gettempdir()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Tipos de arquivos permitidos
ALLOWED_EXTENSIONS = {'txt', 'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Função auxiliar para fazer requisições à API do Hugging Face (apenas para classificação)
def query_huggingface_api(api_url, payload, task_type):
    
    try:
        response = requests.post(api_url, headers=hf_headers, json=payload)
        response.raise_for_status() # Lança um HTTPError para respostas de erro (4xx ou 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"ERRO ao chamar a API {task_type} do Hugging Face: {e}")
        if e.response:
            print(f"Conteúdo da resposta de erro: {e.response.text}")
        raise Exception(f"Erro ao comunicar com a IA ({task_type}): {e}")
    except json.JSONDecodeError as e:
        print(f"ERRO ao decodificar JSON da resposta da API {task_type} do Hugging Face: {e}")
        if 'response' in locals():
            print(f"Resposta bruta que causou o erro: {response.text}")
        raise Exception(f"Resposta da IA ({task_type}) em formato inválido: {e}")

@app.route('/api/classify', methods=['POST'])
def classify_email():
    email_content = None
    print("DEBUG: classify_email rota acessada.")

    # 1. Tentar ler o conteúdo do corpo da requisição (texto direto)
    if request.is_json:
        data = request.get_json()
        email_content = data.get('email_text')
        if email_content:
            print("DEBUG: Conteúdo do email recebido via JSON (texto direto).")
    
    # 2. Se não houver texto direto, verificar upload de arquivo
    if not email_content and 'file' in request.files:
        file = request.files['file']
        print(f"DEBUG: 'file' encontrado em request.files. Filename: {file.filename}")

        if file.filename == '':
            print("DEBUG: Nenhum arquivo selecionado (filename vazio).")
            return jsonify({"error": "Nenhum arquivo selecionado"}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print(f"DEBUG: Salvando arquivo temporário em: {filepath}")
            try:
                file.save(filepath)
                print(f"DEBUG: Arquivo '{filename}' salvo temporariamente.")
            except Exception as e:
                print(f"ERRO: Falha ao salvar arquivo: {e}")
                return jsonify({"error": f"Não foi possível salvar o arquivo: {e}"}), 500

            # ESTE É O BLOCO QUE VOCÊ DEVE SUBSTITUIR:
            # Procure por esta estrutura condicional:
            if filename.lower().endswith('.txt'):
                # >>> COLE O NOVO CÓDIGO AQUI <<<
                # A partir daqui, substitua tudo que está dentro deste 'if'
                # até o 'elif filename.lower().endswith('.pdf'):'
                
                email_content = None # Inicializa como None
                
                # Lista de codificações para tentar, em ordem de probabilidade
                codificacoes_para_tentar = ['utf-8', 'latin-1', 'cp1252']
                
                for encoding_attempt in codificacoes_para_tentar:
                    try:
                        print(f"DEBUG: Tentando ler TXT com codificação '{encoding_attempt}': {filepath}") # NOVO LOG
                        with open(filepath, 'r', encoding=encoding_attempt) as f:
                            email_content = f.read()
                        print(f"DEBUG: Conteúdo do email lido de arquivo TXT com sucesso usando '{encoding_attempt}'.")
                        print(f"DEBUG: Primeiros 50 caracteres do TXT lido: '{email_content[:50]}'")
                        break # Se a leitura for bem-sucedida, sai do loop
                    except UnicodeDecodeError:
                        print(f"ALERTA: Falha ao ler TXT com '{encoding_attempt}'. Tentando a próxima...")
                        continue # Tenta a próxima codificação
                    except Exception as e:
                        # Para outros erros que não sejam de decodificação
                        print(f"ERRO: Erro inesperado ao tentar ler arquivo TXT com '{encoding_attempt}': {e}")
                        break # Sai do loop em caso de erro não-decodificação
                
                if email_content is None:
                    # Se todas as tentativas falharem
                    print("ERRO: Todas as tentativas de leitura do arquivo TXT falharam.")
                    return jsonify({"error": "Não foi possível ler o arquivo TXT com nenhuma codificação conhecida."}), 500

            # O restante do seu código (elif para PDF e remoção do arquivo, etc.)
            elif filename.lower().endswith('.pdf'):
                print(f"DEBUG: Processando arquivo PDF: {filepath}")
                try:
                    email_content = extract_text_from_pdf(filepath)
                    print("DEBUG: Conteúdo do email lido de arquivo PDF com sucesso.")
                except Exception as e:
                    print(f"ERRO: Falha ao extrair texto do PDF: {e}")
                    return jsonify({"error": f"Não foi possível extrair texto do PDF: {e}"}), 500
            
            # Remover o arquivo temporário após o processamento
            try:
                os.remove(filepath)
                print(f"DEBUG: Arquivo '{filename}' removido.")
            except Exception as e:
                print(f"ALERTA: Não foi possível remover o arquivo temporário {filepath}: {e}")
                
            if not email_content:
                print("DEBUG: email_content vazio após processamento de arquivo.")
                return jsonify({"error": "Não foi possível extrair texto do arquivo."}), 400
        else:
            print(f"DEBUG: Arquivo não permitido ou inválido. Filename: {file.filename}")
            return jsonify({"error": "Tipo de arquivo não permitido. Apenas .txt e .pdf são aceitos."}), 400
    
    if not email_content:
        print("DEBUG: email_content ainda está vazio. Retornando erro 400.")
        return jsonify({"error": "Nenhum conteúdo de email fornecido. Por favor, envie texto ou um arquivo."}), 400

    # Pré-processar o texto (opcional, mas boa prática para NLP)
    print(f"Texto original recebido: {email_content[:100]}...")

    classificacao = "Desconhecida"
    resposta_sugerida = "Não foi possível gerar uma resposta."

    try:
        # --- ETAPA 1: CLASSIFICAÇÃO usando Hugging Face Zero-Shot Classification ---
        print("\nIniciando Classificação com Hugging Face Zero-Shot...")
        # Mantém as descrições completas para a classificação do modelo
        candidate_labels = ["Produtivo (Trata de assuntos comerciais ativos, notificação de erros em sistemas, acordos.)", "Improdutivo (Trata de feedbacks, spam, mensagens de agradecimento, entre outros textos deste genêro.)"]
        
        classification_payload = {
            "inputs": email_content,
            "parameters": {"candidate_labels": candidate_labels},
            "options": {"wait_for_model": True}
        }
        
        classification_response = query_huggingface_api(
            CLASSIFICATION_API_URL, 
            classification_payload, 
            "classificação"
        )
        
        classificacao_bruta = "Não Classificado"
        if classification_response and 'labels' in classification_response and classification_response['labels']:
            classificacao_bruta = classification_response['labels'][0]
            print(f"Classificação recebida do Hugging Face (bruta): {classificacao_bruta}")
            
            # CORREÇÃO APLICADA AQUI: Extrair apenas a palavra-chave para o frontend
            if "Produtivo" in classificacao_bruta:
                classificacao = "Produtivo"
            elif "Improdutivo" in classificacao_bruta:
                classificacao = "Improdutivo"
            else:
                classificacao = "Não Classificado" # Fallback se a string não contiver os termos esperados
        else:
            print("Não foi possível obter classificação da API Hugging Face.")
            classificacao = "Não Classificado"

        # --- ETAPA 2: GERAÇÃO DE RESPOSTA usando GROQ (Llama 3) ---
        print(f"\nIniciando Geração de Resposta com Groq ({GROQ_GENERATION_MODEL_ID})...")
        
        # O prompt usa a variável 'classificacao' que agora contém apenas a palavra-chave
        generation_prompt = f"""\
Você é um Assistente de Atendimento ao Cliente para uma empresa financeira, especializado em categorizar e gerar respostas automáticas para e-mails.

O e-mail abaixo foi classificado como '{classificacao}'.

Com base nesta classificação e no conteúdo do e-mail, sua tarefa é gerar uma resposta automática:

1.  **Concisa e Profissional:** A resposta deve ser direta ao ponto e manter um tom corporativo.
2.  **Relevante e Útil:** Aborde diretamente a questão levantada no e-mail, oferecendo uma solução, informação ou próximo passo claro, mesmo que a classificação seja 'improdutiva'.
3.  **Sem Menção à Classificação:** Nunca mencione a classificação do e-mail (ex: "Seu e-mail produtivo...") na resposta final.
4.  **Respostas Evasivas para Dúvidas Sensíveis:** Se o e-mail perguntar sobre o funcionamento interno da empresa, processos confidenciais ou a natureza deste sistema de resposta (ex: "Você é uma IA?", "Como funciona a automação?"), forneça uma resposta curta e evasiva que não revele informações cruciais. Prefira redirecionar para uma equipe de suporte ou informações públicas. Ex: "Nossa equipe de assistentes está aqui para ajudar.", "Para detalhes sobre nossos processos internos, por favor, entre em contato com nosso suporte dedicado."
5.  **Tom Humanizado:** Embora seja uma resposta automática, evite termos que revelem que você é uma inteligência artificial. Use linguagem que sugira uma equipe de assistentes ou um sistema de suporte.
6.  **Formato:** Gere APENAS o texto da resposta automática, sem introduções ou saudações do seu papel como IA.

Email:
---
{email_content}
---

Resposta automática sugerida:
"""
        
        groq_response = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": generation_prompt,
                }
            ],
            model=GROQ_GENERATION_MODEL_ID,
            temperature=0.7,
            max_tokens=200,
        )
        
        if groq_response.choices and groq_response.choices[0].message.content:
            resposta_sugerida = groq_response.choices[0].message.content.strip()
            print(f"Resposta gerada pela Groq: {resposta_sugerida}")
        else:
            print("Não foi possível gerar resposta da API Groq. Resposta vazia.")
            resposta_sugerida = "Não foi possível gerar uma resposta automática neste momento. Por favor, tente novamente."

        # Retornar os resultados, garantindo que 'classificacao' é a string limpa
        return jsonify({
            "classificacao": classificacao,
            "resposta_sugerida": resposta_sugerida
        }), 200

    except Exception as e:
        print(f"Erro inesperado no processo de IA: {e}")
        return jsonify({"error": f"Ocorreu um erro ao processar o email: {e}. Verifique logs do servidor."}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)