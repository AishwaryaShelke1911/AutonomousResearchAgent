"""
Autonomous Research Agent using LangChain
Assignment 2 - AI Research Agent
"""

import os
import json
import datetime
from dotenv import load_dotenv

# LangChain imports
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()


# ─────────────────────────────────────────────
# 1. LLM Setup
# ─────────────────────────────────────────────
def get_llm():
    """Initialize the LLM (Anthropic Claude)."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY not found. Please set it in your .env file.\n"
            "Get your key at: https://console.anthropic.com/"
        )
    return ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        anthropic_api_key=api_key,
        temperature=0.3,
        max_tokens=4096,
    )


# ─────────────────────────────────────────────
# 2. Tool Definitions
# ─────────────────────────────────────────────
def build_tools() -> list:
    """Build and return the list of tools for the agent."""

    # Tool 1 – Web Search (DuckDuckGo)
    search = DuckDuckGoSearchRun()
    web_search_tool = Tool(
        name="WebSearch",
        func=search.run,
        description=(
            "Search the web for current information on a topic. "
            "Use this to find recent news, statistics, research papers, "
            "and expert opinions. Input: a search query string."
        ),
    )

    # Tool 2 – Wikipedia Knowledge Tool
    wiki_wrapper = WikipediaAPIWrapper(top_k_results=3, doc_content_chars_max=4000)
    wiki_tool = WikipediaQueryRun(api_wrapper=wiki_wrapper)
    wikipedia_tool = Tool(
        name="Wikipedia",
        func=wiki_tool.run,
        description=(
            "Query Wikipedia for encyclopedic knowledge about a topic. "
            "Great for background information, definitions, history, and "
            "established facts. Input: a topic or question string."
        ),
    )

    return [web_search_tool, wikipedia_tool]


# ─────────────────────────────────────────────
# 3. ReAct Agent Prompt
# ─────────────────────────────────────────────
REACT_PROMPT_TEMPLATE = """You are an expert research agent. Your task is to thoroughly research the given topic and collect comprehensive information.

You have access to the following tools:
{tools}

Use the following format EXACTLY:

Question: the input question you must answer
Thought: think about what to do next
Action: the action to take, must be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat up to 6 times)
Thought: I now have enough information to compile a report
Final Answer: [RESEARCH_COMPLETE] followed by a JSON summary with keys: overview, key_findings (list of 5+ findings), challenges (list of 4+ challenges), future_scope (list of 4+ future directions), statistics (list of notable stats/facts), experts_and_sources (list of sources/references found)

Begin!

Question: Research the topic thoroughly: {input}
{agent_scratchpad}"""

REACT_PROMPT = PromptTemplate(
    input_variables=["tools", "tool_names", "input", "agent_scratchpad"],
    template=REACT_PROMPT_TEMPLATE,
)


# ─────────────────────────────────────────────
# 4. Report Generation
# ─────────────────────────────────────────────
REPORT_PROMPT = PromptTemplate(
    input_variables=["topic", "research_data", "current_date"],
    template="""You are a professional technical report writer. Based on the research data provided, write a comprehensive, well-structured report.

Topic: {topic}
Research Data: {research_data}
Date: {current_date}

Write a detailed report in the following EXACT structure. Use clear, professional language.

---REPORT_START---

# {topic}
### A Comprehensive Research Report

**Prepared by:** Autonomous Research Agent (LangChain + Claude)
**Date:** {current_date}
**Research Tools Used:** Web Search (DuckDuckGo), Knowledge Base (Wikipedia)

---

## Introduction

[Write 3-4 paragraphs introducing the topic, its significance, and why it matters today.]

---

## Key Findings

[Write 5-7 detailed key findings. Each should be a numbered paragraph with specific details.]

---

## Challenges

[Write 4-6 major challenges. Each numbered, with real-world implications.]

---

## Future Scope

[Write 4-6 future directions and opportunities. Be specific. Number them.]

---

## Conclusion

[Write 2-3 paragraphs summarizing the research and key takeaways.]

---

## References & Sources

[List the sources and references found during research]

---REPORT_END---
""",
)


# ─────────────────────────────────────────────
# 5. Main Research Agent Class
# ─────────────────────────────────────────────
class AutonomousResearchAgent:
    """
    Autonomous agent that researches a topic using web search
    and Wikipedia, then generates a structured report.
    """

    def __init__(self):
        print("Initializing Autonomous Research Agent...")
        self.llm = get_llm()
        self.tools = build_tools()
        self.agent = create_react_agent(self.llm, self.tools, REACT_PROMPT)
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=8,
            handle_parsing_errors=True,
            return_intermediate_steps=True,
        )
        self.report_chain = REPORT_PROMPT | self.llm | StrOutputParser()
        print("Agent initialized successfully!\n")

    def research(self, topic: str) -> dict:
        """Run the research agent on the given topic."""
        print(f"Starting research on: '{topic}'")
        result = self.agent_executor.invoke({"input": topic})
        raw_output = result.get("output", "")
        return self._parse_research_data(raw_output, topic)

    def _parse_research_data(self, raw_output: str, topic: str) -> dict:
        """Parse structured research data from agent output."""
        try:
            start = raw_output.find("{")
            end = raw_output.rfind("}") + 1
            if start != -1 and end > start:
                json_str = raw_output[start:end]
                return json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            pass
        return {
            "overview": raw_output,
            "key_findings": [],
            "challenges": [],
            "future_scope": [],
            "statistics": [],
            "experts_and_sources": [],
        }

    def generate_report(self, topic: str, research_data: dict) -> str:
        """Generate a formatted report from research data."""
        print("Generating structured report...")
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        report = self.report_chain.invoke({
            "topic": topic,
            "research_data": json.dumps(research_data, indent=2),
            "current_date": current_date,
        })
        return report.replace("---REPORT_START---", "").replace("---REPORT_END---", "").strip()

    def save_report(self, topic: str, report: str, output_dir: str = "sample_outputs") -> str:
        """Save the report to a markdown file."""
        os.makedirs(output_dir, exist_ok=True)
        safe_topic = topic.lower().replace(" ", "_").replace("/", "_")[:50]
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{output_dir}/report_{safe_topic}_{timestamp}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Report saved to: {filename}")
        return filename

    def run(self, topic: str, save: bool = True) -> str:
        """Full pipeline: research -> generate report -> optionally save."""
        print(f"\n{'='*60}")
        print(f"  AUTONOMOUS RESEARCH AGENT")
        print(f"  Topic: {topic}")
        print(f"{'='*60}\n")
        research_data = self.research(topic)
        report = self.generate_report(topic, research_data)
        if save:
            self.save_report(topic, report)
        return report


# ─────────────────────────────────────────────
# 6. Entry Point
# ─────────────────────────────────────────────
def main():
    import argparse
    parser = argparse.ArgumentParser(description="Autonomous Research Agent")
    parser.add_argument("--topic", type=str, default="Impact of AI in Healthcare",
                        help="Research topic")
    parser.add_argument("--no-save", action="store_true", help="Don't save report to file")
    args = parser.parse_args()

    agent = AutonomousResearchAgent()
    report = agent.run(topic=args.topic, save=not args.no_save)
    print("\n" + "="*60)
    print("FULL REPORT:")
    print("="*60)
    print(report)

if __name__ == "__main__":
    main()
