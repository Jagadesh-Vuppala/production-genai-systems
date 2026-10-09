import pathlib
from langchain.agents import create_agent
from langgraph.graph import add_messages
import operator
from dotenv import load_dotenv; load_dotenv()
from typing_extensions import TypedDict,Annotated,Literal
from pydantic import BaseModel , Field
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph,START,END
from langchain_core.messages import SystemMessage,AIMessage,HumanMessage,BaseMessage,ToolMessage
from langchain_core.tools import tool
from ddgs import DDGS
import requests
from bs4 import BeautifulSoup
from langgraph.prebuilt import create_react_agent
import sys
from datetime import datetime


if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')


smart_llm = ChatOpenAI(model="gpt-5.4-mini-2026-03-17")
Goat_llm = ChatOpenAI(model="gpt-6-astra")
    


class FinancialState(TypedDict):
    salary : int 
    risk_score : float
    existing_debt : int 
    can_invest : int
    messages : Annotated[list[BaseMessage],add_messages]
    insurance_plan : str
    investment_plan :str
    tax_plan :str
    final_blueprint: str
    qc_score: int
    qc_feedback: str
    iteration:int 
    insurance_budget: int
    investment_budget: int
    age: int       


@tool
def search_web(query: str) -> str:
    """Search live web for latest 2026 financial, tax, insurance, and investment facts in India."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
    try:
        resp = requests.get(url, headers=headers, timeout=6)
        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.find_all("div", class_="result")[:3]
        
        extracted = []
        for item in items:
            title = item.find("a", class_="result__a")
            snippet = item.find("a", class_="result__snippet")
            if title and snippet:
                extracted.append(f"Title: {title.get_text(strip=True)}\nSnippet: {snippet.get_text(strip=True)}")
        
        return "\n\n".join(extracted) if extracted else "No live results found."
    except Exception as e:
        return f"Search error: {str(e)}"



def supervisor_node(state: FinancialState) -> dict:
    # 1. Input Extraction:
    salary = state["salary"]
    age = state["age"]
    debt = state["existing_debt"]
    
    # 2. 50-20-30 CFP Cashflow Math:
    needs = int(salary * 0.5)
    wants = int(salary * 0.2)
    can_invest = salary - (needs + wants + debt)
    
    # 3. Dynamic Budget Allocation (Zero-budget trap fix):
    insurance_budget = int(can_invest * 0.15)
    investment_budget = can_invest - insurance_budget
    
    # Pro Debug Print:
    print(f"\n[Supervisor] ==> Surplus: Rs.{can_invest} | Insurance: Rs.{insurance_budget} | Investment: Rs.{investment_budget}")
    
    # 4. State Inspection for Revision vs Baseline Mode:
    qc_feedback = state.get("qc_feedback", "")
    iteration = state.get("iteration", 0)

    if qc_feedback:
        # Revision Mode: QC Auditor reject chesinappudu
        prompt = (
            f"You are Lead Supervisor in REVISION MODE (Iteration {iteration + 1}).\n"
            f"Auditor Feedback: '{qc_feedback}'.\n"
            f"Profile: Age {age}, Salary Rs.{salary}, Surplus Rs.{can_invest}.\n"
            f"Enforce Insurance Cap: Rs.{insurance_budget}, Investment Target: Rs.{investment_budget}.\n"
            f"Direct specialists to fix gaps immediately!"
        )
    else:
        # Baseline Mode: Initial run
        prompt = (
            f"You are Lead Financial Supervisor (Baseline Planning).\n"
            f"Client: Age {age}, Salary Rs.{salary}, Debt Rs.{debt}.\n"
            f"Needs: Rs.{needs}, Wants: Rs.{wants}, Surplus: Rs.{can_invest}/mo.\n"
            f"Allocated Budgets ==> Insurance Cap: Rs.{insurance_budget}/mo | Investment Target: Rs.{investment_budget}/mo.\n"
            f"Issue directives to Insurance, Investment, and Tax specialists."
        )

    output = Goat_llm.invoke(prompt)
    output.name = "supervisor"
    
    # 5. State Return with Allocated Budgets:
    return {
        "can_invest": can_invest,
        "insurance_budget": insurance_budget,
        "investment_budget": investment_budget,
        "iteration": iteration + 1 if qc_feedback else iteration,
        "messages": [output]
    }


class InsuranceOutput(BaseModel):
    term_plan_name: str = Field(description="Best Term Insurance plan name (e.g. HDFC Life Click 2 Protect Super)")
    term_cover: str = Field(description="Term cover sum assured determined for this budget, e.g. '75 Lakhs' or '1 Crore'")
    term_premium: int = Field(description="Exact monthly premium for the term plan in rupees")
    
    health_plan_name: str = Field(description="Best Health Insurance plan name (e.g. Care Supreme, Niva Bupa ReAssure 2.0)")
    health_cover: str = Field(description="Health cover sum assured determined for this budget, e.g. '5 Lakhs' or '10 Lakhs'")
    health_premium: int = Field(description="Exact monthly premium for the health plan in rupees")
    
    monthly_premium: int = Field(description="Total combined monthly premium (term + health) in rupees")
    reasoning: str = Field(description="Crisp 2-line CFP reasoning explaining why this cover size fits client profile & budget")




def insurance_node(state: FinancialState) -> dict:
    age = state["age"] 
    salary = state["salary"] 
    annual_income = salary * 12
    max_insurance_ceiling = state["insurance_budget"]
    insurance_agent = create_agent(smart_llm, tools=[search_web])
    prompt = (
        f"You are a CFP Senior Insurance Specialist.\n"
        f"Client Profile: Age {age}, Annual Income: Rs.{annual_income} (Monthly: Rs.{salary}).\n"
        f"STRICT MONTHLY BUDGET CEILING: Total combined premium MUST be under Rs.{max_insurance_ceiling}/month!\n\n"
        f"Autonomous Sizing Mandates:\n"
        f"1. Autonomously size the ideal Term Insurance cover (CFP benchmark: 10x-15x annual salary) "
        f"and Health Insurance cover that fit comfortably within the Rs.{max_insurance_ceiling}/mo budget.\n"
        f"2. Use live web search to find top 2026 plans in India with high CSR (>98%).\n"
        f"3. Provide REAL policy names, determined cover amounts, and realistic integer monthly premiums.\n"
        f"4. NEVER say quotes are pending. Return actionable concrete numbers."
    )
    res = insurance_agent.invoke({"messages": [HumanMessage(content=prompt)]})
    raw_result = res["messages"][-1].content
    extractor = smart_llm.with_structured_output(InsuranceOutput)
    structured_data = extractor.invoke(
        f"Extract the plan names, cover amounts, and integer monthly premiums in rupees from this research:\n{raw_result}"
    )
    # Defensive Guardrail: Ensure non-zero realistic cost
    cost = structured_data.monthly_premium
    if cost == 0 and (structured_data.term_premium + structured_data.health_premium) > 0:
        cost = structured_data.term_premium + structured_data.health_premium
    if cost <= 0:
        term_fallback = min(900, max_insurance_ceiling // 2)
        health_fallback = min(650, max_insurance_ceiling // 2)
        cost = term_fallback + health_fallback
        structured_data.term_premium = term_fallback
        structured_data.health_premium = health_fallback
        structured_data.monthly_premium = cost
    details = (
        f"1. Term Insurance: {structured_data.term_plan_name} ({structured_data.term_cover} Cover) @ Rs.{structured_data.term_premium}/mo\n"
        f"2. Health Insurance: {structured_data.health_plan_name} ({structured_data.health_cover} Cover) @ Rs.{structured_data.health_premium}/mo\n"
        f"Why These Plans: {structured_data.reasoning}"
    )
    print(details)
    
    return {
        "insurance_plan": details,
        "insurance_budget": cost,
        "messages": [AIMessage(content=f"[Insurance Plan (Rs.{cost}/mo)]:\n{details}")]
    }



class SpecificFund(BaseModel):
    fund_name: str = Field(description="Real actual market fund name (e.g. 'Parag Parikh Flexi Cap Fund', 'Motilal Oswal Midcap Fund', 'Nippon India Gold ETF'). NEVER use placeholder names like 'Fund A' or 'Fund B'!")
    monthly_amount: int = Field(description="Monthly SIP amount in rupees")


class AssetCategory(BaseModel):
    category_name: str = Field(description="Category: Equity, Gold ETF, Debt/PPF, or NPS")
    total_amount: int = Field(description="Total rupees in this category")
    funds: list[SpecificFund] = Field(description="List of specific funds/instruments under this category")

class investmentoutput(BaseModel):
    categories : list[AssetCategory] = Field(description="Diversified categories breakdown")
    total_investment: int = Field(description="Total investment in rupees(must match the investment_budget)")
    strategy_reasoning :str =Field(description="CFP rationale")


def investment_node(state:FinancialState) -> dict:
    investment_budget =  int(state["can_invest"]-state["insurance_budget"])
    risk = state["risk_score"]
    age =state["age"]

    investment_agent = create_agent(smart_llm,tools= [search_web])
    prompt = (
        f"You are a Certified Financial Planner (CFP) Senior Wealth & Investment Specialist.\n"
        f"Client Profile: Age {age}, Risk Appetite: {risk}/10 "
        f"(Scale: 0/10 = Ultra-Conservative Capital Preservation like Debt/FD/PPF, "
        f"5/10 = Balanced Growth, 10/10 = Maximum Aggressive Equity Growth).\n"
        f"Monthly Investment Budget: EXACTLY Rs.{investment_budget}/month.\n\n"
        f"Your Autonomous Mandates:\n"
        f"1. Interpret the client's Risk Score ({risk}/10) and autonomously determine the ideal Asset Allocation percentage.\n"
        f"2. Use your live web search tool to find the top real-world 2026 instruments in India matching this specific risk level "
        f"(e.g. search safe FDs/PPF/Debt if low risk; search top Flexicap/Midcap equity if high risk; Gold ETFs for hedge).\n"
        f"3. The total sum across all categories MUST EXACTLY equal Rs.{investment_budget}/month.\n"
        f"4. MANDATORY: For every category, provide REAL, SPECIFIC instrument names. Never leave fund names empty!"
    )



    res = investment_agent.invoke({
        "messages": state.get("messages", []) + [HumanMessage(content=prompt)]
    })


    raw_results =  res["messages"][-1].content


    extractor = smart_llm.with_structured_output(investmentoutput)
    structured_data = extractor.invoke(
        f"Extract the investment categories, specific funds, and amounts from this research:\n{raw_results}"
    )





    plan_lines = []
    for cat in structured_data.categories:
        plan_lines.append(f"[{cat.category_name}] --Rs.[{cat.total_amount}/mo]")
        for f in cat.funds:
            plan_lines.append(f"   -{f.fund_name} : Rs[{f.monthly_amount}/mo]")
    
    plan_lines.append(f"Total Allocation: Rs.{structured_data.total_investment}")
    plan_lines.append(f"stratergy: Rs.{structured_data.strategy_reasoning}")

    details = "\n".join(plan_lines)
    actual_invested = structured_data.total_investment

    print(f"\n[Investment Specialist] ==> Portfolio Assembled: Rs.{actual_invested}/month across {len(structured_data.categories)} Asset Classes")

    return {
        "investment_plan": details,
        "investment_budget": actual_invested,
        "messages": [AIMessage(content=f"[Investment Portfolio (Rs.{actual_invested}/mo)]:\n{details}")]
    }


class TaxOutput(BaseModel):
    regime_recommended: str = Field(description="Recommended tax regime (old/new) along with applicable year")
    gross_salary: int = Field(description="Annual gross salary (monthly salary × 12)")
    standard_deduction: int = Field(description="Standard deduction allowed under the chosen regime")
    taxable_income: int = Field(description="Total taxable income after deductions under the chosen regime")
    final_tax_payable: int = Field(description="Net tax liability to be paid")
    tax_saving_explanation: str = Field(description="Explanation of tax calculations, applicable sections, and savings logic")

   

def tax_node(state: FinancialState) -> dict:
    monthly_salary = state["salary"]
    annual_salary = monthly_salary * 12

    tax_agent = create_agent(smart_llm, tools=[search_web])

    prompt = (
        f"You are a Certified Financial Planner (CFP) Senior Tax Specialist for India.\n"
        f"Client Profile: Gross Annual Salary: Rs.{annual_salary} (Rs.{monthly_salary}/month).\n\n"
        f"Your Autonomous Responsibilities:\n"
        f"1. Use your live web search tool to find the latest 2026 Union Budget income tax slabs, "
        f"applicable standard deduction, and Section 87A rebate limits for India.\n"
        f"2. Compare Old Tax Regime vs New Tax Regime for this exact income (Rs.{annual_salary}) "
        f"and determine the most beneficial regime for the client.\n"
        f"3. Calculate the exact standard deduction, resulting taxable income, and net tax liability.\n"
        f"4. Detail whether Section 87A rebate or threshold exemptions reduce the final tax payable to Rs.0.\n"
        f"5. Provide a clear tax optimization summary explaining the full calculation breakdown."
    )

    res = tax_agent.invoke({
        "messages": state.get("messages", []) + [HumanMessage(content=prompt)]
    })
    raw_results = res["messages"][-1].content

    extractor = smart_llm.with_structured_output(TaxOutput)
    structured_data = extractor.invoke(
        f"Extract the regime recommendations, standard deduction, taxable income, and final tax payable from this research:\n{raw_results}"
    )

    tax_plan = (
        f"--- Tax Plan Summary ---\n"
        f"Regime Recommended: {structured_data.regime_recommended}\n"
        f"Gross Salary: Rs.{structured_data.gross_salary}\n"
        f"Standard Deduction: Rs.{structured_data.standard_deduction}\n"
        f"Taxable Income: Rs.{structured_data.taxable_income}\n"
        f"Final Tax Payable: Rs.{structured_data.final_tax_payable}\n"
        f"CFP Tax Strategy: {structured_data.tax_saving_explanation}\n"
        f"-------------------------"
    )

    print(f"\n[Tax Specialist] ==> Regime: {structured_data.regime_recommended} | Final Tax: Rs.{structured_data.final_tax_payable}")

    return {
        "tax_plan": tax_plan,
        "messages": [AIMessage(content=f"[Tax Strategy (Rs.{structured_data.final_tax_payable} Tax)]:\n{tax_plan}")]
    }


def synthesizer_node(state: FinancialState) -> dict:
    salary = state["salary"]
    debt = state["existing_debt"]
    age = state["age"]
    risk = state["risk_score"]
    insurance_plan = state["insurance_plan"]
    insurance_budget = state["insurance_budget"]
    investment_plan = state["investment_plan"]
    investment_budget = state["investment_budget"]
    tax_plan = state["tax_plan"]

    needs = int(salary * 0.5)
    wants = int(salary * 0.2)

    prompt = (
        f"You are the Chief Financial Planner (CFP) creating the final Wealth Blueprint for the client.\n\n"
        f"Client Profile:\n"
        f"- Age: {age} | Monthly In-Hand Salary: Rs.{salary} (Annual: Rs.{salary * 12})\n"
        f"- Existing Debt EMI: Rs.{debt}/month | Risk Appetite: {risk}/10\n\n"
        f"Specialist Inputs:\n"
        f"1. Safety Net (Insurance Budget: Rs.{insurance_budget}/mo):\n{insurance_plan}\n\n"
        f"2. Wealth Creation (Investment Budget: Rs.{investment_budget}/mo):\n{investment_plan}\n\n"
        f"3. Tax Optimization:\n{tax_plan}\n\n"
        f"Task: Synthesize a professional, comprehensive, CFP-grade Markdown Financial Blueprint with:\n"
        f"1. Executive Summary & Client Snapshot\n"
        f"2. Complete Monthly Cashflow Budget Table (Needs Rs.{needs} + Wants Rs.{wants} + Debt EMI Rs.{debt} + Insurance Rs.{insurance_budget} + Investments Rs.{investment_budget} = EXACTLY Rs.{salary})\n"
        f"3. Risk & Protection Roadmap (Insurance picks & rationales)\n"
        f"4. Wealth Multi-Asset Portfolio (Detailed SIP breakdown & long-term projections)\n"
        f"5. Tax Strategy (New Regime savings & zero-tax confirmation)\n"
        f"6. Month-1 Immediate Action Checklist\n"
        f"Use clean markdown formatting, headers, and bullet points."
    )

    res = Goat_llm.invoke(state.get("messages", []) + [HumanMessage(content=prompt)])
    final_blueprint = res.content

    print(f"\n[Synthesizer] ==> Grand 2026 Wealth Blueprint Compiled ({len(final_blueprint)} chars)")

    return {
        "final_blueprint": final_blueprint,
        "messages": [AIMessage(content=f"[Synthesizer]: Grand 2026 Wealth Blueprint Compiled!\n\n{final_blueprint}")]
    }

class QCAuditResult(BaseModel):
    score: int = Field(description="Quality and compliance score from 1 to 10 (8+ is Pass)")
    is_approved: bool = Field(description="True if blueprint is compliant and budget matches salary")
    feedback: str = Field(description="Specific feedback or recommendations for improvement")

def qc_auditor_node(state: FinancialState) -> dict:
    salary = state["salary"]
    needs = int(salary * 0.5)
    wants = int(salary * 0.2)
    debt = state["existing_debt"]
    ins = state["insurance_budget"]
    inv = state["investment_budget"]
    
    # 1. Deterministic Math Check:
    total_allocated = needs + wants + debt + ins + inv
    math_delta = salary - total_allocated
    math_ok = abs(math_delta) <= 100
    # 2. LLM Quality Audit:
    blueprint = state["final_blueprint"]
    prompt = (
        f"You are the Chief QC Auditor & Compliance Officer for a wealth advisory firm.\n"
        f"Audit this Financial Blueprint against strict CFP standards:\n"
        f"1. Math Balance Check: Salary: Rs.{salary} vs Total Accounted: Rs.{total_allocated} (Delta: Rs.{math_delta}). Math Valid: {math_ok}.\n"
        f"2. Safety Net Check: Is Term and Health insurance clearly detailed with real plan names?\n"
        f"3. Wealth Check: Is multi-asset investment allocated without missing funds?\n"
        f"4. Tax Check: Is New Tax Regime zero-tax confirmed?\n\n"
        f"Blueprint to Audit:\n{blueprint}\n\n"
        f"Rate the plan from 1 to 10. If Math Valid is False, score MUST NOT exceed 5."
    )
    extractor = smart_llm.with_structured_output(QCAuditResult)
    audit = extractor.invoke(prompt)
    final_score = audit.score if math_ok else min(audit.score, 5)
    print(f"\n[QC Auditor] ==> Score: {final_score}/10 | Math Balanced: {math_ok} (Delta: Rs.{math_delta})")
    print(f"[QC Auditor Feedback]: {audit.feedback}\n")
    return {
        "qc_score": final_score,
        "qc_feedback": audit.feedback,
        "messages": [AIMessage(content=f"[QC Audit (Score: {final_score}/10)]:\n{audit.feedback}")]
    }

def route_qc_verdict(state: FinancialState) -> str:
    if state["qc_score"] >= 7 or state.get("iteration", 0) >= 1:
        return "approved"
    return "revise"


workflow = StateGraph(FinancialState)

workflow.add_node("supervisor", supervisor_node)
workflow.add_node("insurance", insurance_node)
workflow.add_node("investment", investment_node)
workflow.add_node("tax", tax_node)
workflow.add_node("synthesizer", synthesizer_node)
workflow.add_node("qc_auditor", qc_auditor_node)


workflow.add_edge(START, "supervisor")
workflow.add_edge("supervisor", "insurance")

# Symmetric 1-Hop Fan-Out:
workflow.add_edge("insurance", "investment")
workflow.add_edge("insurance", "tax")

# Symmetric Fan-In to Synthesizer:
workflow.add_edge("investment", "synthesizer")
workflow.add_edge("tax", "synthesizer")

workflow.add_edge("synthesizer", "qc_auditor")


workflow.add_conditional_edges("qc_auditor", route_qc_verdict, {
    "approved": END,
    "revise": "supervisor"
})

app = workflow.compile()


if __name__ == "__main__":
    # 1. Mermaid Graph Diagram PNG Save:
    image_loc = str(pathlib.Path(__file__).parent /"financial_advisor_graph.png")

    try:
        with open(image_loc, "wb") as f:
            f.write(app.get_graph().draw_mermaid_png())
        print("\n[Architecture Diagram Saved] ==> financial_advisor_graph.png")
    except Exception as e:
        print(f"Graph image export note: {e}")

    # 2. Candidate Profile Setup:
    candidate_input: FinancialState = {
        "age": 26,
        "salary": 64000,
        "existing_debt": 0,
        "risk_score": 7.0,
        "can_invest": 0,
        "insurance_budget": 0,
        "investment_budget": 0,
        "insurance_plan": "",
        "investment_plan": "",
        "tax_plan": "",
        "final_blueprint": "",
        "qc_score": 0,
        "qc_feedback": "",
        "iteration": 0,
        "messages": []
    }

    print("\n" + "="*60)
    print(">>> LAUNCHING AUTONOMOUS CFP WEALTH ADVISORY SYSTEM (2026)")
    print("="*60)

    # 3. Graph Invocation:
    final_state = app.invoke(candidate_input)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"WEALTH_BLUEPRINT_{timestamp}.md"
    file_loc = str(pathlib.Path(__file__).parent / filename)


    # 4. Save Final Blueprint Markdown File:
        # 4. Save Final Blueprint Markdown File:
    with open(file_loc, "w", encoding="utf-8") as f:
        f.write(final_state["final_blueprint"])

    print("\n" + "="*60)
    print(">>> 2026 CFP WEALTH BLUEPRINT GENERATED SUCCESSFULLY!")
    print(f">>> File Saved: {filename}")
    print(f">>> Final QC Score: {final_state['qc_score']}/10")
    print("="*60)

