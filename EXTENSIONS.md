# Extensions – Voice, LLM, Dashboard, Emotional Feedback

## Voice/Narration Modules

- Integrate OpenAI or Coqui TTS for dynamic audio.
- Add your own voice packs in `/voice_modules/`.

## Analytics & Emotional Feedback

- Drop-in analytics layers for custom KPIs.
- Use `/analytics/` to add new metrics or sentiment analysis.

## Dashboard Widgets

- Extend the Streamlit dashboard with new visualizations.
- Add files to `/dashboard_widgets/` and import in `dashboard_and_api.py`.

## How to Add a New Extension

1. Clone or create your module in the relevant directory.
2. Register the module in your simulation config.
3. Test by running a simulation and verifying the new feature.
