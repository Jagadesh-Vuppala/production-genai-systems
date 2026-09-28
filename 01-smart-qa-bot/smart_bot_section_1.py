import os
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel,Field
from langchain_core.prompts import ChatPromptTemplate
from langsmith import traceable
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage


load_dotenv()


class QAResponse(BaseModel):
    answer : str = Field(description="The crisp to the user's question")
    confidence : str = Field(description="Confidence level: high,medium, or low")
    reasoning : str = Field(description= "The reason behind the answer provided")
    follow_up_questions : list[str] = Field(description="Suggested follow-up questions related to the topic. ",
                                                        default_factory=list)
    sources_needed: bool = Field(description="Whether external sources are need to verify this answer. ",
                                    default=False

        
    ) 

class SmartQABot:
    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.3):

        openai_llm = ChatOpenAI(model=model_name,temperature=temperature)
        anthropic_llm = ChatOpenAI(model="claude-haiku-4-5-20251001",temperature=temperature)
        resilient_llm = openai_llm.with_fallbacks([anthropic_llm])


        self.model = resilient_llm.with_structured_output(QAResponse)

        self.chat_history = []

        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system","You are a knowledgeable Q&A assistant. Always respond accurately, state your confidence, provide clear reasoning, and suggest relevant follow-up questions."),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human","{question}")
            ]
        )


        self.chain = self.prompt | self.model

    
    @traceable(name="ask_question",run_type="chain")
    def ask(self, question: str) -> QAResponse:
        try:
            # 1. Memory ni invoke lo pass chestunnam
            response = self.chain.invoke({
                "question": question,
                "chat_history": self.chat_history
            })
            
            # 2. Next turn kosam memory lo save chestunnam!
            self.chat_history.append(HumanMessage(content=question))
            self.chat_history.append(AIMessage(content=response.answer))
            
            return response
        except Exception as e:
            # Crash avvadu! Fallback object return chestundi:
            return QAResponse(
                answer="I'm sorry, I couldn't process your question at this time.",
                confidence="low",
                reasoning=f"Handled error: {str(e)}",
                follow_up_questions=["Could you please try again later or rephrase?"],
                sources_needed=True
            )


if __name__ == "__main__":
    bot = SmartQABot()
    print("=" * 60)
    print("🤖 SMART Q&A BOT (Type 'quit' to exit)")
    print("=" * 60)

    last_follow_ups = []

    while True:
        user_input = input("\n👉 You: ").strip()

        if not user_input:
            continue
        if user_input.lower() in ["quit", "exit","q"]:
            print("Bye mawa! 👋")
            break

        # 💡 User just '1' or '2' type chesthe, suggested question ni pick chesko:
        if user_input.isdigit() and 1 <= int(user_input) <= len(last_follow_ups):
            question = last_follow_ups[int(user_input) - 1]
            print(f"👉 Selected Follow-up: {question}")
        else:
            question = user_input

        # Bot execution
        res = bot.ask(question)

        print(f"\n💡 Answer     : {res.answer}")
        print(f"📊 Confidence : {res.confidence}")
        print(f"🧠 Reasoning  : {res.reasoning}")

        # Follow-up Suggestions display
        last_follow_ups = res.follow_up_questions
        if last_follow_ups:
            print("\n🔍 Suggested Follow-ups (Type number to ask):")
            for idx, fq in enumerate(last_follow_ups, 1):
                print(f"   [{idx}] {fq}")
