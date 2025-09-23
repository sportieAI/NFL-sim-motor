import os
import json
import streamlit as st

# --- API integration for LLM (OpenAI example) ---
def generate_llm_commentary_openai(sim_output, openai_api_key):
    try:
        from openai import OpenAI
        client = OpenAI(api_key=openai_api_key)
        prompt = f"Give an exciting, human-like summary for this NFL simulation result:\n{json.dumps(sim_output)}"
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=250
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return f"Simulation summary unavailable (API Error). Result: {sim_output}"

# --- API integration for voice synthesis (Coqui TTS example) ---
def synthesize_voice_coqui(text, output_path, coqui_api_key, speaker_id="speaker_id"):
    try:
        import requests
        url = "https://api.coqui.ai/v1/tts"
        headers = {"Authorization": f"Bearer {coqui_api_key}"}
        payload = {
            "text": text,
            "speaker_id": speaker_id,
            "voice_id": "en-US"
        }
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            return output_path
        else:
            print(f"TTS failed with status {response.status_code}: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"TTS request failed (likely firewall/network issue): {e}")
        # Create a placeholder text file instead of audio
        placeholder_path = output_path.replace('.mp3', '.txt')
        with open(placeholder_path, 'w') as f:
            f.write(f"Voice synthesis unavailable. Text content: {text}")
        print(f"Created text placeholder: {placeholder_path}")
        return placeholder_path
    except Exception as e:
        print(f"TTS unexpected error: {e}")
        return None

# --- Streamlit dashboard ---
def run_dashboard(archive_root="outputs"):
    st.title("NFL Simulation Dashboard")
    sim_dirs = sorted([d for d in os.listdir(archive_root) if os.path.isdir(os.path.join(archive_root, d))], reverse=True)
    if not sim_dirs:
        st.warning("No simulation archives found.")
        return
    selected_sim = st.selectbox("Select Simulation", sim_dirs)
    archive_dir = os.path.join(archive_root, selected_sim)

    # Load outputs
    with open(os.path.join(archive_dir, "simulation_output.json")) as f:
        sim_output = json.load(f)
    with open(os.path.join(archive_dir, "analytics_report.json")) as f:
        analytics = json.load(f)
    with open(os.path.join(archive_dir, "summary.txt")) as f:
        commentary = f.read()
    audio_path = os.path.join(archive_dir, "narration.mp3")

    # Visualization
    st.subheader("Scoreboard")
    team_scores = {team["name"]: team["points"] for team in sim_output["teams"]}
    st.bar_chart(team_scores)

    st.subheader("Analytics")
    for k, v in analytics.items():
        st.write(f"**{k}:** {v}")

    st.subheader("Commentary")
    st.write(commentary)

    st.subheader("Audio Narration")
    if os.path.exists(audio_path):
        st.audio(audio_path)
    else:
        st.info("No audio narration found.")

    st.subheader("Raw Simulation Data")
    st.json(sim_output)

# Example usage for API integration
if __name__ == "__main__":
    # --- API integration example calls ---
    # openai_api_key = "<YOUR_OPENAI_KEY>"
    # coqui_api_key = "<YOUR_COQUI_KEY>"
    # sim_output = {...} # Your simulation result dictionary
    # commentary = generate_llm_commentary_openai(sim_output, openai_api_key)
    # synthesize_voice_coqui(commentary, "narration.mp3", coqui_api_key)
    
    # --- Dashboard ---
    run_dashboard()