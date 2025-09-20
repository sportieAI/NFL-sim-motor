# SportieAI NFL Simulation Motor – Onboarding

Welcome! This is your entrypoint to simulating, narrating, and evolving the future of sports intelligence.

## Overview & Philosophy

SportieAI brings together simulation, analytics, and advanced voice/LLM agents for next-generation sports storytelling and research. Our system is modular, extensible, and built for both rapid prototyping and production deployment.

- **Simulate**: Recreate NFL games, seasons, or hypothetical matchups.
- **Narrate**: Generate dynamic, emotional commentary with LLM and voice.
- **Evolve**: Extend with your own agents, analytics, and integrations.

## Quickstart Setup

1. **Clone the repo**  
   ```bash
   git clone https://github.com/sportieAI/NFL-sim-motor.git
   cd NFL-sim-motor
   ```
2. **Run the setup script**  
   ```bash
   bash get_started.sh
   ```
3. **(Optional) Set API keys**  
   - For voice/LLM, set your `OPENAI_API_KEY` and/or `COQUI_API_KEY` in your environment.
4. **Launch the dashboard**  
   ```bash
   python dashboard_and_api.py
   ```
   The Streamlit dashboard will open in your browser.

_See [SIMULATION_GUIDE.md](./SIMULATION_GUIDE.md) for details on running custom simulations._

## Simulation Modes

- **Historical Replay**: Re-simulate past NFL seasons or games.
- **Agent-Based Simulation**: Deploy custom agents for strategy benchmarking.
- **Live Firehose**: Ingest and simulate in near-real-time.

## Extending with Agents, Analytics, Voice

- **Agents**: Add agent scripts to `/agents`.
- **Analytics**: Integrate custom analytics in `/analytics`.
- **Voice/LLM**: Plug in OpenAI, Coqui, or your own TTS for commentary and narration.

## Links to Other Guides

- [Fly Dashboard Setup](./FLY_DASHBOARD.md)
- [SaaS/Infra Deployment](./SAAS_DEPLOYMENT.md)
- [Investor Demo Outline](./INVESTOR_DEMO.md)
- [Simulation Guide](./SIMULATION_GUIDE.md)
- [Extensions](./EXTENSIONS.md)
- [Security](./SECURITY.md)
- [API Reference](./API_REFERENCE.md)