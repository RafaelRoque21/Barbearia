from groq import Groq
from django.conf import settings

# Configurar cliente
client = Groq(api_key=settings.GROQ_API_KEY)

def gerar_resposta_chatbot(mensagem: str, historico: list = None) -> str:
    """
    Gera resposta do chatbot usando Groq (GRÁTIS).
    """
    try:
        # Instrução do sistema
        system_message = """Você é um assistente amigável da Barbers OS.

INFORMAÇÕES:
- Horário: Seg-Sex 8h-18h | Sábado 8h-14h
- Endereço: Rua das Flores, 123, Toledo
- Telefone: (45) 98765-4321
- Preços: Corte R$35, Barba R$25, Combo R$50
- Barbeiros: Vitor (Cabelo) e Rafael (Barba)

Responda em máximo 3-4 linhas.
Para agendar: "Acesse www.barberia.com/agendar"
Dar a lista dos horarios disponiveis do dia(caso a pessoa escolha um horario ja ocupado mostre a lista de horarios disponiveis).
Português brasileiro apenas."""

        # Preparar mensagens
        messages = [
            {"role": "system", "content": system_message}
        ]
        
        if historico:
            for msg in historico[-5:]:
                messages.append({
                    "role": msg.get('role', 'user'),
                    "content": msg.get('content', '')
                })
        
        messages.append({
            "role": "user",
            "content": mensagem
        })
        
        print(f"📤 Enviando para Groq: {mensagem}")

        # Chamar Groq
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )

        return response.choices[0].message.content
        print(f"✅ Resposta recebida: {resultado[:50]}...")
        
        return resultado

    except Exception as e:
        erro_msg = f"❌ Erro Groq: {str(e)}"
        print(erro_msg)
        print(f"Tipo de erro: {type(e).__name__}")
        return "Desculpe, tive um problema técnico. Tente novamente! 😊"