# Anna - Free AI Student Assistant 🤖🎓

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**Anna** is an open-source, privacy-focused AI assistant designed specifically for students. Built with **100% free and open-source technologies**, Anannya helps you manage your academic life through intuitive voice and text commands. Whether you're tracking assignments, studying with flashcards, or summarizing lectures, Anannya is your personal academic companion.

---

## Features 🚀

### 🎤 **Voice Control**
- **Wake Word Detection**: Uses Picovoice's free tier for always-on listening.
- **Speech-to-Text**: Powered by Google's free speech recognition API.
- **Text-to-Speech**: Offline TTS using system voices via `pyttsx3`.

### 📚 **Academic Tools**
- **Assignment Tracker**: Log assignments with deadlines and get reminders.
- **Smart Flashcards**: Spaced repetition system for efficient studying.
- **Study Timer**: Pomodoro technique with customizable work/break intervals.
- **Lecture Summarizer**: Condense long texts using NLP-powered summarization.
- **Research Helper**: Quick access to Wikipedia and DuckDuckGo for instant answers.

### 🛠 **Productivity Features**
- **Class Schedule Manager**: Organize your weekly timetable.
- **File Quick-Access**: Open frequently used files with voice commands.
- **Screen Time Monitor**: Track and manage your study time.
- **Customizable Hotkeys**: Quick shortcuts for common tasks.
- **Cross-Platform Support**: Works on Windows, macOS, and Linux.

---

## Installation 📦

### Prerequisites
- Python 3.8+
- Microphone
- Free Picovoice account (for wake word)

### Step-by-Step Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Mainali1/Ai-Anna.git
   cd Ai-Anna
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

3. **Set Up Picovoice**:
   - Create a free account at [Picovoice Console](https://console.picovoice.ai/).
   - Create a `.env` file in the project root and add your API key:
     ```env
     PICOVOICE_KEY=your-free-key-here
     ```

4. **Run Anna**:
   ```bash
   python main.py
   ```

---

## Usage Guide 🗣️

### **Basic Commands**
| Command | Action |
|---------|--------|
| "Anna, what's my schedule?" | View your class timetable |
| "Add physics assignment due Friday" | Log a new assignment |
| "Start 30-minute study timer" | Begin a Pomodoro session |
| "Search Wikipedia for AI history" | Get a Wikipedia summary |
| "Create flashcard: Photosynthesis..." | Make a study card |
| "Summarize this text: [paste text]" | Condense long text |
| "Open my math notes" | Quick-access files |

### **Keyboard Shortcuts**
- `Ctrl + Space`: Toggle voice listening
- `Alt + Q`: Show quick command list
- `Esc`: Minimize to system tray

---

## Development 🛠️

### **Project Structure**
```
Ai-Anannya/
│
├── main.py
├── assistant/
│   ├── __init__.py
│   ├── gui.py
│   ├── voice_engine.py
│   ├── command_handler.py
│   ├── study_manager.py
│   ├── database.py
│   └── resources/
│       └── wake_word.ppn (Make a Wake word in Picovoice)
│
├── requirements.txt
├── README.md
└── assignments.db
```

### **Contribute**
We welcome contributions! Please follow these steps:
1. Fork the repository.
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
5. Open a Pull Request.

---

## Future Roadmap 🔮

### **Planned Features**
- Mood tracking with sentiment analysis
- Peer collaboration tools
- Integration with open-source LMS platforms
- Ethical voice cloning for personalized TTS
- Multi-language support

### **How You Can Help**
- Report bugs or suggest features by opening an issue.
- Contribute code via pull requests.
- Share Anannya with fellow students!

---
## License  
This project is licensed under the **Ai-Anna Custom License**.  
- **Non-Commercial Use**: The software may not be used for commercial purposes in its original form.  
- **Attribution**: Proper credit must be given to the original author (Mainali1).  
- **Derivative Works**: Allowed only if significant modifications (at least 50%) and substantial contributions are made.  
See the [LICENSE](LICENSE) file for full details.

---

## Acknowledgments 🙏

- **Speech Recognition**: Powered by [SpeechRecognition](https://github.com/Uberi/speech_recognition).
- **Wake Word Detection**: Enabled by [Picovoice](https://picovoice.ai/).
- **NLP Capabilities**: Provided by [spaCy](https://spacy.io/) and [NLTK](https://www.nltk.org/).
- **UI Design**: Enhanced with [ttkthemes](https://github.com/RedFantom/ttkthemes).

---

## Contributing
Please read our [Contributing Guidelines](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md) before making contributions.

---

**Made with ❤️ by Mainali1 - Empowering Students Through Open Source**