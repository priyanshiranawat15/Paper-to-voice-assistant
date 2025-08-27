# Paper to Voice Assistant 🎙️

An intelligent Streamlit application that converts research papers into engaging podcast audio using AI-powered analysis and text-to-speech synthesis.

## 🌟 Features

- **PDF Analysis**: Automatically processes research papers and extracts key insights
- **AI-Powered Workflow**: Uses Google's Gemini AI to understand and structure content
- **Podcast Generation**: Creates engaging dialog between host (Jane) and expert (Dr. Sharma)
- **High-Quality TTS**: Leverages MeloTTS for natural-sounding voice synthesis
- **Audio Processing**: Combines voice tracks with background audio for professional results

## 🏗️ Project Structure

```
Paper-to-voice-assistant/
├── src/paper_to_voice/           # Main package
│   ├── core/                     # Core functionality
│   │   ├── config.py            # Configuration and settings
│   │   └── models.py            # Data models and type definitions
│   ├── utils/                    # Utility functions
│   │   └── pdf_processor.py     # PDF processing and image conversion
│   ├── workflow/                 # AI workflow components
│   │   ├── steps.py             # Research paper analysis steps
│   │   ├── dialog.py            # Dialog generation
│   │   └── orchestrator.py      # Workflow orchestration
│   └── audio/                    # Audio processing
│       ├── tts.py               # Text-to-speech functionality
│       └── processor.py         # Audio consolidation
├── config/                       # Configuration files
│   └── .env.example             # Environment variables template
├── tests/                        # Test files
│   └── test_basic.py            # Basic functionality tests
├── static/                       # Static assets (if needed)
├── temp/                         # Temporary files (auto-created)
├── main.py                       # Main Streamlit application
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google Generative AI API key
- Internet connection for TTS services

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Paper-to-voice-assistant
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp config/.env.example .env
   # Edit .env file with your API keys
   ```

4. **Run the application**
   ```bash
   streamlit run main.py
   ```

### Environment Variables

Create a `.env` file in the root directory:

```env
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_MODEL_NAME=gemini-1.5-flash
```

## 🎯 Usage

1. **Launch the App**: Run `streamlit run main.py`
2. **Upload PDF**: Use the file uploader to select your research paper
3. **Configure Settings**: Choose podcast tone and language from the sidebar
4. **Generate Podcast**: Wait for the AI to process and generate your podcast
5. **Listen & Download**: Play the generated audio directly in the browser

## 🔧 Configuration

The application can be customized through several configuration files:

- **Core Settings**: `src/paper_to_voice/core/config.py`
- **Environment Variables**: `.env` file
- **Model Selection**: Configure different AI models for text generation and TTS

## 🧪 Testing

Run the test suite:

```bash
python -m pytest tests/
# or
python tests/test_basic.py
```

## 📦 Components

### Core Components

- **Config Management**: Centralized configuration and API key management
- **Data Models**: Type-safe data structures using TypedDict and Pydantic

### Workflow Components

- **Steps Processing**: Analyzes research papers and extracts actionable steps
- **Dialog Generation**: Creates natural conversations between podcast characters
- **Orchestration**: Manages the complete workflow using LangGraph

### Audio Components

- **TTS Integration**: High-quality text-to-speech using MeloTTS
- **Audio Processing**: Combines multiple audio tracks with background music

### Utilities

- **PDF Processing**: Converts PDF pages to images for AI analysis
- **Image Encoding**: Handles base64 encoding for API consumption

## 🚨 Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure your `GOOGLE_API_KEY` is correctly set in `.env`
2. **TTS Failures**: Check internet connection and HuggingFace service availability
3. **Memory Issues**: Large PDFs may require more system memory
4. **Audio Generation**: Ensure proper text formatting for dialog parsing

### Error Handling

The application includes comprehensive error handling:
- Retry logic for TTS generation
- Graceful handling of PDF processing errors
- User-friendly error messages in the Streamlit interface

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Generative AI for powerful text analysis
- MeloTTS for high-quality voice synthesis
- Streamlit for the amazing web framework
- LangChain and LangGraph for AI workflow orchestration

## 📞 Support

If you encounter any issues or have questions:

1. Check the troubleshooting section
2. Review the logs in the Streamlit interface
3. Open an issue on GitHub
4. Check environment variable configuration

---

**Made with ❤️ for researchers and podcast enthusiasts**
