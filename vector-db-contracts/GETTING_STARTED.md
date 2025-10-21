# Getting Started with VectorDB Contracts

This guide will help you set up and test the dual-publishing contracts package for the first time.

## 🎯 What Was Created

Your repository now has a complete dual-publishing setup:

```
vector-db-contracts/
├── VERSION (1.0.0)                           # ✅ Shared version source
├── .github/workflows/                        # ✅ CI/CD automation
│   ├── test-python-package.yml
│   ├── test-nuget-package.yml
│   ├── publish-python-testpypi.yml
│   ├── publish-python-pypi.yml
│   └── publish-nuget.yml
├── src/VectorDB.Contracts/                   # ✅ C# NuGet package
│   ├── VectorDB.Contracts.csproj (updated)
│   └── Protos/vector_service.proto
├── python/                                   # ✅ Python package structure
│   ├── setup.py
│   ├── pyproject.toml
│   ├── MANIFEST.in
│   ├── README.md
│   ├── .gitignore
│   ├── vectordb_contracts/
│   │   ├── __init__.py
│   │   └── py.typed
│   └── scripts/
│       ├── generate_protos.py
│       └── build_package.py
├── README.md                                 # ✅ Main documentation
└── GETTING_STARTED.md                        # ✅ This file
```

## 📋 Next Steps

### Step 1: Test Python Package Locally (5 minutes)

```bash
# Navigate to Python package directory
cd vector-db-contracts/python

# Install development dependencies
pip install grpcio-tools build twine

# Generate protobuf code
python scripts/generate_protos.py

# You should see:
# ✓ Successfully generated protobuf files:
#   - vectordb_contracts/vector_service_pb2.py
#   - vectordb_contracts/vector_service_pb2_grpc.py

# Test imports
python -c "from vectordb_contracts import vector_service_pb2, vector_service_pb2_grpc; print('✓ Imports work!')"

# Build the package
python scripts/build_package.py --clean

# Install locally
pip install dist/*.whl

# Test the installed package
python -c "from vectordb_contracts import vector_service_pb2; print('✓ Package installed successfully!')"
```

### Step 2: Test C# Package Locally (5 minutes)

```bash
# Navigate to C# project
cd vector-db-contracts/src/VectorDB.Contracts

# Restore dependencies
dotnet restore

# Build (this auto-generates proto code and reads VERSION file)
dotnet build --configuration Release

# Pack the NuGet package
dotnet pack --configuration Release --output ../../nupkg

# Check the version matches VERSION file
ls ../../nupkg/
# Should show: VectorDB.Contracts.1.0.0.nupkg
```

### Step 3: Setup GitHub Environments & Secrets (10 minutes)

This project uses **DEV → UAT → PROD** deployment environments.

#### 3a. Create Environments

1. Go to your GitHub repo → **Settings** → **Environments**
2. Click **New environment**
3. Create **three environments**:
   - `dev` (Development)
   - `uat` (User Acceptance Testing)
   - `prod` (Production)

#### 3b. Configure Environment Protection Rules

**For dev environment:**
- No protection rules needed (auto-deploy)

**For uat environment:**
- Optional: Add reviewers if you want approval

**For prod environment** (IMPORTANT):
- ✅ **Check "Required reviewers"**
- ✅ **Add yourself as a reviewer**
- ✅ **Deployment branches**: Select "Selected branches" → Add `main` or `master`

#### 3c. Add Secrets to Environments

**Get TestPyPI Token:**
1. Go to https://test.pypi.org/ and register
2. Go to https://test.pypi.org/manage/account/token/
3. Click "Add API token"
   - Token name: `github-actions-vectordb-contracts`
   - Scope: "Entire account"
4. **Copy the token** (starts with `pypi-...`)

**Add to dev environment:**
1. Click on **dev** environment
2. Click "Add secret"
   - Name: `TESTPYPI_API_TOKEN`
   - Secret: Paste the token

**Add to uat environment:**
1. Click on **uat** environment
2. Click "Add secret"
   - Name: `TESTPYPI_API_TOKEN`
   - Secret: Same token as dev

**For prod environment (optional for now):**
- `PYPI_API_TOKEN` - Get from https://pypi.org/ (when ready for public release)
- `NUGET_API_KEY` - Get from https://www.nuget.org/account/apikeys (when ready)

### Step 4: Publish to DEV (First Test Publish!)

1. Go to your GitHub repository
2. Click **Actions** tab
3. Click **Publish to DEV** (left sidebar)
4. Click **Run workflow** (right side)
5. Enter beta number: `1`
6. Click **Run workflow** button
7. Wait for the workflow to complete (~2 minutes)

