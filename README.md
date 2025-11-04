# 🎬 OpenStudio - Multi-Agent Storytelling Platform

OpenStudio is a powerful, AI-driven storytelling platform that leverages multiple specialized agents to create compelling narratives collaboratively. Built with FastAPI, LangChain, and supporting both OpenAI and Groq APIs, it provides a comprehensive suite of tools for creative writing, world-building, and collaborative storytelling.

## ✨ Features

### 🤖 Specialized AI Agents
- **Plotter Agent**: Generates story outlines, character development, and narrative arcs
- **Writer Agent**: Transforms plots into detailed prose with various writing styles
- **Editor Agent**: Refines content for grammar, style, and readability
- **World Builder Agent**: Creates detailed settings, cultures, and environments

### 🎭 Multi-Agent Orchestration
- Coordinated workflows between agents
- Intelligent task routing and dependency management
- Customizable storytelling pipelines

### 🤝 Collaborative Features
- Real-time collaboration sessions
- Multi-user project management
- Version control and change tracking
- Role-based access control

### 🚀 Modern API Architecture
- RESTful FastAPI endpoints
- Comprehensive request/response models
- Interactive API documentation
- CORS support for web applications

## 📁 Project Structure

```
OpenStudio/
├── agents/                 # AI agent implementations
│   ├── __init__.py
│   ├── base_agent.py      # Base agent class
│   ├── plotter_agent.py   # Story plotting agent
│   ├── writer_agent.py    # Content writing agent
│   ├── editor_agent.py    # Content editing agent
│   └── world_builder_agent.py  # World building agent
├── api/                   # FastAPI endpoints
│   ├── __init__.py
│   └── endpoints.py       # All API routes
├── collaboration/         # Session management
│   ├── __init__.py
│   └── session_manager.py # Collaborative features
├── config/               # Configuration management
│   ├── __init__.py
│   └── settings.py       # Environment settings
├── models/               # Data models
│   ├── __init__.py
│   └── schemas.py        # Pydantic models
├── orchestrator/         # Multi-agent coordination
│   ├── __init__.py
│   └── workflow_orchestrator.py
├── .env.example          # Environment variables template
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- OpenAI API key (optional)
- Groq API key (optional)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd OpenStudio
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
```bash
cp .env.example .env
```

Edit the `.env` file with your API keys and preferences:
```env
# AI Model Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=mixtral-8x7b-32768

# Database Configuration
DATABASE_URL=sqlite:///./openstudio.db
REDIS_URL=redis://localhost:6379

# Application Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true
SECRET_KEY=your_secret_key_here
DEFAULT_MODEL_PROVIDER=openai
```

### 5. Run the Application
```bash
python main.py
```

The API will be available at:
- **API Server**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 API Usage

### Authentication
Currently, the API is open for development. In production, implement proper authentication.

### Core Endpoints

#### 🎯 Plotter Agent
Generate story plots and character development:

```bash
curl -X POST "http://localhost:8000/plotter/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A mystery story set in Victorian London",
    "genre": "mystery",
    "target_length": "novel",
    "characters": ["detective", "suspect", "witness"]
  }'
```

#### ✍️ Writer Agent
Transform plots into detailed content:

```bash
curl -X POST "http://localhost:8000/writer/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "plot_outline": "Detective investigates mysterious disappearance...",
    "style": "descriptive",
    "target_length": "medium",
    "tone": "suspenseful"
  }'
```

#### 📝 Editor Agent
Refine and improve written content:

```bash
curl -X POST "http://localhost:8000/editor/refine" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Your written content here...",
    "focus_areas": ["grammar", "clarity", "style"],
    "target_audience": "general"
  }'
```

#### 🌍 World Builder Agent
Create detailed settings and environments:

```bash
curl -X POST "http://localhost:8000/world-builder/create" \
  -H "Content-Type: application/json" \
  -d '{
    "world_type": "fantasy",
    "genre": "fantasy",
    "scope": "city",
    "key_elements": ["magic system", "political structure"]
  }'
```

#### 🎭 Orchestrator
Coordinate multi-agent workflows:

```bash
curl -X POST "http://localhost:8000/orchestrator/workflow" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_type": "complete_story",
    "initial_input": "A story about time travel",
    "preferences": {
      "genre": "science_fiction",
      "length": "short_story"
    }
  }'
```

### 🤝 Collaboration Features

#### Create Collaboration Session
```bash
curl -X POST "http://localhost:8000/collaboration/session" \
  -H "Content-Type: application/json" \
  -d '{
    "participants": ["user1", "user2"],
    "project_type": "novel",
    "shared_context": "Collaborative fantasy novel project"
  }'
```

#### Join Session
```bash
curl -X GET "http://localhost:8000/collaboration/session/{session_id}"
```

## 🔧 Configuration Options

### Model Providers
OpenStudio supports multiple AI providers:

- **OpenAI**: GPT-3.5, GPT-4, GPT-4 Turbo
- **Groq**: Mixtral, LLaMA models

Configure in `.env`:
```env
DEFAULT_MODEL_PROVIDER=openai  # or 'groq'
OPENAI_MODEL=gpt-4
GROQ_MODEL=mixtral-8x7b-32768
```

### Agent Customization
Each agent can be customized through their respective classes:

```python
from agents import PlotterAgent

# Custom plotter with specific parameters
plotter = PlotterAgent(
    model_provider="openai",
    model_name="gpt-4",
    temperature=0.7
)
```

## 🧪 Testing

### Manual Testing
Use the interactive API documentation at `/docs` to test endpoints manually.

### Automated Testing
```bash
# Install test dependencies
pip install pytest httpx

# Run tests (when implemented)
pytest tests/
```

### Health Check
```bash
curl http://localhost:8000/health
```

## 🚀 Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

### Production Considerations
1. **Environment Variables**: Use secure secret management
2. **Database**: Configure PostgreSQL for production
3. **Caching**: Set up Redis for session management
4. **Authentication**: Implement JWT or OAuth2
5. **Rate Limiting**: Add API rate limiting
6. **Monitoring**: Set up logging and monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add type hints to all functions
- Write comprehensive docstrings
- Include tests for new features
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Common Issues

**Issue**: API key not working
**Solution**: Ensure your API key is correctly set in the `.env` file and has sufficient credits.

**Issue**: Import errors
**Solution**: Make sure all dependencies are installed: `pip install -r requirements.txt`

**Issue**: Port already in use
**Solution**: Change the port in `.env` or stop the process using the port.

### Getting Help
- Check the [API documentation](http://localhost:8000/docs)
- Review the code examples in this README
- Open an issue on GitHub for bugs or feature requests

## 🔮 Roadmap

### Upcoming Features
- [ ] Real-time WebSocket collaboration
- [ ] Advanced workflow templates
- [ ] Plugin system for custom agents
- [ ] Export to various formats (PDF, EPUB, etc.)
- [ ] Advanced analytics and insights
- [ ] Mobile API support
- [ ] Integration with external writing tools

### Version History
- **v1.0.0**: Initial release with core agents and API
- **v0.9.0**: Beta release with collaboration features
- **v0.8.0**: Alpha release with basic multi-agent support

---

**Built with ❤️ using FastAPI, LangChain, and AI**

For more information, visit our [documentation](http://localhost:8000/docs) or contact the development team.