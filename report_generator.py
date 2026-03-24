from langchain_community.llms import Ollama

llm = Ollama(model="llama3")

def generate_report(topic, research_data):
    prompt = f"""
    Create a structured report on: {topic}

    Use the following format:

    Cover Page
    Title
    Introduction
    Key Findings
    Challenges
    Future Scope
    Conclusion

    Use this research data:
    {research_data}
    """

    report = llm.invoke(prompt)
    return report


if __name__ == "__main__":
    topic = input("Enter Topic: ")
    
    with open("research.txt", "r") as f:
        data = f.read()

    report = generate_report(topic, data)

    print("\n===== FINAL REPORT =====\n")
    print(report)