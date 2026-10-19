from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

llm = ChatOpenAI()


class JokeState(TypedDict):
    topic: str
    joke: str
    explanation: str


def generate_joke(state: JokeState):
    prompt = f'generate a joke on the topic {state["topic"]}'
    response = llm.invoke(prompt).content

    return {"joke": response}


def generate_explanation(state: JokeState):
    prompt = f'write an explanation for the joke - {state["joke"]}'
    response = llm.invoke(prompt).content

    return {"explanation": response}


graph = StateGraph(JokeState)

graph.add_node("generate_joke", generate_joke)
graph.add_node("generate_explanation", generate_explanation)

graph.add_edge(START, "generate_joke")
graph.add_edge("generate_joke", "generate_explanation")
graph.add_edge("generate_explanation", END)

checkpointer = InMemorySaver()

workflow = graph.compile(checkpointer=checkpointer)

config1 = {"configurable": {"thread_id": "1"}}
print(workflow.invoke({"topic": "pizza"}, config=config1))

config2 = {"configurable": {"thread_id": "2"}}
print(workflow.invoke({"topic": "pasta"}, config=config2))

print(workflow.get_state(config1))
print(list(workflow.get_state_history(config1)))

# Time travel
print(
    workflow.invoke(
        None,
        {
            "configurable": {
                "thread_id": "1",
                "checkpoint_id": "1f06cc6e-7232-6cb1-8000-f71609e6cec5",
            }
        },
    )
)

# Updating state
print(
    workflow.update_state(
        {
            "configurable": {
                "thread_id": "1",
                "checkpoint_id": "1f06cc6e-7232-6cb1-8000-f71609e6cec5",
                "checkpoint_ns": "",
            }
        },
        {"topic": "samosa"},
    )
)

print(
    workflow.invoke(
        None,
        {
            "configurable": {
                "thread_id": "1",
                "checkpoint_id": "1f06cc72-ca16-6359-8001-7eea05e07dd2",
            }
        },
    )
)

print(list(workflow.get_state_history(config1)))

# Fault tolerance

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver
from typing import TypedDict
import time


# 1. Define the state
class CrashState(TypedDict):
    input: str
    step1: str
    step2: str


# 2. Define steps
def step_1(state: CrashState) -> CrashState:
    print("✅ Step 1 executed")
    return {"step1": "done", "input": state["input"]}


def step_2(state: CrashState) -> CrashState:
    print(
        "⏳ Step 2 hanging... now manually interrupt from the notebook toolbar (STOP button)"
    )
    time.sleep(1000)  # Simulate long-running hang
    return {"step2": "done"}


def step_3(state: CrashState) -> CrashState:
    print("✅ Step 3 executed")
    return {"done": True}


# 3. Build the graph
builder = StateGraph(CrashState)
builder.add_node("step_1", step_1)
builder.add_node("step_2", step_2)
builder.add_node("step_3", step_3)

builder.set_entry_point("step_1")
builder.add_edge("step_1", "step_2")
builder.add_edge("step_2", "step_3")
builder.add_edge("step_3", END)

checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)
try:
    print("▶️ Running graph: Please manually interrupt during Step 2...")
    graph.invoke({"input": "start"}, config={"configurable": {"thread_id": "thread-1"}})
except KeyboardInterrupt:
    print("❌ Kernel manually interrupted (crash simulated).")

# 4. Re-run to show fault-tolerant resume
print("\n🔁 Re-running the graph to demonstrate fault tolerance...")
final_state = graph.invoke(None, config={"configurable": {"thread_id": "thread-1"}})

print("\n✅ Final State:", final_state)
list(graph.get_state_history({"configurable": {"thread_id": "thread-1"}}))
