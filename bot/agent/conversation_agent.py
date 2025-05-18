import logging
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder


from bot.utils.time_helpers import get_greeting_by_hour
from bot.prompts.system_prompts import banking_assistant_prompt
from bot.tools.check_authentication import check_authentication
from bot.tools.authenticate_user import authenticate_user
from bot.tools.get_balance import get_balance
from bot.tools.get_transactions import get_transactions
from bot.tools.loan_simulation import simulate_loan
from bot.tools.get_loan_history import get_loan_history
from bot.services.redis_service import redis_service


from config import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
    SESSION_TTL_SECONDS,
    CONTEXT_WINDOW_LENGTH,
    REDIS_HOST,
    REDIS_PORT,
)

logger = logging.getLogger(__name__)


class ConversationAgent:
    """
    Conversational agent for NicoBank using LangChain, Redis and OpenAI functions.
    """

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.redis_url = f"redis://{REDIS_HOST}:{REDIS_PORT}"
        self.agent = self._build_agent()

    def _build_agent(self) -> AgentExecutor:
        memory = ConversationBufferMemory(
            chat_memory=RedisChatMessageHistory(
                session_id=f"chat:{self.user_id}",
                url=self.redis_url,
                ttl=SESSION_TTL_SECONDS,
            ),
            memory_key="chat_history",
            return_messages=True,
            k=CONTEXT_WINDOW_LENGTH,
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                banking_assistant_prompt,
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        llm = ChatOpenAI(
            temperature=0,
            model=OPENAI_MODEL,
            openai_api_key=OPENAI_API_KEY,
        )

        tools = [
            check_authentication,
            authenticate_user,
            get_balance,
            get_transactions,
            simulate_loan,
            get_loan_history,
        ]

        agent = create_openai_functions_agent(
            llm=llm,
            tools=tools,
            prompt=prompt,
        )

        return AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=tools,
            memory=memory,
            verbose=True,
        )

    async def run(self, user_input: str) -> str:
        """
        Procesa la entrada del usuario y devuelve una respuesta generada por el agente.
        """

        await redis_service.increment_interaction_count(self.user_id)
        interaction_count = await redis_service.get_interaction_count(self.user_id)

        greeting = get_greeting_by_hour()
        input_text = (
            f"[user_id: {self.user_id}]\n"
            f"[interacción: {interaction_count}]\n"
            f"[saludo: {greeting}]\n"
            f"Mensaje del usuario: {user_input}"
        )

        logger.info(f"[Agent] Input for {self.user_id}: {user_input}")

        try:
            result = await self.agent.ainvoke(
                {
                    "input": input_text,
                }
            )
            logger.info(f"[Agent] Output for {self.user_id}: {result['output']}")
            return result["output"]
        except Exception as e:
            logger.exception(
                f"[Agent] Error processing message for {self.user_id}: {e}"
            )
            return "Lo siento, ha ocurrido un error interno al procesar su consulta."
