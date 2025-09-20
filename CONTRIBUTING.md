# Contributing to MemeDoc

Thank you for your interest in contributing to MemeDoc!

## Getting Started

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test your changes locally
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/memedoc.git
cd memedoc

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows
# or
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your credentials
```

## Code Style

- Follow PEP 8 for Python code
- Use type hints where possible
- Add docstrings for new functions/classes
- Keep functions focused and small

## Adding New Scrapers

1. Create a new scraper class inheriting from `BaseScraper`
2. Implement the required methods
3. Add platform configuration in `config/platforms/`
4. Register the scraper in the registry

## Testing

Run the scraper locally before submitting:

```bash
python main.py
```

## Submitting Changes

- Create descriptive commit messages
- Reference issue numbers in commits when applicable
- Keep pull requests focused on a single feature/fix
- Update documentation if needed

## Code of Conduct

Be respectful and constructive in all interactions.