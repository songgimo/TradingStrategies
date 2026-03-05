import json
from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate
)
from src.config.config import STATIC_FOLDER_PATH


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


def create_strategy_generator_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages([
        ("system", "You are an expert quantitative trading strategist. "
                   "Given a candidate stock with its technical context and recent market sentiment, "
                   "generate a concrete trading strategy. "
                   "Determine whether to LONG, SHORT, or CASH_HOLD, and provide realistic entry price, "
                   "take profit, and stop loss levels (in the correct currency). "
                   "Use the provided format strictly."),
        ("human", "Candidate Stock and Context:\n{context_data}\n\n{format_instructions}")
    ])

def create_risk_manager_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages([
        ("system", "You are a strict Risk Manager for a trading fund. "
                   "Review the proposed trading strategy and filter out or adjust if it carries excessive risk. "
                   "Consider technical context and broader market sentiment. "
                   "If risk is too high or reward is too low, change action to CASH_HOLD or adjust stop_loss. "
                   "Use the provided format strictly to output the validated strategy."),
        ("human", "Proposed Strategy:\n{strategy_data}\n\nContext Context:\n{market_context}\n\n{format_instructions}")
    ])
