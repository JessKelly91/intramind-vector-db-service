# VectorDB Contracts

Protocol Buffer contracts for the Vector Database Service. This repository provides gRPC service definitions published as both **NuGet** (C#) and **PyPI** (Python) packages.

## 📦 Packages

### C# / .NET
[![NuGet](https://img.shields.io/nuget/v/VectorDB.Contracts)](https://www.nuget.org/packages/VectorDB.Contracts/)

```bash
dotnet add package VectorDB.Contracts
```

### Python
[![PyPI](https://img.shields.io/pypi/v/vectordb-contracts)](https://pypi.org/project/vectordb-contracts/)

```bash
pip install vectordb-contracts
```

## 🏗️ Architecture

This repository follows a **dual-publishing pattern** where:
- A single `.proto` file serves as the source of truth
- The C# project automatically generates code during build
- The Python package generates code during package build
- Both packages share the same version number from `VERSION` file

```
vector-db-contracts/
├── VERSION                                    # Shared version (e.g., "1.0.0")
├── src/
│   └── VectorDB.Contracts/                   # C# NuGet package
│       ├── VectorDB.Contracts.csproj
│       └── Protos/
│           └── vector_service.proto          # 📍 Single source of truth
├── python/
│   ├── setup.py                              # Python package config
│   ├── pyproject.toml
│   ├── vectordb_contracts/                   # Python package
│   │   └── __init__.py
│   └── scripts/
│       ├── generate_protos.py                # Reads from ../src/.../Protos/
│       └── build_package.py
└── .github/
    └── workflows/                            # CI/CD automation
        ├── test-python-package.yml           # Test on PR
        ├── test-nuget-package.yml            # Test on PR
        ├── publish-to-dev.yml                # DEV environment
        ├── publish-to-uat.yml                # UAT environment
        └── publish-to-prod.yml               # PROD environment
```

## 🚀 Usage

### C# / .NET

```csharp
using Grpc.Net.Client;
using VectorDB;

// Create a gRPC channel
var channel = GrpcChannel.ForAddress("https://localhost:5001");

// Create a client
var client = new VectorDBService.VectorDBServiceClient(channel);

// Make a request
var request = new InsertVectorRequest
{
    CollectionName = "documents",
    Content = "Sample text for vectorization",
    CorrelationId = Guid.NewGuid().ToString()
};

var response = await client.InsertVectorAsync(request);
Console.WriteLine($"Vector ID: {response.Id}");
```

### Python

```python
import grpc
from vectordb_contracts import vector_service_pb2
from vectordb_contracts import vector_service_pb2_grpc

# Create a gRPC channel
channel = grpc.insecure_channel('localhost:50051')

# Create a client stub
client = vector_service_pb2_grpc.VectorDBServiceStub(channel)

# Make a request
request = vector_service_pb2.InsertVectorRequest(
    collection_name="documents",
    content="Sample text for vectorization",
    correlation_id="123"
)

response = client.InsertVector(request)
print(f"Vector ID: {response.id}")
```

## 🛠️ Development

### Prerequisites

**For C# development:**
- .NET 8.0 SDK or later
- Visual Studio 2022 or VS Code with C# extension

**For Python development:**
- Python 3.9 or later
- pip

### Local Development Setup

#### C# Package

```bash
cd vector-db-contracts/src/VectorDB.Contracts

# Restore dependencies
dotnet restore

# Build (auto-generates proto code)
dotnet build

# Pack
dotnet pack --configuration Release
```

#### Python Package

```bash
cd vector-db-contracts/python

# Install development dependencies
pip install -e ".[dev]"

# Generate protobuf code
python scripts/generate_protos.py

# Test imports
python -c "from vectordb_contracts import vector_service_pb2, vector_service_pb2_grpc"

# Build package
python scripts/build_package.py --clean

# Install locally for testing
pip install dist/*.whl
```

## 📝 Making Changes to the Proto File

1. **Edit the proto file**: `src/VectorDB.Contracts/Protos/vector_service.proto`
2. **Update version**: Edit `VERSION` file (e.g., `1.1.0`)
3. **Test locally**:
   - C#: `dotnet build` in the C# project
   - Python: `python scripts/generate_protos.py` in the Python directory
4. **Commit changes**: The generated files are `.gitignore`d
5. **Publish**: Use GitHub Actions (see below)

## 🚢 Publishing Packages

This project uses an enterprise-grade **DEV → UAT → PROD** deployment workflow.

### Automated Testing

Pull requests automatically trigger:
- ✅ Python package build and import tests (Python 3.9-3.12)
- ✅ NuGet package build tests

### Deployment Environments

| Environment | Version Format | Target | Approval |
|-------------|----------------|--------|----------|
| **DEV** | `1.0.0-beta.X` | TestPyPI | None |
| **UAT** | `1.0.0-rc.X` | TestPyPI | Optional |
| **PROD** | `1.0.0` | PyPI + NuGet.org | **Required** |

### Quick Deploy Guide

**DEV (Development Testing):**
```bash
# Manual trigger or auto-deploy on push to develop branch
Actions → Publish to DEV → Run workflow
# Publishes: vectordb-contracts==1.0.0-beta.1
```

**UAT (Release Candidate):**
```bash
# Manual trigger for release validation
Actions → Publish to UAT → Run workflow
# Publishes: vectordb-contracts==1.0.0-rc.1
```

**PROD (Production Release):**
```bash
# Update VERSION file first
echo "1.0.0" > VERSION
git commit -am "chore: bump version to 1.0.0"
git push

# Trigger deployment (requires approval)
Actions → Publish to PROD → Run workflow → Approve
# Publishes: vectordb-contracts==1.0.0 (PyPI + NuGet.org)
```

📖 **For detailed deployment instructions**, see [DEPLOYMENT.md](DEPLOYMENT.md)

## 🔐 GitHub Environment Secrets Setup

Add secrets to GitHub Environments (Settings → Environments):

| Environment | Secret Name | Where to Get It |
|-------------|-------------|-----------------|
| **dev** | `TESTPYPI_API_TOKEN` | https://test.pypi.org/manage/account/token/ |
| **uat** | `TESTPYPI_API_TOKEN` | https://test.pypi.org/manage/account/token/ |
| **prod** | `PYPI_API_TOKEN` | https://pypi.org/manage/account/token/ |
| **prod** | `NUGET_API_KEY` | https://www.nuget.org/account/apikeys |

**Important:** Configure the **prod** environment to require manual approval before deployment.

📖 **Detailed setup instructions**: [DEPLOYMENT.md](DEPLOYMENT.md)

## 📚 Service Definition

The Vector Database Service provides the following operations:

### Vector Operations
- `InsertVector` - Insert a single vector
- `InsertVectorBatch` - Insert multiple vectors
- `GetVector` - Retrieve a vector by ID
- `UpdateVector` - Update an existing vector
- `DeleteVector` - Delete a vector

### Search Operations
- `SemanticSearch` - Perform semantic similarity search
- `StreamSearch` - Streaming search results

### Collection Operations
- `CreateCollection` - Create a new collection
- `ListCollections` - List all collections
- `GetCollection` - Get collection details
- `DeleteCollection` - Delete a collection

### Health Check
- `HealthCheck` - Service health status

For detailed message definitions, see [`vector_service.proto`](src/VectorDB.Contracts/Protos/vector_service.proto).

## 📄 License

MIT License - see [LICENSE](../LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes to the proto file
4. Test both C# and Python builds locally
5. Submit a pull request

## 🔗 Links

- **GitHub Repository**: https://github.com/JessKelly91/ai-vector-db-practice
- **PyPI Package**: https://pypi.org/project/vectordb-contracts/
- **TestPyPI Package**: https://test.pypi.org/project/vectordb-contracts/
- **NuGet Package**: https://www.nuget.org/packages/VectorDB.Contracts/

