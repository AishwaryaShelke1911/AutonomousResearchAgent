# 🤖 Autonomous Research Agent (LangChain)

An AI-powered research agent that automatically searches, analyzes, and generates structured reports on any topic.

## Architecture

```
User Input (Topic)
       │
       ▼
┌─────────────────────┐
│  ReAct Agent Loop   │
│  ┌───────────────┐  │
│  │  WebSearch    │  │  ← Tool 1: DuckDuckGo live web search
│  │  (DuckDuckGo) │  │
│  └───────────────┘  │
│  ┌───────────────┐  │
│  │  Wikipedia    │  │  ← Tool 2: Wikipedia knowledge base
│  │  Knowledge    │  │
│  └───────────────┘  │
└─────────────────────┘
       │
       ▼
  Research Data (JSON)
       │
       ▼
 Report Generator
 (Claude LLM chain)
       │
       ▼
 Structured Report (.md)
```

## Setup

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd research_agent
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Key
```bash
cp .env.example .env
# Edit .env and add your Anthropic API key
```

### 4. Run the agent
```bash
# Default topic
python research_agent.py

# Custom topic
python research_agent.py --topic "Quantum Computing Applications"

# Without saving to file
python research_agent.py --topic "Climate Change" --no-save
```

## Output Format

Reports are saved to `sample_outputs/` as `.md` files and include:

| Section | Description |
|---|---|
| **Cover Page** | Title, date, tools used |
| **Introduction** | Topic overview and significance |
| **Key Findings** | 5-7 detailed research findings |
| **Challenges** | 4-6 real-world challenges |
| **Future Scope** | 4-6 future directions |
| **Conclusion** | Summary and takeaways |
| **References** | Sources found during research |

## Tools Used

| Tool | Purpose | Source |
|---|---|---|
| `WebSearch` | Live web search | DuckDuckGo (free, no API key) |
| `Wikipedia` | Encyclopedic knowledge | Wikipedia API (free) |

## Agent Type
- **ReAct (Reasoning + Acting)** agent pattern
- Iterates up to 8 times, combining search results before generating the final report
- Uses Claude 3.5 Sonnet as the underlying LLM

## Sample Output Topics
- `Impact of AI in Healthcare`
- `Renewable Energy Trends 2025`

See `sample_outputs/` for pre-generated example reports.