If successful, you'll see:
```
✅ DEV package published to TestPyPI!

Version: 1.0.0-beta.1
View on TestPyPI: https://test.pypi.org/project/vectordb-contracts/1.0.0-beta.1/
```

### Step 5: Test Install from DEV

```bash
# Create a fresh virtual environment for testing
python -m venv test-env
source test-env/bin/activate  # On Windows: test-env\Scripts\activate

# Install DEV version from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ vectordb-contracts==1.0.0-beta.1

# Test it works
python -c "
from vectordb_contracts import vector_service_pb2, vector_service_pb2_grpc
print('✓ Successfully installed from TestPyPI!')
print(f'Package: vectordb_contracts')
print(f'Available modules: {dir(vector_service_pb2)[:3]}...')
"

# Deactivate when done
deactivate
```

## 🎉 Success Checklist

After completing the steps above, verify:

- [ ] Python protobuf generation works locally
- [ ] Python package builds without errors
- [ ] C# project builds and reads VERSION file correctly
- [ ] GitHub environments created (dev, uat, prod)
- [ ] Secrets configured in environments
- [ ] Package successfully published to DEV environment
- [ ] DEV package can be installed from TestPyPI
- [ ] Imports work correctly after installation

## 🚀 What's Next?

### For Development

1. **Make changes to proto file**: Edit `src/VectorDB.Contracts/Protos/vector_service.proto`
2. **Update version**: Edit `VERSION` file (e.g., change to `1.1.0`)
3. **Test locally**: Run build scripts for both Python and C#
4. **Commit changes**: Generated files are gitignored automatically
5. **Push to GitHub**: Automated tests will run on PR

### For UAT and Production Publishing

**UAT (Release Candidate Testing):**
```bash
# When ready for UAT validation
Actions → Publish to UAT → Run workflow
# Publishes: 1.0.0-rc.1
```

**PROD (Public Release):**
```bash
# 1. Update VERSION file
echo "1.0.0" > vector-db-contracts/VERSION
git commit -am "chore: bump version to 1.0.0"
git push

# 2. Configure prod secrets first:
#    - PYPI_API_TOKEN (from pypi.org)
#    - NUGET_API_KEY (from nuget.org)

# 3. Trigger deployment
Actions → Publish to PROD → Run workflow

# 4. Approve deployment when prompted
Actions → Review pending deployments → Approve
```

📖 **Full deployment guide**: [DEPLOYMENT.md](DEPLOYMENT.md)

## 📚 Quick Reference

### Common Commands

```bash
# Python: Generate protos
cd vector-db-contracts/python
python scripts/generate_protos.py

# Python: Build package
python scripts/build_package.py --clean

# Python: Install locally
pip install -e .

# C#: Build
cd vector-db-contracts/src/VectorDB.Contracts
dotnet build

# C#: Pack
dotnet pack --configuration Release --output ../../nupkg

# Update version (both packages)
echo "1.1.0" > vector-db-contracts/VERSION
```

### File Locations

- **Proto source**: `src/VectorDB.Contracts/Protos/vector_service.proto`
- **Version**: `VERSION` (root of vector-db-contracts/)
- **Python generated files**: `python/vectordb_contracts/*_pb2.py` (gitignored)
- **C# generated files**: `src/VectorDB.Contracts/obj/` (gitignored)

## 🆘 Troubleshooting

### Python: "Module not found: grpc_tools"

```bash
pip install grpcio-tools
```

### Python: Generated files not found

```bash
cd vector-db-contracts/python
python scripts/generate_protos.py
```

### C#: Version not updating

The VERSION file is read at build time. Make sure to:
1. Edit the VERSION file
2. Run `dotnet clean`
3. Run `dotnet build`

### GitHub Actions: Workflow not running

Check that:
- Workflow files are in `.github/workflows/` directory
- File extensions are `.yml` (not `.yaml`)
- Files are committed and pushed to GitHub

### TestPyPI: "Project name already exists"

If someone else has already taken `vectordb-contracts` on TestPyPI, you can:
1. Use a different name in `setup.py` (e.g., `jk-vectordb-contracts`)
2. Or continue - TestPyPI clears old test packages periodically

## 📖 Documentation

- **Main README**: [README.md](README.md)
- **Python README**: [python/README.md](python/README.md)
- **Proto definition**: [src/VectorDB.Contracts/Protos/vector_service.proto](src/VectorDB.Contracts/Protos/vector_service.proto)

## 🤝 Need Help?

- Check the [main README](README.md) for detailed documentation
- Review [GitHub Actions workflows](.github/workflows/) for CI/CD details
- Open an issue on GitHub if you encounter problems

---

**Ready to start?** Begin with Step 1 above! 🎯

