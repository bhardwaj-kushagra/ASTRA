# Contributing to ASTRA

Thank you for your interest in contributing to ASTRA (Adaptive Surveillance Tracking and Recognition Architecture)!

## Getting Started

1. **Fork the repository** and clone your fork locally
2. **Set up your development environment**:
   ```bash
   # Install dependencies
   powershell -File setup.ps1
   
   # Copy environment template
   cp .env.example .env
   ```

3. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Running Services Locally

```bash
# Start all services
powershell -File tools/scripts/start-all-services.ps1

# Or start individual services
cd services/ingestion
python main.py
```

### Testing Your Changes

```bash
# Run integration tests
python tools/scripts/test_integration.py

# Test individual endpoints
# See QUICKSTART.md for API examples
```

### Code Quality

- **Follow PEP 8** style guidelines for Python code
- **Add docstrings** to all functions and classes
- **Type hints** are encouraged for function signatures
- **Keep commits atomic** - one logical change per commit

### Commit Messages

Use clear, descriptive commit messages:

```
feat: Add graph-based attribution detector
fix: Resolve race condition in ingestion service
docs: Update EXTENSION_GUIDE with new connector pattern
refactor: Simplify detection registry logic
```

Prefixes:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

## Extending ASTRA

### Adding New Connectors

See `docs/EXTENSION_GUIDE.md` for detailed patterns:

```python
from connector import Connector, ConnectorRegistry

class MyConnector(Connector):
    async def fetch(self, config: dict) -> List[ContentEvent]:
        # Your implementation
        pass

ConnectorRegistry.register("my-connector", MyConnector)
```

### Adding New Detectors

```python
from detector import Detector, DetectorRegistry

class MyDetector(Detector):
    async def detect(self, text: str) -> Dict[str, Any]:
        # Your implementation
        pass

DetectorRegistry.register("my-detector", MyDetector)
```

## Pull Request Process

1. **Update documentation** if you've changed APIs or added features
2. **Test your changes** thoroughly
3. **Update CHANGELOG.md** with a brief description
4. **Submit PR** with:
   - Clear title describing the change
   - Description of what changed and why
   - References to related issues (if any)
   - Screenshots (for UI changes)

5. **Address review feedback** promptly

## Code Review Guidelines

### For Contributors
- Be open to feedback
- Respond to comments within 48 hours
- Update your PR based on review suggestions

### For Reviewers
- Be respectful and constructive
- Focus on code quality, security, and maintainability
- Approve when changes meet project standards

## Security

If you discover a security vulnerability:
- **DO NOT** open a public issue
- Email security details to: [your-security-email]
- Include: description, reproduction steps, potential impact

## Questions?

- Check `docs/` directory for additional documentation
- Open a discussion in GitHub Discussions
- Join our community chat (link TBD)

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

---

**Thank you for helping make ASTRA better!** 🚀
