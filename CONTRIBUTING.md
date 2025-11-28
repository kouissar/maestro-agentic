# Contributing to Gemini 3 Agent System

Thank you for your interest in contributing to the Gemini 3 Agent System! This document provides guidelines and instructions for contributing.

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/maestro-agentic.git
   cd maestro-agentic
   ```
3. **Set up your development environment** following the instructions in [README.md](README.md)

## 🔧 Development Setup

### Backend (Python)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Or using uv:
uv pip install -r requirements.txt
```

### Frontend (React)

```bash
cd web_ui
npm install
```

### Environment Variables

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

## 📝 Making Changes

1. **Create a new branch** for your feature or bugfix:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our coding standards:

   - Write clear, descriptive commit messages
   - Follow existing code style and conventions
   - Add comments for complex logic
   - Update documentation as needed

3. **Test your changes**:

   - Test the backend: `python main.py`
   - Test the web UI: `cd web_ui && npm run dev`
   - Ensure all agents work correctly

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

## 🎯 Commit Message Convention

We follow conventional commits:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

## 🧪 Testing

Before submitting a pull request:

1. Test all agents (orchestrator, search, band_tour, workout)
2. Verify the web UI works correctly
3. Check that no sensitive data (API keys) are committed
4. Ensure `.gitignore` is working properly

## 📤 Submitting a Pull Request

1. **Push your branch** to your fork:

   ```bash
   git push origin feature/your-feature-name
   ```

2. **Open a Pull Request** on GitHub with:

   - Clear title and description
   - Reference any related issues
   - Screenshots/demos if applicable
   - List of changes made

3. **Wait for review** - maintainers will review your PR and may request changes

## 🐛 Reporting Bugs

When reporting bugs, please include:

- Description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Error messages or logs

## 💡 Suggesting Features

We welcome feature suggestions! Please:

- Check if the feature has already been requested
- Clearly describe the feature and its benefits
- Provide use cases and examples

## 📜 Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what's best for the project
- Help others learn and grow

## 🙏 Thank You!

Your contributions make this project better for everyone. We appreciate your time and effort!
