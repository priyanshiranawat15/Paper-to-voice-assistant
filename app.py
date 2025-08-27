import streamlit as st
import os
import base64
import json
import time
import sys
import operator
from typing import Annotated, TypedDict
from pathlib import Path
import pypdfium2 as pdfium
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.graph.message import add_messages
from langgraph.constants import Send
from langchain_core.messages import HumanMessage
from time import sleep
import google.generativeai as genai
from gradio_client import Client
from pydub import AudioSegment
from pydub.generators import Sine
from langchain_core.pydantic_v1 import BaseModel
from tqdm import tqdm
from tempfile import NamedTemporaryFile
from dotenv import load_dotenv

load_dotenv()

# Set up Google API Key (consider using st.secrets in production)
os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

llm= ChatGoogleGenerativeAI(
    model=os.getenv('GOOGLE_MODEL_NAME'),
    temperature=0,
    max_tokens=None,
    max_retries=2
)

class State(TypedDict):
    image_path: str
    steps: Annotated[list,operator.add]
    substeps:Annotated[list,operator.add]
    solutions:Annotated[list,operator.add]
    
    content:str
    plan: str
    Dialog:Annotated[list,operator.add]
    
class Task(BaseModel):
    task:str

#storing each sub-step
class SubStep(BaseModel):
    substep: str
    
class StepState(TypedDict):
    step: str
    image_path: str
    solutions: str
    Dialog: str
    
# Utility Functions (copied from the original script)
def encode_image_to_base64(file_path):
    with open(file_path, "rb") as img_file:
        return f"data:image/jpeg;base64,{base64.b64encode(img_file.read()).decode()}"

def process_pdf(pdf_path):
    image_filenames = []
    try:
        pdf = pdfium.PdfDocument(pdf_path)
        num_pages = len(pdf)

        output_dir = os.path.dirname(pdf_path)
        os.makedirs(output_dir, exist_ok=True)

        for i in range(num_pages):
            page = pdf[i]
            image = page.render(scale=4).to_pil()

            filename = f"Photo_{i:03d}.jpg"
            image_path = os.path.join(output_dir, filename)
            image.save(image_path)
            image_filenames.append(filename)

    except Exception as e:
        st.error(f"Error processing PDF: {e}")

    return image_filenames

def get_text_to_voice(text, speed=0.9, accent="EN-US", language="EN"):
    hf_client = Client("neuromod0/MeloTTS-English-v3")
    file_path = hf_client.predict(
        text=text,
        language=language,
        speaker=accent,
        speed=speed,
        api_name="/synthesize",
    )
    return file_path
    
            
def generate_steps(state: State):
    prompt="""
    Consider you are a research scientist in artificial intelligence who is expert in understanding research papers.
    You will be given a research paper and you need to identify all the steps a researcher need to perform.
    Identify each steps and their substeps.
    """
    message = HumanMessage(content=[{'type':'text','text':prompt},
                                    *[{"type":'image_url','image_url':img} for img in state['image_path']] # '*' is used to unpack list comprehension into individual elements
                                    ]

                                    )
    response = llm.invoke([message])
    print(response)
    return {"content": [response.content],"image_path":state['image_path']}

def markdown_to_json(state: State):
    prompt ="""
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
    """% state['content']
    str_response = llm.invoke([prompt])
   

    return({'content':str_response.content,"image_path":state['image_path']})

#parse JSON data embedded within markdown content. 
import json

def parse_json(state: State):
    try:
        text=state['content'] #Extracts markdown content
        lines = text.splitlines()
        json_lines = [line for line in lines if not line.strip().startswith("```") and not line.strip().startswith("'''")] #Filters out content not in JSON
        json_content = "\n".join(json_lines).strip() #Joins the string back to a single string and removes any whitespace
        json_data = json.loads(json_content) #Parse json string into content
        output = []

        for step in json_data:
            substeps = []
            for substep in step['substeps']:
                substeps.append(substep['value'])  # Extract the value directly

            output.append({'step': step['step'], 'substeps': substeps})
        print(json_content)
        return {"plan": output}
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        # Handle the error, e.g., log it, retry the parsing, or return a default value
        return {"plan": []}
    
