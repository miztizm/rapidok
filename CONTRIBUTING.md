# Contributing to Rapidok

Thank you for your interest in contributing to this project! Rapidok is a fork of the original work by [xsrazy](https://github.com/xsrazy/Download-All-Tiktok-Videos), maintained and enhanced by miztizm.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior vs actual behavior
- Your environment (OS, Python version, yt-dlp version)
- Error messages or logs (if applicable)

### Suggesting Enhancements

Feature requests are welcome! Please include:
- A clear description of the feature
- Why this feature would be useful
- Potential implementation approach (if you have ideas)

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
   - Follow existing code style
   - Add comments for complex logic
   - Update documentation if needed
4. **Test your changes** thoroughly
5. **Commit your changes** (`git commit -m 'Add amazing feature'`)
6. **Push to the branch** (`git push origin feature/amazing-feature`)
7. **Open a Pull Request**

### Code Style

- Follow PEP 8 guidelines for Python code
- Use meaningful variable and function names
- Add docstrings for functions and classes
- Keep functions focused and modular

### Testing

Before submitting a PR:
- Test with multiple TikTok URLs
- Test both watermark and no-watermark modes
- Test with different worker counts
- Verify error handling works correctly

## Development Setup

```bash
# Clone your fork
git clone https://github.com/miztizm/rapidok
cd rapidok

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies (if any)
pip install pylint pytest black
```

## Questions?

Feel free to open an issue for questions or discussions.

## Attribution

Remember that this project is built on the work of xsrazy. Please maintain proper attribution in all contributions.

---

**Happy coding! 🚀**

*- miztizm*
