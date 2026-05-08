from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class AgentState(TypedDict):
    query: str
    selected_agent: str


def route_node(state: AgentState) -> AgentState:
    query = state["query"].lower()
    state["selected_agent"] = "exam_preparation_agent" if "exam" in query else "tutor_agent"
    return state


def build_agent_graph():
    graph = StateGraph(AgentState)
    graph.add_node("route", route_node)
    graph.add_edge(START, "route")
    graph.add_edge("route", END)
    return graph.compile()
