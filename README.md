# Anna - Free AI Student Assistant 🤖🎓

[![License](https://img.shields.io/badge/License-Custom%20Attribution--NonCommercial--NoDerivatives-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**Anna** is an open-source AI assistant optimized for student productivity. Featuring **voice-first interaction** and **offline capabilities**, Anna helps manage academic tasks through natural language commands. Now with improved stability and reduced CPU usage.

---

## Features 🚀

### 🎤 **Voice Control**
- **Wake Phrase**: "Anna ready" (customizable in config)
- **Hybrid Recognition**: Google Speech (online) + Vosk (offline)
- **Low-Latency Audio**: SoundDevice backend for responsive interaction
- **AI Mode**: Enhanced conversational capabilities

### 📚 **Core Academic Features**
- **Smart Pomodoro Timer**: `"Start 25 minute study timer"` with work/break sessions
- **Flashcard System**: `"Create flashcard: [front]: [back]"` with spaced repetition
- **Text Summarization**: NLTK-based text summarization capabilities
- **Quick Research**: `"Wikipedia [topic]"` for instant information

### 🌟 **Enhanced Features**
- **Weather Updates**: Real-time weather information via WeatherService
- **Mood Detection**: Context-aware responses with dynamic mood transitions
- **File System Integration**: Organized file management and access
- **Email Integration**: Email management capabilities
- **Dynamic Responses**: Personalized interactions via DynamicResponseGenerator
- **Enhanced Context**: Improved conversation awareness with EnhancedContextManager
- **Session Management**: Secure user session handling
- **Backup System**: Automated data backup and restoration capabilities
- **Screen Analysis**: Ability to analyze screen content for context-aware assistance
- **Event System**: Robust event handling and management
- **Dependency Container**: Efficient dependency injection and management
- **Conversation Storage**: Persistent storage of conversation history

### 🖥️ **System Integration**
- **App Launcher**: Extensive application control (Chrome, Discord, VS Code, etc.)
- **File Access**: Direct file system operations
- **Music Control**: Audio playback management
- **System Control**: Advanced system operations management

---

## Installation 📦

### Prerequisites
- Python 3.10+
- Windows/Linux/macOS
- Microphone

### Environment Setup
1. **Picovoice Configuration**:
   - Create a free account at [Picovoice Console](https://console.picovoice.ai/)
   - Create a `.env` file in the project root

2. **Environment Variables**:
```bash
# .env file
PICOVOICE_ACCESS_KEY=your-key-here
WEATHER_API_KEY=your-weather-api-key
EMAIL_PASSWORD=your-email-password
```

### Quick Setup
```bash
git clone https://github.com/Mainali1/Ai-Anna.git
cd Ai-Anna

# Install dependencies
pip install -r requirements.txt
pip -v install vosk

# Launch Anna
python main.py
```

---

## Configuration ⚙️
Edit `config.json` to customize:
```json
{
  "wake_phrase": "Anna ready",
  "voice_response": true,
  "speech_rate": 150,
  "wake_word_sensitivity": 0.5,
  "offline_mode": false,
  "speech_volume": 1.0
}
```

---

## Command Reference 🗣️

### Study Management
| Command Pattern | Example |
|-----------------|----------|
| "Start [X] minute timer" | "Start 25 minute timer" |
| "Create flashcard [front]: [back]" | "Create flashcard CPU: Central Processing Unit" |
| "Summarize text" | Generates text summary using NLTK |

### System Control
| Command Pattern | Action |
|-----------------|--------|
| "Open [application]" | Launches specified app (VS Code, Discord, etc.) |
| "What time is it?" | Current time/date |
| "Search web for [query]" | Web search functionality |
| "Weather update" | Get weather information |

### Utilities
| Command | Function |
|---------|----------|
| "Sleep" | Toggle voice listening |
| "Help" | Show command list |
| "Exit" | Close application |

---

## Technical Overview 🛠️

### Architecture
```mermaid
graph TD
    A[GUI] <--> B[Command Handler]
    B <--> C[Study Manager]
    B <--> D[Voice Engine]
    B <--> E[Email Manager]
    B <--> F[System Controller]
    B <--> G[AI Service Handler]
    B <--> H[File System Handler]
    B <--> I[Music Controller]
    B <--> L[Event System]
    B <--> M[Screen Analyzer]
    B <--> N[Session Manager]
    B <--> O[Backup Manager]
    C <--> J[Database]
    D <--> K[Picovoice]
    G <--> P[Dynamic Response Generator]
    G <--> Q[Enhanced Context Manager]
    G <--> R[Dependency Container]
    J <--> S[Conversation Storage]
```

### Key Technologies
- **Wake Word**: Picovoice Porcupine
- **Speech Recognition**: Google Web Speech API + Vosk
- **Text-to-Speech**: pyttsx3 with gTTS fallback
- **Database**: SQLite with spaced repetition
- **UI**: Tkinter + ttkthemes
- **Audio**: SoundDevice and Pygame mixer
- **NLP**: NLTK for text processing

---

## Performance Optimization 🚀
- Efficient audio processing with SoundDevice
- Threaded wake word detection
- Caching system for flashcards
- Configurable wake word sensitivity
- Automatic NLTK resource management

---

## Development 🛠️

### **Project Structure**
```
Ai-Anna/
│
├── main.py
├── assistant/
│   ├── __init__.py
│   ├── ai_service_handler.py
│   ├── backup_manager.py
│   ├── command_handler.py
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── help_command.py
│   │   ├── music_command.py
│   │   ├── system_command.py
│   │   ├── time_command.py
│   │   ├── weather_command.py
│   │   ├── web_search_command.py
│   │   ├── wikipedia_command.py
│   │   └── youtube_command.py
│   ├── config_manager.py
│   ├── conversation_storage.py
│   ├── database.py
│   ├── dependency_container.py
│   ├── dynamic_response_generator.py
│   ├── email_manager.py
│   ├── enhanced_context_manager.py
│   ├── env_loader.py
│   ├── event_system.py
│   ├── external_services.py
│   ├── file_system_handler.py
│   ├── gui.py
│   ├── logger.py
│   ├── mood_detector.py
│   ├── music_controller.py
│   ├── resources/
│   │   └── email_templates.json
│   ├── screen_analyzer.py
│   ├── secure_config.py
│   ├── session_manager.py
│   ├── spaced_repetition.py
│   ├── study_manager.py
│   ├── system_controller.py
│   ├── voice_engine.py
│   └── weather_service.py
│
├── requirements.txt
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── config.json
├── setup_startup.bat
├── .env
├── .gitignore
└── bell.wav
```

### **Contribute**
We welcome contributions! Please follow these steps:
1. Fork the repository
2. Create your feature branch:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. Commit your changes:
   ```bash
   git commit -m 'Add amazing feature'
   ```
4. Push to the branch:
   ```bash
   git push origin feature/amazing-feature
   ```
5. Open a Pull Request

---

### **How You Can Help**
- Report bugs or suggest features by opening an issue
- Contribute code via pull requests
- Share Anna with fellow students!

---
## License  
This project is licensed under the **Ai-Anna Custom License**.
- **Non-Commercial Use**: The software may not be used for commercial purposes in its original form
- **Attribution**: Proper credit must be given to the original author (Mainali1)
- **Derivative Works**: Allowed only if significant modifications (at least 50%) and substantial contributions are made
See the [LICENSE](LICENSE) file for full details.

---

## Acknowledgments 🙏

- **Speech Recognition**: Powered by [SpeechRecognition](https://github.com/Uberi/speech_recognition)
- **Wake Word Detection**: Enabled by [Picovoice](https://picovoice.ai/)
- **NLP Capabilities**: Provided by [NLTK](https://www.nltk.org/)
- **UI Design**: Enhanced with [ttkthemes](https://github.com/RedFantom/ttkthemes)
- **Audio Processing**: [SoundDevice](https://python-sounddevice.readthedocs.io/) and [Pygame](https://www.pygame.org/)

---

## Contributing
Please read our [Contributing Guidelines](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md) before making contributions.

---

**Made with ❤️ by Mainali1 - Empowering Students Through Open Source**