def solve_substeps(state: StepState):
    print(state)
    inp = state['step'] #Extracts the step information from state object
    print('solving sub steps')
    #iterates over each substeps and create question answering pair
    qanda = ' '.join([f'\n Question: {substep} \n Answer:' for substep  in inp['substeps']])
    prompt=f""" You will be given instruction to analyze research papers. You need to understand the
    instruction and solve all the questions mentioned in the list.
    Keep the pair of Question and its answer in your response. Your response should be next to the keyword "Answer"

    Instruction:
    {inp['step']}
    Questions:
    {qanda}
    """
    message = HumanMessage(content=[{'type':'text','text':prompt},
                                    *[{"type":'image_url','image_url':img} for img in state['image_path']]
                                    ]
                                    )
    response = llm.invoke([message])
    return {"steps":[inp['step']], 'solutions':[response.content]}

#Managing the larger text in more managable pieces of text
def continue_to_substeps(state: State):
    steps = state['plan']# extracts list of text from state obj
    return [Send("solve_substeps", {"step": s,'image_path':state['image_path']}) for s in steps] 

SYSTEM_PROMPT = """
You are a world-class podcast producer tasked with transforming the provided input text into an engaging and informative podcast script. The input may be unstructured or messy, sourced from PDFs or web pages. Your goal is to extract the most interesting and insightful content for a compelling podcast discussion.

# Steps to Follow:

1. **Analyze the Input:**
   Carefully examine the text, identifying key topics, points, and interesting facts or anecdotes that
   could drive an engaging podcast conversation. Disregard irrelevant information or formatting issues.

2. **Brainstorm Ideas:**
   In the `<scratchpad>`, creatively brainstorm ways to present the key points engagingly. Consider:
   - Analogies, storytelling techniques, or hypothetical scenarios to make content relatable
   - Ways to make complex topics accessible to a general audience
   - Thought-provoking questions to explore during the podcast
   - Creative approaches to fill any gaps in the information

3. **Craft the Dialogue:**
   Develop a natural, conversational flow between the host (Jane) and Dr. Sharma (the author or an expert on the topic). Incorporate:
   - The best ideas from your brainstorming session
   - Clear explanations of complex topics
   - An engaging and lively tone to captivate listeners
   - A balance of information and entertainment

   Rules for the dialogue:
   - The host (Jane) always initiates the conversation and interviews  Dr. Sharma
   - Include thoughtful questions from the host to guide the discussion
   - Incorporate natural speech patterns, including occasional verbal fillers (e.g., "um," "well," "you know")
   - Allow for natural interruptions and back-and-forth between host and Dr. Sharma
   - Ensure  Dr. Sharma's responses are substantiated by the input text, avoiding unsupported claims
   - Maintain a PG-rated conversation appropriate for all audiences
   - Avoid any marketing or self-promotional content from Dr. Sharma
   - The host concludes the conversation

4. **Summarize Key Insights:**
   Naturally weave a summary of key points into the closing part of the dialogue. This should feel like a casual conversation rather than a formal recap, reinforcing the main takeaways before signing off.

5. **Maintain Authenticity:**
   Throughout the script, strive for authenticity in the conversation. Include:
   - Moments of genuine curiosity or surprise from the host
   - Instances where Dr. Sharma might briefly struggle to articulate a complex idea
   - Light-hearted moments or humor when appropriate
   - Brief personal anecdotes or examples that relate to the topic (within the bounds of the input text)

6. **Consider Pacing and Structure:**
   Ensure the dialogue has a natural ebb and flow:
   - Start with a strong hook to grab the listener's attention
   - Gradually build complexity as the conversation progresses
   - Include brief "breather" moments for listeners to absorb complex information
   - End on a high note, perhaps with a thought-provoking question or a call-to-action for listeners
"""
def generate_dialog(state):
    text = state['text']
    tone = state['tone']
    length = state['length']
    language = state['language']

    modified_system_prompt = SYSTEM_PROMPT
    modified_system_prompt += f"\n\PLEASE paraphrase the following TEXT in dialog format."

    if tone:
        modified_system_prompt += f"\n\nTONE: The tone of the podcast should be {tone}."
    if length:
        length_instructions = {
            "Short (1-2 min)": "Keep the podcast brief, around 1-2 minutes long.",
            "Medium (3-5 min)": "Aim for a moderate length, about 3-5 minutes.",
        }
        modified_system_prompt += f"\n\nLENGTH: {length_instructions[length]}"
    if language:
        modified_system_prompt += (
            f"\n\nOUTPUT LANGUAGE <IMPORTANT>: The the podcast should be {language}."
        )

    messages = modified_system_prompt + '\nTEXT: '+ text
    

    response = llm.invoke([messages])
    print(response)
    return {"Step":[state['step']],"Finding":[state['text']], 'Dialog':[response.content]}


