from langchain.tools import tool

FAQ = {
    "tarjetas": "Ofrecemos tarjetas de débito y crédito Visa y Mastercard, con beneficios exclusivos en comercios locales.",
    "plazo fijo": "Un plazo fijo puede ser conveniente si buscás una inversión segura. Actualmente ofrecemos una tasa anual del 8.5%.",
    "tasa préstamos": "La tasa de interés para préstamos personales es del 22% anual fija, sujeta a perfil crediticio.",
    "requisitos préstamo": "Para solicitar un préstamo personal necesitás cédula vigente, comprobante de ingresos y antigüedad mínima de 3 meses.",
    "caja ahorro": "Podés abrir una caja de ahorro 100% online, sin costo de mantenimiento durante los primeros 6 meses.",
}

@tool
def answer_bank_faq(question: str) -> str:
    """
    Answers frequently asked questions (FAQs) about banking topics like cards, loans or interest rates.
    """
  

    question = question.lower()
    for key, answer in FAQ.items():
        if key in question:
            return answer
    return "Puedo ayudarte con consultas sobre tarjetas, préstamos, plazo fijo y más. ¿Qué querés saber exactamente?"
