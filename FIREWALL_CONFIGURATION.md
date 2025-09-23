# Firewall Configuration Guide

## Overview

The NFL Simulation Engine has been designed to work both with and without external API access. This guide explains how to configure your environment to handle firewall restrictions and provides setup instructions for both online and offline modes.

## External Dependencies and Firewall Requirements

### APIs and External Services

The simulation engine may attempt to connect to the following external services:

1. **OpenAI API** (`api.openai.com`)
   - Used for: LLM-based game commentary generation
   - Ports: 443 (HTTPS)
   - Fallback: Returns template-based commentary when unavailable

2. **Coqui TTS API** (`api.coqui.ai`)
   - Used for: Voice synthesis of game commentary
   - Ports: 443 (HTTPS)  
   - Fallback: Creates text files instead of audio when unavailable

3. **Sportradar API** (`api.sportradar.com`)
   - Used for: Real NFL team and player statistics
   - Ports: 443 (HTTPS)
   - Fallback: Uses built-in mock data when unavailable

4. **SportsData.io API** (`api.sportsdata.io`)
   - Used for: Additional player statistics
   - Ports: 443 (HTTPS)
   - Fallback: Uses built-in mock data when unavailable

### GitHub Actions Dependencies

The GitHub Actions workflows may attempt to download:

1. **Spotless JAR** (`github.com/diffplug/spotless/releases/`)
   - Used for: Java code formatting
   - Alternative: Use Maven/Gradle plugins instead

## Firewall Allow List Configuration

### Option 1: Allow Required Domains

Add these domains to your firewall allow list:

```
api.openai.com
api.coqui.ai
api.sportradar.com
api.sportsdata.io
github.com
raw.githubusercontent.com
pypi.org
files.pythonhosted.org
```

### Option 2: Use Offline Mode (Recommended)

Set the environment variable to enable offline mode:

```bash
export OFFLINE_MODE=true
```

This will:
- Skip all external API calls
- Use built-in mock data for simulations
- Provide text fallbacks for voice synthesis
- Enable full simulation functionality without network access

## Environment Setup

### For Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sportieAI/NFL-sim-motor.git
   cd NFL-sim-motor
   ```

2. **Set up Python environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   # For offline mode (recommended for firewall-restricted environments)
   export OFFLINE_MODE=true
   
   # Optional: Set API keys if you have access
   export OPENAI_API_KEY="your_openai_key"
   export COQUI_API_KEY="your_coqui_key"
   export SPORTRADAR_API_KEY="your_sportradar_key"
   export FASTR_API_KEY="your_fastr_key"
   ```

5. **Run the simulation:**
   ```bash
   python main.py
   ```

6. **Launch the dashboard:**
   ```bash
   python dashboard_and_api.py
   # or
   streamlit run dashboard_and_api.py
   ```

### For GitHub Actions

If using GitHub Actions in a firewall-restricted environment:

1. **Configure the repository secrets with your firewall requirements**

2. **Use the provided workflows** - they have been updated to work without external downloads

3. **Enable Actions setup steps** by adding to your workflow:
   ```yaml
   steps:
     - name: Setup dependencies offline
       run: |
         # Pre-install all dependencies that would normally be downloaded
         pip install --upgrade pip
         pip install -r requirements.txt
   ```

## Error Handling and Fallbacks

The system includes comprehensive fallback mechanisms:

### API Fallbacks
- **OpenAI API failure**: Returns descriptive text summaries
- **Coqui TTS failure**: Creates `.txt` files with commentary text
- **Sports data APIs failure**: Uses realistic mock team/player data

### File Fallbacks
- **Missing historical data**: Uses generated mock matchup data
- **Missing output directories**: Creates them automatically
- **Missing configuration files**: Uses sensible defaults

### Error Messages
All error messages include:
- Clear description of what failed
- Information about which fallback was used
- Guidance for resolving the issue if desired

## Testing Offline Mode

To verify your setup works in offline mode:

```bash
# Set offline mode
export OFFLINE_MODE=true

# Test main simulation
python main.py

# Test API functions
python -c "
from dashboard_and_api import generate_llm_commentary_openai, synthesize_voice_coqui
print('Testing OpenAI fallback...')
result = generate_llm_commentary_openai({'test': 'data'}, 'fake_key')
print(f'Result: {result}')

print('Testing Coqui fallback...')
result = synthesize_voice_coqui('Test narration', '/tmp/test.mp3', 'fake_key')
print(f'Result: {result}')
"
```

## Performance Considerations

### Offline Mode Benefits
- **Faster startup**: No network timeouts
- **Consistent performance**: Not dependent on external API response times
- **Reliable testing**: Reproducible results with mock data
- **Lower costs**: No API usage charges

### Online Mode Benefits
- **Real data**: Current NFL statistics and information
- **Enhanced commentary**: AI-generated narrative content
- **Voice synthesis**: Audio output for commentary

## Troubleshooting

### Common Issues

1. **"Connection timeout" errors**
   - **Solution**: Enable offline mode or configure firewall allow list

2. **"Module not found" errors**
   - **Solution**: Ensure all dependencies are installed: `pip install -r requirements.txt`

3. **"Permission denied" errors**
   - **Solution**: Check file permissions and directory access

4. **"API key invalid" errors**
   - **Solution**: Use offline mode or verify API key configuration

### Debug Mode

Enable debug logging:
```bash
export DEBUG=true
python main.py
```

This will provide detailed information about:
- Which APIs are being attempted
- Fallback mechanisms being used
- Mock data being loaded
- Error details and stack traces

## Security Notes

- **API Keys**: Never commit API keys to version control
- **Environment Variables**: Use `.env` files for local development
- **Network Security**: The system works fully offline for security-sensitive environments
- **Data Privacy**: Mock data ensures no real player/team data is required

## Support

For additional help with firewall configuration:

1. Check the repository issues for similar problems
2. Review the error messages carefully - they include specific guidance
3. Test in offline mode first to isolate network vs. code issues
4. Refer to the `ONBOARDING.md` for general setup guidance