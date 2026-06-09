# Contributing

## Development Setup

Follow the [Quick Start](README.md#quick-start-local-development) guide.

## Code Style

- **Python**: Follow PEP 8. Run `ruff check .` before committing.
- **TypeScript/React**: Follow ESLint config. Run `npm run lint` before committing.
- **Imports**: Group standard lib, third-party, then local imports.

## Testing

```bash
cd backend
pytest -v --cov=app tests/
```

All PRs must maintain or improve test coverage.

## Pull Request Process

1. Create a feature branch from `main`
2. Write tests for new functionality
3. Ensure all tests pass
4. Update documentation if APIs change
5. Request review from a maintainer

## Commit Messages

Follow conventional commits:
- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation
- `refactor:` — Code change without feature/fix
- `test:` — Test additions/changes
- `chore:` — Maintenance tasks
