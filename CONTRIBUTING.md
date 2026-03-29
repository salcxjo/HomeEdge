# Contributing to HomeEdge

Thank you for your interest in HomeEdge! This is primarily a personal learning project, but contributions, suggestions, and feedback are welcome.

## How to Contribute

### Reporting Issues

If you encounter bugs or have feature suggestions:

1. **Search existing issues** to avoid duplicates
2. **Open a new issue** with a clear title and description
3. **Include details:**
   - Hardware configuration (Pico 2W, Pi 4, sensors)
   - Software versions (Python, MicroPython, library versions)
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Error messages or logs

### Suggesting Enhancements

Feature requests are welcome! Please include:
- **Use case:** Why is this feature useful?
- **Proposed solution:** How would it work?
- **Alternatives considered:** Other approaches you've thought about

### Code Contributions

1. **Fork the repository**
2. **Create a feature branch:** `git checkout -b feature/your-feature-name`
3. **Make your changes:**
   - Follow existing code style
   - Add comments for complex logic
   - Test thoroughly on actual hardware
4. **Commit with clear messages:** `git commit -m "Add feature: description"`
5. **Push to your fork:** `git push origin feature/your-feature-name`
6. **Open a Pull Request** with:
   - Description of changes
   - Testing performed
   - Any new dependencies

## Development Setup

See [docs/setup.md](docs/setup.md) for complete installation instructions.

Quick start:
```bash
git clone https://github.com/yourusername/HomeEdge.git
cd HomeEdge
pip install -r requirements_pi.txt --break-system-packages
```

## Code Style

### Python (Pi 4)
- Follow PEP 8 style guide
- Use type hints where helpful
- Maximum line length: 100 characters
- Docstrings for functions and classes

### MicroPython (Pico 2W)
- Keep memory usage in mind
- Avoid large imports (bloats flash storage)
- Comment hardware-specific assumptions
- Test on actual Pico hardware

### Documentation
- Update README.md if adding features
- Add to docs/ if substantial new functionality
- Include wiring diagrams for new sensors
- Explain "why" not just "what"

## Testing

Currently no automated test suite (hardware-in-the-loop makes this challenging).

**Manual testing checklist:**
- [ ] All sensors read correctly
- [ ] MQTT messages publish successfully
- [ ] Dashboard displays new data
- [ ] No Python exceptions or crashes
- [ ] Runs for >1 hour without issues

## Areas for Contribution

Some ideas where help would be appreciated:

### Hardware
- Testing with different sensor modules/manufacturers
- PCB design for cleaner deployment
- 3D-printed enclosures
- Low-power optimization

### Software
- Unit tests for non-hardware code
- CI/CD pipeline (GitHub Actions)
- Docker containerization
- Alternative dashboard frameworks

### Machine Learning
- LSTM-based time series forecasting
- Transfer learning for custom object detection
- Federated learning across multiple nodes
- Model compression techniques

### Documentation
- Video tutorials
- Fritzing diagrams
- Troubleshooting guides
- Non-English translations

### Integrations
- Home Assistant integration
- Prometheus/Grafana metrics export
- IFTTT webhooks
- Voice assistant integration

## Questions?

Open an issue or reach out via mirikhoo@ualberta.ca

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
