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
│   ├── appSettings.json        # Base configuration (non-secret settings)
│   └── env.example             # Environment variables template
├── .env                        # Local environment variables (gitignored, create from template)
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

# Optional: If using Azure Application Insights for telemetry
pip install -r requirements-azure.txt
```

4. Configure local environment variables:
```bash
# Copy the environment template
cp config/env.example .env
```

Edit `.env` with your local configuration:
```bash
# Environment
ENVIRONMENT=Local

# Vectorizer Configuration
DEFAULT_VECTORIZER=text2vec-transformers  # Options: text2vec-transformers, text2vec-openai, none
VECTORIZER_ENABLED=true  # Set to false to disable vectorizers (uses 'none')

# Weaviate Configuration
WEAVIATE_URL=http://localhost:8080
WEAVIATE_KEY=  # Leave empty for local docker-compose (anonymous access enabled)

# OpenAI Configuration (OPTIONAL - only needed if you want to use OpenAI embeddings)
OPENAI_API_KEY=  # Leave empty to use free local vectorization

# Application Insights (optional)
APPINSIGHTS_CONNECTION_STRING=

# Application ID (optional)
APPLICATION_ID=weaviate-client-local
```

**For local development with docker-compose:** You can leave `WEAVIATE_KEY` and `OPENAI_API_KEY` empty - the free local vectorizer will work without any API keys!

**Note**: `.env` is gitignored and will not be committed. For GitHub Actions/production, configure these as GitHub Secrets.

### Running Weaviate Locally with Docker Compose (Recommended)

This project includes a `docker-compose.yml` file configured with **free local vectorization** (no API keys required).

#### Quick Start

1. **Start Weaviate**:
```bash
docker-compose up -d
```

2. **Check status**:
```bash
docker-compose ps
```

3. **View logs**:
```bash
docker-compose logs -f weaviate
```

4. **Stop Weaviate**:
```bash
docker-compose down
```

5. **Stop and remove data** (fresh start):
```bash
docker-compose down -v
```

**Weaviate will be available at:**
- REST API: `http://localhost:8080`
- gRPC API: `http://localhost:50051`
- Health check: `http://localhost:8080/v1/.well-known/ready`

**Data Persistence:**
- Data is stored in a Docker volume named `weaviate_data`
- Data persists between container restarts
- To wipe all data: `docker-compose down -v`

#### Vectorization Options

**Default: Free Local Vectorization (text2vec-transformers)** ✅ **Recommended for Development**
- ✅ **Completely free** - no API keys or costs
- ✅ **Works offline** - runs entirely on your machine
- ✅ **Pre-configured** - works out of the box
- Uses `sentence-transformers/all-MiniLM-L6-v2` model
- Good quality embeddings for most use cases
- Trade-off: Slower than cloud APIs, uses more local resources

**Optional: OpenAI Embeddings** 💰 **Requires Paid API Key**
- Higher quality embeddings
- Faster processing (cloud-based)
- Costs money (~$0.0001 per 1K tokens for text-embedding-3-small)

To enable OpenAI:
1. Get an API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. In `docker-compose.yml`, uncomment the `OPENAI_APIKEY` line:
   ```yaml
   OPENAI_APIKEY: ${OPENAI_API_KEY:-}
   ```
3. Add to `ENABLE_MODULES`: `'text2vec-transformers,text2vec-openai'`
4. Set `OPENAI_API_KEY` in your `.env` file
5. Restart: `docker-compose down && docker-compose up -d`

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

The project uses a **production-like two-tier configuration system** following [12-factor app methodology](https://12factor.net/config):

### 1. Base Configuration (`appSettings.json`)
- Contains **non-secret configuration only** (logging levels, feature flags, etc.)
- Checked into source control
- Environment-specific values are left empty and provided via environment variables

### 2. Environment Variables (Primary Configuration Source)

**Local Development:**
- Create a `.env` file in the project root (gitignored)
- Copy from `config/env.example` template
- Contains your local API keys and secrets
- Automatically loaded via `python-dotenv`

**Production/GitHub Actions:**
- Configure secrets in GitHub repository settings (Settings → Secrets and variables → Actions)
- GitHub automatically exposes secrets as environment variables in workflows
- Required variables:
  - `WEAVIATE_URL`
  - `WEAVIATE_KEY`
  - `ENVIRONMENT`
  - `DEFAULT_VECTORIZER` (optional - defaults based on ENVIRONMENT)
  - `VECTORIZER_ENABLED` (optional - set to 'false' in CI)
- Optional variables:
  - `OPENAI_API_KEY` (only if using OpenAI embeddings)
  - `APPINSIGHTS_CONNECTION_STRING` (telemetry)

### Accessing Configuration

```python
from src.weaviate_client.config import get_settings

settings = get_settings()
url = settings.weaviate_url
api_key = settings.weaviate_api_key

# Or use dot notation
custom_value = settings.get('CustomSection.CustomKey', 'default_value')
```

### GitHub Actions Example

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run application
        env:
          WEAVIATE_URL: ${{ secrets.WEAVIATE_URL }}
          WEAVIATE_KEY: ${{ secrets.WEAVIATE_KEY }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          ENVIRONMENT: Production
        run: python scripts/example.py
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
