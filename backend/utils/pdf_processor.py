import PyPDF2
import os

def extract_text_from_pdf(pdf_path):
    """
    Extrai texto de um arquivo PDF.

    Args:
        pdf_path (str): O caminho completo para o arquivo PDF.

    Returns:
        str: O texto extraído do PDF, ou uma string vazia se houver erro.
    """
    text = ""
    try:
        # Abre o arquivo PDF em modo de leitura binária
        with open(pdf_path, 'rb') as file:
            # Cria um objeto leitor de PDF
            reader = PyPDF2.PdfReader(file)
            # Itera sobre cada página do PDF
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                # Extrai o texto da página e adiciona ao resultado
                text += page.extract_text() + "\n"
    except FileNotFoundError:
        print(f"Erro: Arquivo PDF não encontrado em {pdf_path}")
    except PyPDF2.errors.PdfReadError:
        print(f"Erro: Não foi possível ler o arquivo PDF em {pdf_path}. Pode estar corrompido ou criptografado.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado ao extrair texto do PDF: {e}")
    return text.strip() # Remove espaços em branco no início/fim

if __name__ == '__main__':
    # Exemplo de uso (para testar o módulo individualmente)
    # Crie um arquivo PDF de teste ou use um existente
    dummy_pdf_path = "exemplo.pdf" 
    # Para criar um PDF de teste rápido (requer reportlab, opcional)
    # from reportlab.pdfgen import canvas
    # c = canvas.Canvas(dummy_pdf_path)
    # c.drawString(100, 750, "Este é um texto de exemplo em PDF.")
    # c.save()

    if os.path.exists(dummy_pdf_path):
        extracted_text = extract_text_from_pdf(dummy_pdf_path)
        print(f"\n--- Texto extraído de {dummy_pdf_path} ---")
        print(extracted_text)
    else:
        print(f"\nArquivo '{dummy_pdf_path}' não encontrado. Crie um PDF para testar este módulo.")