def continue_to_substeps_voice(state: State):
    print('voice substeps')

    solutions = state['solutions']
    steps = state['steps']

    tone ='Formal' #  ["Fun", "Formal"]
    return [Send("generate_dialog", {"step":st,"text": s,'tone':tone,'length':"Short (1-2 min)",'language':"EN"}) for st,s in zip(steps,solutions)]


def create_podcast_workflow():
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

def generate_podcast_audio(text: str, language: str) -> str:
    
    if "**Jane:**" in text:
        text = text.replace("**Jane:**",'').strip()
        accent = "EN-US"
        speed = 0.9
    elif "**Dr. Sharma:**" in text:  # host
        text = text.split("**")[-1].strip()
        accent = "EN_INDIA"
        speed = 0.9
    else:
        return 'Empty Text'
    for attempt in range(3):

        try:
            file_path = get_text_to_voice(text,speed,accent,language)
            return file_path
        except Exception as e:
            if attempt == 2:  # Last attempt
                raise  # Re-raise the last exception if all attempts fail
            time.sleep(1)  # Wait for 1 second before retrying

def store_voice(topic_dialog):
    audio_path = []
    for topic, dialog in tqdm(topic_dialog.items()):
        # Check if dialog is a string or already a list
        if isinstance(dialog, str):
            dialog_speaker = dialog.split("\n")
        elif isinstance(dialog, list):
            dialog_speaker = dialog  # If it's already a list, use it directly
        else:
            continue  # Skip if dialog is neither a string nor a list

        for speaker in tqdm(dialog_speaker):
            one_dialog = speaker.strip()

            language_for_tts = "EN"

            if len(one_dialog) > 0:
                # Generate the podcast audio for each dialog
                audio_file_path = generate_podcast_audio(one_dialog, language_for_tts)
                audio_path.append(audio_file_path)

            sleep(5)
        break  # This break will stop after processing the first topic
    return audio_path


def consolidate_voice(audio_paths, voice_dir):
    audio_segments = []
    voice_path = [paths for paths in audio_paths if paths != 'Empty Text']

    # Create guitar audio paths
    light_guitar_path = os.path.join(voice_dir, "light-guitar.wav")
    ambient_guitar_path = os.path.join(voice_dir, "ambient-guitar.wav")

    # Ensure guitar audio exists
    if not os.path.exists(light_guitar_path):
        Sine(440).to_audio_segment(duration=1000).export(light_guitar_path, format="wav")
    
    if not os.path.exists(ambient_guitar_path):
        Sine(220).to_audio_segment(duration=1000).export(ambient_guitar_path, format="wav")

    # Add background guitar tracks
    audio_segments.append(AudioSegment.from_file(light_guitar_path))
    
    # Add voice tracks
    for audio_file_path in voice_path:
        try:
            audio_segment = AudioSegment.from_file(audio_file_path)
            audio_segments.append(audio_segment)
        except Exception as e:
            st.warning(f"Could not process audio file {audio_file_path}: {e}")

    # Add ambient guitar track
    audio_segments.append(AudioSegment.from_file(ambient_guitar_path))

    # Combine audio
    if audio_segments:
        combined_audio = sum(audio_segments)
        os.makedirs(os.path.join(voice_dir, "tmp"), exist_ok=True)
        
        with NamedTemporaryFile(dir=os.path.join(voice_dir, "tmp"), 
                                 delete=False, 
                                 suffix=".mp3") as temp_file:
            combined_audio.export(temp_file.name, format="mp3")
            return temp_file.name
    
    return None

