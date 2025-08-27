"""
Main Streamlit application for Paper to Voice Assistant
"""

import os
import streamlit as st
import traceback

from src.paper_to_voice.utils.pdf_processor import process_pdf, encode_image_to_base64
from src.paper_to_voice.workflow.orchestrator import create_podcast_workflow
from src.paper_to_voice.audio.processor import store_voice, consolidate_voice
from src.paper_to_voice.audio.tts import generate_podcast_audio
from src.paper_to_voice.core.config import TEMP_DIR, VOICES_DIR


def main():
    """Main Streamlit application"""
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
            # Ensure temp directory exists
            os.makedirs(TEMP_DIR, exist_ok=True)
            
            # Save uploaded PDF
            pdf_path = os.path.join(TEMP_DIR, uploaded_pdf.name)
            with open(pdf_path, "wb") as f:
                f.write(uploaded_pdf.getbuffer())

            # Process PDF into images
            status_text.text("Processing PDF pages...")
            progress_bar.progress(10)
            image_paths = process_pdf(pdf_path)
            
            # Encode images
            encoded_images = [
                encode_image_to_base64(os.path.join(TEMP_DIR, f"Photo_{i:03d}.jpg")) 
                for i in range(len(image_paths))
            ]

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
            dialog_planner = {}
            
            # Extract dialogs from workflow output
            for responses in output[10:17]:
                if 'generate_dialog' in responses:
                    dialog = responses['generate_dialog']['Dialog'][0]
                    dialog = dialog.strip().split('## Podcast Script')[-1].strip()
                    dialog = dialog.replace('[Guest name]', 'Dr. Sharma')
                    dialog = dialog.replace('**Guest:**', '**Dr. Sharma**')
                    dialog_planner[len(dialog_planner)] = dialog
            
            print("Dialog planner:", dialog_planner)

            # Generate audio
            status_text.text("Synthesizing podcast audio...")
            progress_bar.progress(90)
            
            # Temporary directory for voice generation
            voice_dir = os.path.join(TEMP_DIR, VOICES_DIR)
            os.makedirs(voice_dir, exist_ok=True)

            # Generate voice for each dialog part
            audio_paths = []
            for _, dialog in dialog_planner.items():
                dialog_parts = dialog.split('\n')
                for part in dialog_parts:
                    if len(part.strip()) > 0:
                        try:
                            audio_file = generate_podcast_audio(part.strip(), language)
                            if audio_file != 'Empty Text':
                                audio_paths.append(audio_file)
                        except Exception as e:
                            st.warning(f"Could not generate voice for part: {e}")

            # Consolidate voice tracks
            print("Audio paths:", audio_paths)
            final_audio_path = consolidate_voice(audio_paths, voice_dir)
            print("Final audio path:", final_audio_path)

            # Final display
            progress_bar.progress(100)
            status_text.text("Podcast generation complete!")

            # Play audio
            if final_audio_path:
                st.audio(final_audio_path, format="audio/mpeg")
                st.success("🎉 Podcast generated successfully!")
            else:
                st.warning("No audio was generated. Please check your PDF and try again.")

        except Exception as e:
            st.error(f"An error occurred: {traceback.format_exc()}")
            st.error("Please check your PDF and try again.")


if __name__ == "__main__":
    main()
