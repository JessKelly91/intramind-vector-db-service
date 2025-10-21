# Deployment Guide - DEV/UAT/PROD Workflow

This document explains the enterprise-grade deployment workflow for VectorDB Contracts packages.

## 🏗️ Environment Strategy

| Environment | Purpose | Version Format | Approval Required | Target |
|-------------|---------|----------------|-------------------|--------|
| **DEV** | Development testing, rapid iteration | `1.0.0-beta.X` | ❌ No | TestPyPI + Artifacts |
| **UAT** | Release candidate validation | `1.0.0-rc.X` | ⚠️ Optional | TestPyPI + Artifacts |
| **PROD** | Production release | `1.0.0` | ✅ **Yes** | PyPI + NuGet.org |

---

## 📦 Version Naming Convention

### DEV (Beta Versions)
```
Base version from VERSION file: 1.0.0
DEV version: 1.0.0-beta.1, 1.0.0-beta.2, etc.

Install:
pip install --index-url https://test.pypi.org/simple/ vectordb-contracts==1.0.0-beta.1
```

### UAT (Release Candidates)
```
Base version from VERSION file: 1.0.0
UAT version: 1.0.0-rc.1, 1.0.0-rc.2, etc.

Install:
pip install --index-url https://test.pypi.org/simple/ vectordb-contracts==1.0.0-rc.1
```

### PROD (Production Versions)
```
Version from VERSION file: 1.0.0

Install:
pip install vectordb-contracts==1.0.0
dotnet add package VectorDB.Contracts --version 1.0.0
```

---

## 🚀 Deployment Workflow

### Standard Release Process

```
1. Development
   └─→ Push to develop branch OR manually trigger
       └─→ Publish to DEV (1.0.0-beta.X)
           └─→ Test on TestPyPI
           
2. User Acceptance Testing
   └─→ When ready for UAT
       └─→ Publish to UAT (1.0.0-rc.X)
           └─→ Validate release candidate
           
3. Production
   └─→ When UAT passes
       └─→ Update VERSION file to 1.0.0
       └─→ Publish to PROD (requires approval)
           └─→ Public release on PyPI + NuGet.org
```

---

## 🔧 GitHub Environment Setup

### Step 1: Create Environments

Go to: **GitHub Repo → Settings → Environments**

Create these three environments:

#### 1. **dev** Environment
- **Name**: `dev`
- **Protection rules**:
  - ⚠️ Required reviewers: None (auto-deploy for rapid testing)
  - ⚠️ Wait timer: 0 minutes
  - ✅ Deployment branches: All branches OR specific (develop, dev)
- **Secrets**:
  - `TESTPYPI_API_TOKEN` - From https://test.pypi.org/manage/account/token/

#### 2. **uat** Environment
- **Name**: `uat`
- **Protection rules**:
  - ⚠️ Required reviewers: Optional (your choice)
  - ⚠️ Wait timer: 0 minutes
  - ✅ Deployment branches: `main`, `master`, `release/*`
- **Secrets**:
  - `TESTPYPI_API_TOKEN` - Same as DEV (TestPyPI allows multiple versions)

#### 3. **prod** Environment  
- **Name**: `prod`
- **Protection rules**:
  - ✅ **Required reviewers**: Add yourself (IMPORTANT!)
  - ⚠️ Wait timer: 5 minutes (optional - time to review)
  - ✅ Deployment branches: **Only** `main` or `master`
- **Secrets**:
  - `PYPI_API_TOKEN` - From https://pypi.org/manage/account/token/
  - `NUGET_API_KEY` - From https://www.nuget.org/account/apikeys

---

## 📝 How to Deploy

### Deploy to DEV

**Automatic (on push to develop branch):**
```bash
git checkout develop
git add .
git commit -m "feat: add new feature"
git push origin develop
```
Workflow automatically triggers and publishes `1.0.0-beta.TIMESTAMP`

**Manual (any branch):**
1. Go to **Actions** → **Publish to DEV**
2. Click **Run workflow**
3. Enter beta number (e.g., `1` for `1.0.0-beta.1`)
4. Click **Run workflow**

**Result:**
- Python package: `vectordb-contracts==1.0.0-beta.1` on TestPyPI
- NuGet package: Saved as GitHub artifact

---

### Deploy to UAT

**Manual only:**
1. Go to **Actions** → **Publish to UAT**
2. Click **Run workflow**
3. Enter RC number (e.g., `1` for `1.0.0-rc.1`)
4. Click **Run workflow**
5. If approval required, approve the deployment

**Result:**
- Python package: `vectordb-contracts==1.0.0-rc.1` on TestPyPI
- NuGet package: Saved as GitHub artifact

**Testing:**
```bash
# Install and test
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ vectordb-contracts==1.0.0-rc.1

python -c "
from vectordb_contracts import vector_service_pb2, vector_service_pb2_grpc
print('✓ UAT package works!')
"
```

