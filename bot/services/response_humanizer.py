from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from config import OPENAI_API_KEY, OPENAI_MODEL

import json
import logging
import re

logger = logging.getLogger(__name__)

"""
Module for humanizing and formatting assistant responses for a banking chatbot.
This module uses OpenAI's language model to convert raw responses into a more
human-readable format, breaking them into smaller conversational parts.
"""


class ResponseHumanizer:
    def __init__(self, raw_response: str):
        self.raw_response = raw_response

        self.llm = ChatOpenAI(
            temperature=0.5,
            model=OPENAI_MODEL,
            openai_api_key=OPENAI_API_KEY,
        )

        prompt_template = """
            Tenes que humanizar una respuesta de asistente bancario y dividirla en partes conversacionales naturales.

            1. Humaniza la conversacion para que suene natural, clara y fluida.  
            2. Eliminá los signos de apertura como "¡" y "¿", pero conservá los de cierre "!" y "?".  
            3. Dividí el texto en hasta 4 partes llamadas parte_1, parte_2, parte_3 y parte_4.  
            Cada parte debe ser una unidad de sentido. No cortes frases.  
            Si no hay suficiente contenido, dejá vacías las partes que no se usen.

            Si el contenido es una lista estructurada de movimientos o préstamos, aplicá estos formatos:

            Para movimientos bancarios:
            🧾 Últimos movimientos:
            📅 [fecha]  
            ⬆️ Ingreso · $ [monto]  
            ⬇️ Egreso · $ [monto]

            Para historial de préstamos simulados:
            🧾 Historial de préstamos simulados:
            Préstamo 1:  
            💰 Monto: $ [monto]  
            📆 Plazo: [meses] meses  
            🧾 Cuota mensual: $ [cuota]  
            🔢 Total a pagar: $ [total]  
            📅 Fecha: [fecha]

            Para simulación de préstamo individual:
            🧾 Simulación de préstamo:

            💰 Monto solicitado: $ [monto]  
            📆 Plazo en meses: [meses]  
            🧾 Valor cuota: $ [cuota]  
            🔢 Total a pagar: $ [total]  
            💸 Monto de intereses: $ [intereses]  
            📅 Fecha de simulación: [fecha]

            Para resumen de perfil crediticio:

            📊 Resumen de perfil:
    
            🔍 Nivel crediticio: [level]  
            💼 Ingresos mensuales estimados: $ [monthly_income]  
            ⚠️ Riesgo de crédito: [risk]

            Para confirmaciones de simulación antes de ejecutar:

            Si el mensaje incluye una confirmación como:
            “Perfecto, para confirmar, usted quiere simular un préstamo con un monto de 344.000 pesos uruguayos y pagarlo en 14 meses. ¿Es correcto esto?”

            Dividí el mensaje en partes lógicas
            
            Si recibís una frase como:  

            “Según su perfil, usted califica como cliente de riesgo moderado con ingresos mensuales estimados en $75,000”  
            Debés convertirla a este formato, agregando el título:

            📊 Resumen de perfil: 

            [frase original]

            Asegurate de usar salto de línea entre cada línea. No escribas todo seguido en una sola frase.

            Respondé con un JSON válido así:
            {
            "parte_1": "...",
            "parte_2": "...",
            "parte_3": "...",
            "parte_4": "..."
            }
        """

        self.prompt = ChatPromptTemplate.from_messages(
            [SystemMessage(content=prompt_template), ("human", "{raw_response}")]
        )

    def rewrite(self) -> dict:
        try:
            chain = self.prompt | self.llm
            response = chain.invoke({"raw_response": self.raw_response}).content

            # using regex to find the first JSON-like block
            match = re.search(r"\{.*?\}", response, re.DOTALL)
            if not match:
                raise ValueError("No se encontró un bloque JSON en la respuesta")

            parsed = json.loads(match.group(0))
            return {
                "parte_1": parsed.get("parte_1", ""),
                "parte_2": parsed.get("parte_2", ""),
                "parte_3": parsed.get("parte_3", ""),
                "parte_4": parsed.get("parte_4", ""),
            }

        except Exception as e:
            logger.exception(f"[Humanizer] Failed to parse response: {e}")
            return {
                "parte_1": self.raw_response,
                "parte_2": "",
                "parte_3": "",
                "parte_4": "",
            }
