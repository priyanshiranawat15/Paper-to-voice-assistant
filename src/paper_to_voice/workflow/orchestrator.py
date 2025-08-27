"""
Main workflow orchestration using LangGraph
"""

from langgraph.graph import StateGraph, START, END
from langgraph.constants import Send
from langchain_google_genai import ChatGoogleGenerativeAI

from ..core.models import State
from .steps import generate_steps, markdown_to_json, parse_json, solve_substeps
from .dialog import generate_dialog


def continue_to_substeps(state: State):
    """
    Managing the larger text in more manageable pieces of text
    """
    steps = state['plan']  # extracts list of text from state obj
    return [Send("solve_substeps", {"step": s, 'image_path': state['image_path']}) for s in steps]


def continue_to_substeps_voice(state: State):
    """
    Continue to voice generation for substeps
    """
    print('voice substeps')
    solutions = state['solutions']
    steps = state['steps']
    tone = 'Formal'  # ["Fun", "Formal"]
    return [
        Send("generate_dialog", {
            "step": st,
            "text": s,
            'tone': tone,
            'length': "Short (1-2 min)",
            'language': "EN"
        }) for st, s in zip(steps, solutions)
    ]


def create_podcast_workflow():
    """
    Create and return the podcast generation workflow
    """
    llm = ChatGoogleGenerativeAI(
        model='gemini-1.5-flash',
        temperature=0,
        max_tokens=None,
        max_retries=2
    )

    graph = StateGraph(State)
    graph.add_node("generate_steps", generate_steps)
    graph.add_node("markdown_to_json", markdown_to_json)
    graph.add_node("parse_json", parse_json)
    graph.add_node("solve_substeps", solve_substeps)
    graph.add_node("generate_dialog", generate_dialog)

    graph.add_edge(START, "generate_steps")
    graph.add_edge("generate_steps", "markdown_to_json")
    graph.add_edge("markdown_to_json", "parse_json")
    graph.add_conditional_edges("parse_json", continue_to_substeps, ["solve_substeps"])
    graph.add_conditional_edges("solve_substeps", continue_to_substeps_voice, ["generate_dialog"])
    graph.add_edge("generate_dialog", END)
    
    app = graph.compile()
    return app, llm
