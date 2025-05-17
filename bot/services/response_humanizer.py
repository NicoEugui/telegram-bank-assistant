from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from config import OPENAI_API_KEY, OPENAI_MODEL

import json
import logging

logger = logging.getLogger(__name__)

class ResponseHumanizer:
    def __init__(self, raw_response: str):
        self.llm = ChatOpenAI(
            temperature=0.5,
            model=OPENAI_MODEL,
            openai_api_key=OPENAI_API_KEY,
        )

        prompt_text = """
                # Tenes 3 tareas a completar muy importantes

                ## 1: Tu primer y principal tarea es humanizar la conversacion, tené en cuenta que las respuestas que envien forman parte de una
                conversacion con un usuario, por lo que priorizar la claridad y naturalidad. Por lo tanto las tareas que estan a continuacion son
                puntos que vas a tener en cuenta para poder humanizar la conversacion convertiendola en un ida y vuelta natural y claro.


                ## 2: En caso de que los contenga, elimina los signos de apertura tanto de exlamacion como de interrogacion ("¡" y "¿")
                y deja los de cierre del siguiente texto: "{raw}". Es crucial que los signos de finalizacion los dejes ("!" y "?").


                ## 3: Con el fin de humanizar la conversacion y simular una conversacion entre personas, tenes que separar el siguiente mensaje: "{raw}",
                sin dejar nada afuera, en 3 partes mas pequeñas. Tené en cuenta que es posible que el mensaje sea demasiado breve y no tengas que dividir especificamente
                en 3 partes, en caso de que suceda eso, deja las partes necesarias vacias. Cada parte tiene que tener un sentido por su cuenta y no debe cortarse a menos que
                haya un punto o un simbulo que de por terminada la oracion. Asegurate de que cada una de las partes que devolves no termine en un punto ya que hace la conversacion
                mas real. 

                ## 4: Para el caso de saldos y movimientos mantiene el formato de la respuesta como viene, no lo modifiques.
                
                Evitá cortar texto relevante o dejar líneas vacías.
                Devolveme:
                
                {
                    "parte_1": "Texto de la primera parte",
                    "parte_2": "Texto de la segunda parte",
                    "parte_3": "Texto de la tercera parte"
                }

                Ejemplo 1:

                Recibis:

                "¡Bienvenido a NicoBank! ¿En que puedo ayudarte hoy?"

                Respondes:
                {
                    "parte1": "Bienvenido a NicoBank!",
                    "part_2": "En que puedo ayudarte hoy?",
                    "part_3": ""
                }

                ## Importante:
                - Es crucial que los signos de finalizacion los dejes ("!" y "?"). Pero los de apertura tanto de exlamacion como de interrogacion ("¡" y "¿") los elimines.
                - No utilices formato Markdown como **negritas** ni _itálicas_ en tus respuestas. Respondé solo con texto plano

        """
        prompt_text = prompt_text.replace("{raw}", raw_response)

        self.prompt = ChatPromptTemplate.from_messages(
            [SystemMessage(content=prompt_text)]
        )

    def rewrite(self) -> dict:
        chain = self.prompt | self.llm
        response = chain.invoke({}).content
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.exception(f"[Humanizer] JSON decoding failed: {e}")
            return {
                "parte_1": response,
                "parte_2": "",
                "parte_3": ""
            }
