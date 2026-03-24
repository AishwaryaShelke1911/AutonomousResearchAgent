from langchain_ollama import OllamaLLM
from langchain.agents import initialize_agent, AgentType
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

# Load LLM (LOCAL - no API key)
llm = OllamaLLM(model="phi3")

# Tools
search_tool = DuckDuckGoSearchRun()

wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())

tools = [search_tool, wiki]

# Initialize Agent (ReAct)
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True
)

def research_topic(topic):
    prompt = f"""
    Research the topic: {topic}

    Do the following:
    1. Search relevant information
    2. Extract key insights
    3. Summarize properly
    4. Prepare structured content
    """

    result = agent.run(prompt)
    return result


if __name__ == "__main__":
    topic = input("Enter Topic: ")
    output = research_topic(topic)

    print("\n===== RAW RESEARCH OUTPUT =====\n")
    print(output)