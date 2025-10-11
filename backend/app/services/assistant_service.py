"""
AuraQuant - AI Research Assistant Service
"""
import logging
from langchain_ollama.llms import OllamaLLM
from langchain import hub
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate

from app.llm_tools.tool_definitions import llm_tools

logger = logging.getLogger(__name__)


class AssistantService:
    def __init__(self):
        self.agent_executor = None
        self._initialize_agent()

    def _initialize_agent(self):
        """
        Initializes the LangChain agent with the LLM and our custom tools.
        """
        try:
            logger.info("Initializing AI Research Assistant Agent...")
            # This points to a local Ollama instance running a model like llama3
            llm = OllamaLLM(model="llama3", temperature=0)

            # The "ReAct" (Reasoning and Acting) prompt template tells the LLM how to
            # think step-by-step and use the available tools.
            prompt = hub.pull("hwchase17/react")

            # The agent is the core reasoning engine.
            agent = create_react_agent(llm, llm_tools, prompt)

            # The executor is what actually runs the agent and its tools.
            # `verbose=True` is great for debugging, as it prints the LLM's "thoughts".
            self.agent_executor = AgentExecutor(agent=agent, tools=llm_tools, verbose=True)
            logger.info("AI Research Assistant Agent initialized successfully.")

        except Exception as e:
            logger.error(f"FATAL: Could not initialize LangChain agent. Assistant will be disabled. Error: {e}")

    async def get_response(self, user_query: str, user_id: int) -> str:
        """
        Gets a response from the AI assistant for a given user query.
        """
        if not self.agent_executor:
            return "I'm sorry, the AI Assistant is currently offline."

        try:
            # We invoke the agent executor, which starts the reasoning loop.
            # The LLM will see the query, decide which tool to use (if any),
            # get the result from the tool, and then use that result to
            # formulate a final human-readable answer.
            response = await self.agent_executor.ainvoke({
                "input": user_query,
                # In a multi-user system, you'd also pass a session_id for conversation history
            })
            return response.get("output", "I'm sorry, I encountered an error.")
        except Exception as e:
            logger.error(f"Error invoking AI assistant: {e}")
            return "An error occurred while processing your request."


assistant_service = AssistantService()