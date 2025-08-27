"""
Workflow steps for processing research papers
"""

import json
from langchain_core.messages import HumanMessage
from ..core.models import State, StepState
from ..core.config import get_llm


def generate_steps(state: State) -> dict:
    """
    Generate research steps from paper images
    """
    llm = get_llm()
    prompt = """
    Consider you are a research scientist in artificial intelligence who is expert in understanding research papers.
    You will be given a research paper and you need to identify all the steps a researcher need to perform.
    Identify each steps and their substeps.
    """
    message = HumanMessage(content=[
        {'type': 'text', 'text': prompt},
        *[{"type": 'image_url', 'image_url': img} for img in state['image_path']]
    ])
    response = llm.invoke([message])
    print(response)
    return {"content": [response.content], "image_path": state['image_path']}


def markdown_to_json(state: State) -> dict:
    """
    Convert markdown content to JSON format
    """
    llm = get_llm()
    prompt = """
    You are given a markdown content and you need to parse this data into json format. Follow correctly key and value
    pairs for each bullet point.
    Follow following schema strictly.

    schema:
    [
    {
      "step": "description of step 1 ",
      "substeps": [
        {
          "key": "title of sub step 1 of step 1",
          "value": "description of sub step 1 of step 1"
        },
        {
          "key": "title of sub step 2 of step 1",
          "value": "description of sub step 2 of step 1"
        }]},
        {
      "step": "description of step 2",
      "substeps": [
        {
          "key": "title of sub step 1 of step 2",
          "value": "description of sub step 1 of step 2"
        },
        {
          "key": "title of sub step 2 of step 2",
          "value": "description of sub step 2 of step 2"
        }]}]'

    Content:
    %s
    """ % state['content']
    str_response = llm.invoke([prompt])
    return {'content': str_response.content, "image_path": state['image_path']}


def parse_json(state: State) -> dict:
    """
    Parse JSON data embedded within markdown content
    """
    try:
        text = state['content']  # Extracts markdown content
        lines = text.splitlines()
        json_lines = [
            line for line in lines 
            if not line.strip().startswith("```") and not line.strip().startswith("'''")
        ]
        json_content = "\n".join(json_lines).strip()
        json_data = json.loads(json_content)
        output = []

        for step in json_data:
            substeps = []
            for substep in step['substeps']:
                substeps.append(substep['value'])

            output.append({'step': step['step'], 'substeps': substeps})
        print(json_content)
        return {"plan": output}
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return {"plan": []}


def solve_substeps(state: StepState) -> dict:
    """
    Solve substeps for each main step
    """
    llm = get_llm()
    print(state)
    inp = state['step']
    print('solving sub steps')
    
    qanda = ' '.join([
        f'\n Question: {substep} \n Answer:' 
        for substep in inp['substeps']
    ])
    
    prompt = f"""You will be given instruction to analyze research papers. You need to understand the
    instruction and solve all the questions mentioned in the list.
    Keep the pair of Question and its answer in your response. Your response should be next to the keyword "Answer"

    Instruction:
    {inp['step']}
    Questions:
    {qanda}
    """
    
    message = HumanMessage(content=[
        {'type': 'text', 'text': prompt},
        *[{"type": 'image_url', 'image_url': img} for img in state['image_path']]
    ])
    response = llm.invoke([message])
    return {"steps": [inp['step']], 'solutions': [response.content]}
