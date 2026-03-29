# Contributing to RageType

Thanks for wanting to contribute! RageType is intentionally simple, and we'd like to keep it that way.

## How to Contribute

### Bug Reports
- Open an issue with steps to reproduce
- Include your OS, Python version, and error output
- Check existing issues first

### Sound Packs
Created a fun sound pack? We'd love to feature it!
- Open a PR or issue with a link to your sound pack
- Include a short description and demo video/audio if possible
- Sound packs should be 36 MP3 files (`a.mp3`–`z.mp3`, `0.mp3`–`9.mp3`)
- Keep file sizes reasonable (under 100KB per file is ideal)

### Code Changes
1. Fork the repo
2. Create a feature branch (`git checkout -b feature/my-idea`)
3. Make your changes
4. Test on your platform
5. Submit a PR with a clear description

### What We're Looking For
- Sound pack contributions
- Platform-specific fixes (especially Linux/Wayland)
- UI improvements to the dashboard
- Performance improvements
- Documentation improvements
- Translations for the landing page

### What We're NOT Looking For
- Features that require internet connectivity
- Telemetry or analytics of any kind
- Cryptocurrency / blockchain integration
- Complexity for complexity's sake

## Code Style
- Keep it simple — this is a fun project, not enterprise software
- Follow existing patterns in the codebase
- Comment non-obvious code
- Test on at least one platform before submitting

## Development Setup

```bash
git clone https://github.com/MateiCysec/ragetype.git
cd ragetype
python3 -m pip install -r requirements.txt
# Place test sounds in sounds/default/
python3 ragetype.py
```

## Code of Conduct

Be kind. Be respectful. Have fun. Don't be a jerk.

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/) code of conduct.