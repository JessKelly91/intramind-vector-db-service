# Weaviate Python Client Project

A Python project for interacting with Weaviate vector database, featuring collection management, document insertion, and semantic search capabilities.

## Project Structure

```
ai-vector-db-practice/
├── src/
│   └── weaviate_client/
│       ├── __init__.py
│       ├── client.py          # Main Weaviate client connection
│       ├── config.py           # Configuration manager
│       ├── models.py           # Pydantic models for documents
│       ├── collections.py      # Collection/schema management
│       └── queries.py          # Query and CRUD operations
├── scripts/
│   └── example.py              # Example usage script
├── tests/                      # Unit tests (empty)
├── config/
│   ├── appSettings.json        # Base configuration (for Azure/Production)
│   └── appSettings.Local.json.example  # Local settings template
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup

### Prerequisites

- Python 3.8+
- A running Weaviate instance (local or cloud)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-vector-db-practice
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure local settings:
```bash
cd config
cp appSettings.Local.json.example appSettings.Local.json
```

Edit `appSettings.Local.json` with your local configuration:
```json
{
  "Weaviate": {
    "Url": "http://localhost:8080",
    "ApiKey": "your-weaviate-api-key-here",
    "DefaultVectorizer": "text2vec-openai"
  },
  "OpenAI": {
    "ApiKey": "your-openai-api-key-here"
  },
  "Logging": {
    "Level": "INFO"
  }
}
```

**Note**: `appSettings.Local.json` is gitignored and will not be committed. In production/Azure, configure `appSettings.json` with values from Azure KeyVault or Pipeline Library variables.

### Running Weaviate Locally

Using Docker:
```bash
docker run -d \
  -p 8080:8080 \
  -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
  -e PERSISTENCE_DATA_PATH=/var/lib/weaviate \
  -e ENABLE_MODULES=text2vec-openai \
  -e OPENAI_APIKEY=your_openai_key \
  semitechnologies/weaviate:latest
```

Or use Docker Compose for a more complete setup.

## Usage

### Basic Example

Run the example script:
```bash
python scripts/example.py
```

### Using the Client

```python
from src.weaviate_client import WeaviateClient, Document
from src.weaviate_client.collections import CollectionManager
from src.weaviate_client.queries import QueryManager
from datetime import datetime

# Connect to Weaviate
with WeaviateClient() as client:
    # Create a collection
    collections = CollectionManager(client.client)
    collections.create_collection(
        name="MyCollection",
        description="My documents"
    )

    # Insert documents
    queries = QueryManager(client.client, "MyCollection")
    doc = Document(
        content="Sample document content",
        metadata={"author": "John Doe"},
        created_at=datetime.now()
    )
    doc_id = queries.insert(doc)

    # Search
    results = queries.search("sample query", limit=5)
    for result in results:
        print(f"Score: {result.score}, Content: {result.content}")
```

## Features

- **Connection Management**: Easy connection to local or cloud Weaviate instances
- **JSON Configuration**: Uses appSettings.json pattern for configuration management
- **Collection Management**: Create, delete, and list collections
- **Document Operations**: Insert single or multiple documents with metadata
- **Semantic Search**: Vector-based similarity search
- **CRUD Operations**: Full create, read, update, delete support
- **Type Safety**: Pydantic models for data validation
- **Context Manager**: Automatic connection handling

## Configuration

The project uses a two-tier configuration system:

### Local Development
- Create `config/appSettings.Local.json` (gitignored) with your local settings
- This file overrides base settings in `appSettings.json`

### Production/Azure
- `appSettings.json` contains base configuration
- Populate with Azure KeyVault secrets or Azure Pipeline Library variables
- Can be updated during deployment pipeline

### Accessing Configuration

```python
from src.weaviate_client.config import get_settings

settings = get_settings()
url = settings.weaviate_url
api_key = settings.weaviate_api_key

# Or use dot notation
custom_value = settings.get('CustomSection.CustomKey', 'default_value')
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Style

This project uses standard Python conventions. Consider using:
- `black` for formatting
- `pylint` for linting
- `mypy` for type checking

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License

## Resources

- [Weaviate Documentation](https://weaviate.io/developers/weaviate)
- [Weaviate Python Client](https://weaviate.io/developers/weaviate/client-libraries/python)
