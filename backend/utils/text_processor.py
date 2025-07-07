import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer

# --- Baixar dados necessários para NLTK (melhorado) ---
# Esta parte garantirá que os recursos existam antes de tentar usá-los.

def ensure_nltk_data():
    """Baixa recursos NLTK se ainda não estiverem presentes."""
    resources = ['stopwords', 'punkt', 'wordnet', 'omw-1.4']
    for resource in resources:
        try:
            nltk.data.find(f'corpora/{resource}')
            print(f"NLTK Resource '{resource}' já encontrado.")
        except LookupError:
            print(f"Baixando NLTK Resource '{resource}'...")
            try:
                nltk.download(resource)
                print(f"NLTK Resource '{resource}' baixado com sucesso.")
            except Exception as e: # Captura uma exceção mais genérica
                print(f"Erro ao baixar NLTK Resource '{resource}': {e}")
                print("Por favor, tente executar 'python -m nltk.downloader <recurso>' manualmente no terminal.")

# Chame esta função para garantir que os dados estejam disponíveis
ensure_nltk_data()

# Inicializar stemmer e lemmatizer
stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()
# Inclua stopwords de português e inglês para cobertura ampla
stop_words = set(stopwords.words('portuguese') + stopwords.words('english'))

def preprocess_text(text):
    """
    Realiza pré-processamento básico em um texto.
    Para LLMs, a remoção de stopwords é geralmente a única modificação recomendada,
    pois mantém o contexto completo. Stemmização/Lematização são geralmente evitadas.
    """
    if not isinstance(text, str):
        return ""

    text = text.lower()
    tokens = word_tokenize(text)
    
    # Remover stopwords
    filtered_tokens = [word for word in tokens if word not in stop_words]

    return " ".join(filtered_tokens)

if __name__ == '__main__':
    # Exemplo de uso (para testar o módulo individualmente)
    print("\n--- Testando text_processor.py ---")
    sample_text = "Prezados, gostaríamos de saber o status da nossa solicitação de saque feita semana passada. Muito obrigado!"
    processed_sample = preprocess_text(sample_text)
    print(f"Texto Original: {sample_text}")
    print(f"Texto Processado: {processed_sample}")

    sample_text_2 = "Hello, I would like to know the status of my loan application. Thanks!"
    processed_sample_2 = preprocess_text(sample_text_2)
    print(f"Texto Original: {sample_text_2}")
    print(f"Texto Processado: {processed_sample_2}")