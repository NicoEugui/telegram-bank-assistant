from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from bot.prompts.system_prompts import banking_assistant_prompt
from bot.tools.check_authentication import check_authentication
from bot.tools.authenticate_user import authenticate_user
from bot.tools.get_balance import get_balance
from bot.tools.get_transactions import get_transactions
from bot.tools.loan_simulation import simulate_loan
from bot.tools.get_loan_history import get_loan_history

from config import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
    SESSION_TTL_SECONDS,
    CONTEXT_WINDOW_LENGTH,
    REDIS_HOST,
    REDIS_PORT,
)

import logging

logger = logging.getLogger(__name__)

"""
This module defines the ConversationAgent class, which manages conversational interactions
with a banking assistant using LangChain, OpenAI, and Redis for chat history.
"""
class ConversationAgent:
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

    def run(self, user_input: str) -> str:

        input_text = f"[user_id: {self.user_id}]\n Mensaje del usuario: {user_input}"
        result = self.agent.invoke({"input": input_text})
        return result["output"]
