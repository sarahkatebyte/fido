# FIDO 🐕

**F**aithful **I**nbox **D**e-clutter **O**rchestrator

*"FIDO fetches!"* - An automated email cleaning bot that runs as a Kubernetes CronJob

## What is FIDO?

FIDO is a Python application that automatically cleans your Gmail inbox by:
- 🔍 Searching emails using Gmail queries and custom grep/regex patterns
- 🗑️ Deleting, archiving, or labeling emails based on configurable rules
- ⏰ Running on a schedule as a Kubernetes CronJob
- 🛡️ Safe with dry-run mode to preview before executing

## Features

- **Two-stage search**: Gmail API queries + grep engine for deep pattern matching
- **Flexible rules**: Delete, archive, or label emails
- **Configurable**: Rules stored in Kubernetes ConfigMap
- **Containerized**: Docker + Kubernetes deployment
- **Observable**: Detailed logging, optional Slack notifications

## Project Status

🚧 **Under Construction** - Week 1 of 3-week build

- [x] Project structure
- [x] Python environment setup
- [x] Gmail API integration
- [ ] Grep engine
- [ ] Docker container
- [ ] Kubernetes deployment

## Quick Start

### Prerequisites

- Python 3.11+
- Docker (for containerization)
- Kubernetes cluster (Minikube for local)
- Gmail account with API access

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy example config
cp config/rules.example.yaml config/rules.yaml

# Edit rules (start with dry_run: true!)
vim config/rules.yaml

# Run FIDO locally
python -m src.fido
```

## Project Structure

```
fido/
├── src/
│   ├── fido.py           # Main orchestrator
│   ├── gmail_client.py   # Gmail API wrapper
│   ├── grep_engine.py    # Pattern matching engine
│   └── config.py         # Config loading
├── k8s/
│   ├── cronjob.yaml      # CronJob definition
│   ├── configmap.yaml    # Rules configuration
│   └── secret.yaml       # OAuth credentials
├── config/
│   └── rules.example.yaml # Example rules
├── tests/
├── Dockerfile
└── requirements.txt
```

## Development Timeline

- **Week 1**: Core functionality (Gmail API + grep engine)
- **Week 2**: Kubernetes deployment
- **Week 3**: Polish, documentation, tests

## License

MIT

---

*Built with 🐕 by Sarah Kate*