---

### Deploy to PROD

**Prerequisites:**
1. ✅ UAT testing complete and successful
2. ✅ Update `VERSION` file to production version (e.g., `1.0.0`)
3. ✅ Commit VERSION file change
4. ✅ All tests passing

**Steps:**
1. **Update VERSION file:**
   ```bash
   echo "1.0.0" > vector-db-contracts/VERSION
   git add vector-db-contracts/VERSION
   git commit -m "chore: bump version to 1.0.0"
   git push origin main
   ```

2. **Trigger deployment:**
   - Go to **Actions** → **Publish to PROD**
   - Click **Run workflow**
   - Leave version empty (uses VERSION file) OR specify manually
   - Click **Run workflow**

3. **Approve deployment:**
   - Workflow will pause and wait for approval
   - Review the pending deployment
   - Click **Review deployments**
   - Select **prod** environment
   - Click **Approve and deploy**

4. **Verify:**
   - Wait for workflow to complete
   - Check PyPI: https://pypi.org/project/vectordb-contracts/
   - Check NuGet: https://www.nuget.org/packages/VectorDB.Contracts/

**Result:**
- Python package: `vectordb-contracts==1.0.0` on **public PyPI**
- NuGet package: `VectorDB.Contracts 1.0.0` on **NuGet.org**

---

## 🎯 Secrets Summary

| Secret Name | Environments | Where to Get | Purpose |
|-------------|--------------|--------------|---------|
| `TESTPYPI_API_TOKEN` | dev, uat | https://test.pypi.org/manage/account/token/ | Publish test packages |
| `PYPI_API_TOKEN` | prod | https://pypi.org/manage/account/token/ | Publish production Python package |
| `NUGET_API_KEY` | prod | https://www.nuget.org/account/apikeys | Publish production NuGet package |

---

## 🔍 Troubleshooting

### DEV deployment fails with "403 Forbidden"
- Check `TESTPYPI_API_TOKEN` is set in **dev** environment secrets
- Verify token has not expired
- Try regenerating token on TestPyPI

### UAT shows same issue as another version
- Use a new RC number: `1.0.0-rc.2`, `1.0.0-rc.3`, etc.
- TestPyPI doesn't allow overwriting versions

### PROD deployment pending forever
- Check if approval is required (Settings → Environments → prod)
- Go to Actions → pending workflow → Review deployments → Approve

### Version mismatch
- Ensure VERSION file is committed before PROD deployment
- Check workflow logs for actual version being published

### NuGet package not appearing
- NuGet.org can take 10-15 minutes to index new packages
- Check workflow logs for push errors
- Verify NUGET_API_KEY is valid and has push permissions

---

## 📊 Workflow Comparison

| Feature | DEV | UAT | PROD |
|---------|-----|-----|------|
| **Trigger** | Auto + Manual | Manual only | Manual only |
| **Approval** | ❌ None | Optional | ✅ Required |
| **Python Target** | TestPyPI | TestPyPI | PyPI |
| **NuGet Target** | Artifact | Artifact | NuGet.org |
| **Version** | beta.X | rc.X | Production |
| **Testing Purpose** | Feature testing | Release validation | Public release |

---

## 🎓 Best Practices

### Version Management
- Keep VERSION file at next planned release (e.g., `1.1.0`)
- DEV/UAT auto-add suffixes (`-beta.X`, `-rc.X`)
- Only bump VERSION for PROD releases

### Deployment Cadence
- **DEV**: Multiple times per day (rapid iteration)
- **UAT**: 1-3 times per feature (release candidate)
- **PROD**: When UAT is validated (weekly/monthly)

### Testing Strategy
```
DEV (beta)
└─ Developers test new features
   └─ Iterate quickly on feedback
      
UAT (rc)
└─ Stakeholders validate release
   └─ Full integration testing
      
PROD
└─ Public release
   └─ Monitor for issues
```

### Git Workflow Integration
```
feature/new-feature
└─→ develop (triggers DEV)
    └─→ main (manual UAT)
        └─→ tag v1.0.0 (manual PROD)
```

---

## 📚 Related Documentation

- [README.md](README.md) - Main project documentation
- [GETTING_STARTED.md](GETTING_STARTED.md) - First-time setup
- [python/README.md](python/README.md) - Python package usage

---

## 🚦 Quick Reference Commands

```bash
# Test DEV package
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ vectordb-contracts==1.0.0-beta.1

# Test UAT package
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ vectordb-contracts==1.0.0-rc.1

# Install PROD package
pip install vectordb-contracts==1.0.0
dotnet add package VectorDB.Contracts --version 1.0.0

# Update VERSION for production
echo "1.1.0" > vector-db-contracts/VERSION
git add vector-db-contracts/VERSION
git commit -m "chore: bump version to 1.1.0"
```

---

**Questions?** Open an issue on GitHub or check the workflow logs for detailed error messages.