def main():
    st.title("📄 Research Paper Podcast Generator 🎙️")
    
    # Sidebar for configuration
    st.sidebar.header("Configuration")
    tone = st.sidebar.selectbox("Podcast Tone", ["Formal", "Conversational"])
    language = st.sidebar.selectbox("Language", ["EN"])

    # PDF Upload
    uploaded_pdf = st.file_uploader("Upload Research Paper (PDF)", type=['pdf'])
    
    if uploaded_pdf is not None:
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Save uploaded PDF
            with open(os.path.join("temp", uploaded_pdf.name), "wb") as f:
                f.write(uploaded_pdf.getbuffer())
            pdf_path = os.path.join("temp", uploaded_pdf.name)

            # Process PDF into images
            status_text.text("Processing PDF pages...")
            progress_bar.progress(10)
            image_paths = process_pdf(pdf_path)
            
            # Encode images
            encoded_images = [encode_image_to_base64(f"temp/Photo_{i:03d}.jpg") for i in range(len(image_paths))]

            # Create workflow
            status_text.text("Generating podcast workflow...")
            progress_bar.progress(30)
            workflow_app, _ = create_podcast_workflow()

            # Run workflow
            status_text.text("Analyzing research paper...")
            progress_bar.progress(50)
            output = list(workflow_app.stream({'image_path': encoded_images}))

            # Extract dialog
            status_text.text("Generating podcast dialog...")
            progress_bar.progress(70)
            topics = []
            dialog_planner = {}
            
            for responses in output[10:17]:
                dialog = responses['generate_dialog']['Dialog'][0]
                dialog = dialog.strip().split('## Podcast Script')[-1].strip()
                dialog = dialog.replace('[Guest name]', 'Dr. Sharma')
                dialog = dialog.replace('**Guest:**', '**Dr. Sharma**')
                dialog_planner[len(dialog_planner)] = dialog
            print(dialog)
            print(dialog_planner)

            # Generate audio
            status_text.text("Synthesizing podcast audio...")
            progress_bar.progress(90)
            
            # Temporary directory for voice generation
            voice_dir = os.path.join("temp", "voices")
            os.makedirs(voice_dir, exist_ok=True)
            audio_paths = store_voice(dialog_planner)
            print("Generated audio paths:", audio_paths)

            # Generate voice for each dialog part
            audio_paths = []
            for _, dialog in dialog_planner.items():
                dialog_parts = dialog.split('\n')
                for part in dialog_parts:
                    if len(part.strip()) > 0:
                        try:
                            audio_file = generate_podcast_audio(part.strip(),language)
                            audio_paths.append(audio_file)
                        except Exception as e:
                            st.warning(f"Could not generate voice for part: {e}")

            # Consolidate voice tracks
            print(audio_paths)
            final_audio_path = consolidate_voice(audio_paths, voice_dir)
            print(final_audio_path)

            # Final display
            progress_bar.progress(100)
            status_text.text("Podcast generation complete!")

            # Play audio
            if final_audio_path:
                #with open(final_audio_path, 'rb') as audio_file:
                st.audio(final_audio_path, format="audio/mpeg")
                st.success("Podcast generated successfully!")

        except Exception as e:
            import traceback
            
            st.error(f"An error occurred: {traceback.format_exc()}")
            st.error("Please check your PDF and try again.")

if __name__ == "__main__":
    main()