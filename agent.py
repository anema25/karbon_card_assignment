# agent.py

import argparse
import os
import pandas as pd
import pdfplumber
from typing import TypedDict, List
from pathlib import Path
from io import StringIO

from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END

from prompts import PLAN_PROMPT, CODE_GENERATION_PROMPT
from tools import run_parser_and_test

# --- Agent State Definition ---
class AgentState(TypedDict):
    target_bank: str
    pdf_path: Path
    csv_path: Path
    parser_path: Path
    pdf_text: str
    schema: str
    plan: str
    code: str
    test_result: str
    error_feedback: str
    attempt_count: int

# --- Agent Nodes ---
def plan_node(state: AgentState) -> AgentState:
    """Creates a plan to write the parser based on PDF text and schema."""
    print("--- 🧠 Planning ---")
    prompt = PLAN_PROMPT.format(
        pdf_text=state["pdf_text"],
        schema=state["schema"],
        error_feedback=state.get("error_feedback", "N/A"),
    )
    response = llm.invoke(prompt)
    state["plan"] = response.content
    state["attempt_count"] += 1
    print(f"Attempt #{state['attempt_count']} Plan:\n{state['plan']}")
    return state

def code_generation_node(state: AgentState) -> AgentState:
    """Generates Python code based on the plan."""
    print("--- 💻 Generating Code ---")
    prompt = CODE_GENERATION_PROMPT.format(plan=state["plan"])
    response = llm.invoke(prompt)
    # Clean up potential markdown formatting
    code = response.content.strip().replace("```python", "").replace("```", "")
    state["code"] = code
    print(f"Generated Code Snippet:\n{state['code'][:300]}...")
    return state

def test_code_node(state: AgentState) -> AgentState:
    """Tests the generated code against the ground-truth CSV."""
    print("--- 🧪 Testing Code ---")
    success, result = run_parser_and_test(
        parser_code=state["code"],
        parser_path=state["parser_path"],
        pdf_path=state["pdf_path"],
        csv_path=state["csv_path"],
    )
    state["test_result"] = result
    if not success:
        print(f"--- ❌ Test Failed ---\n{result}")
        state["error_feedback"] = result
    else:
        print(f"--- ✅ Test Passed ---\n{result}")
        # On success, write the final code to the file
        with open(state["parser_path"], "w") as f:
            f.write(state["code"])
        print(f"Successfully created parser at: {state['parser_path']}")
        state["error_feedback"] = "" # Clear feedback on success
    return state

# --- Conditional Logic ---
def should_continue(state: AgentState) -> str:
    """Determines whether to continue the loop or end."""
    MAX_ATTEMPTS = 3
    if state["error_feedback"] == "":
        return "end"  # Success
    if state["attempt_count"] >= MAX_ATTEMPTS:
        print(f"--- 🚫 Reached max attempts ({MAX_ATTEMPTS}). Halting. ---")
        return "end"
    return "continue"

# --- Main Agent Logic ---
def main():
    parser = argparse.ArgumentParser(description="AI Agent for generating bank statement parsers.")
    parser.add_argument(
        "--target",
        type=str,
        required=True,
        help="The target bank name (e.g., 'icici'). Expects a folder in `data/` with this name.",
    )
    args = parser.parse_args()

    target_bank = args.target
    data_dir = Path("data") / target_bank
    pdf_path = data_dir / f"{target_bank}_sample.pdf"
    csv_path = data_dir / f"{target_bank}_sample.csv"
    parser_path = Path("custom_parsers") / f"{target_bank}_parser.py"

    if not all([pdf_path.exists(), csv_path.exists()]):
        raise FileNotFoundError(f"Ensure {pdf_path} and {csv_path} exist.")

    print(f"--- 🚀 Starting Agent for: {target_bank.upper()} ---")

    # Initial context gathering
    with pdfplumber.open(pdf_path) as pdf:
        pdf_text = pdf.pages[0].extract_text() or ""
    
    # Use a StringIO buffer to capture the schema info
    buffer = StringIO()
    pd.read_csv(csv_path).info(buf=buffer)
    schema_str = buffer.getvalue()
    
    # Initialize the graph
    graph = StateGraph(AgentState)
    graph.add_node("planner", plan_node)
    graph.add_node("coder", code_generation_node)
    graph.add_node("tester", test_code_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "coder")
    graph.add_edge("coder", "tester")
    graph.add_conditional_edges(
        "tester",
        should_continue,
        {"continue": "planner", "end": END},
    )

    app = graph.compile()

    # Run the agent
    initial_state = AgentState(
        target_bank=target_bank,
        pdf_path=pdf_path,
        csv_path=csv_path,
        parser_path=parser_path,
        pdf_text=pdf_text,
        schema=schema_str,
        plan="",
        code="",
        test_result="",
        error_feedback="",
        attempt_count=0,
    )
    
    app.invoke(initial_state)

if __name__ == "__main__":
    # Ensure you have your GROQ_API_KEY set as an environment variable
    if not os.getenv("GROQ_API_KEY"):
        raise ValueError("GROQ_API_KEY environment variable not set.")

    # This line uses the key from your terminal, not from the code
    llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.1)

    main()
