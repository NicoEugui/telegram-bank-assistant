from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_openai import ChatOpenAI

from bot.tools.answer_bank_faq import answer_bank_faq


class ConversationAgent:
    def __init__(self, user_id: str, redis_url: str, openai_api_key: str):
        self.user_id = user_id
        self.redis_url = redis_url
        self.openai_api_key = openai_api_key
        self.agent = self._build_agent()

    def _build_agent(self):
        memory = ConversationBufferMemory(
            chat_memory=RedisChatMessageHistory(
                session_id=f"chat:{self.user_id}", url=self.redis_url, ttl=200
            ),
            memory_key="chat_history",
            return_messages=True,
        )

        llm = ChatOpenAI(temperature=0, openai_api_key=self.openai_api_key)

        tools = [
            answer_bank_faq
        ]

        return initialize_agent(
            tools=tools,
            llm=llm,
            memory=memory,
            agent=AgentType.OPENAI_FUNCTIONS,
            verbose=True,
        )

    async def run(self, user_input: str) -> str:
        return self.agent.invoke({"input": user_input})
