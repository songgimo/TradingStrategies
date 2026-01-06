import json
from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate
)
from config.config import STATIC_FOLDER_PATH


def create_analyst_prompt() -> ChatPromptTemplate:
    example_prompt = ChatPromptTemplate.from_messages([
        ("human", "{input}",),
        ("ai", "{output}")
    ])

    with open(STATIC_FOLDER_PATH / "llm_templates/market_analysis.json", "r") as f:
        raw = json.loads(f.read())

    examples = []
    for ex in raw:
        examples.append({
            "input": ex["input"],
            "output": json.dumps(ex["output"], ensure_ascii=False)
        })

    few_shot = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=examples,
    )

    final_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a professional market analyst. Use Chain-of-Thought reasoning."),
        few_shot,
        ("human", "Analyze the following news:\n{news_data}\n\n{format_instructions}")
    ])

    return final_prompt
