# LLM Narrative Integration Blueprint

This document outlines a production-ready architecture for integrating LLM-powered narrative generation into the NFL simulation engine, along with optional TTS/voiceover extensions.

---

## 1. **Narrative Trigger Points**

Define key moments to generate narrative:
- After each play or batch of events
- At simulation milestones (touchdowns, turnovers, halftime, game end)
- On-demand (API/dashboard)

**Example:**
```python
def should_trigger_narrative(event):
    return any(tag in event.get("tags", []) for tag in ["critical", "turning_point", "heroic"])
```

---

## 2. **Memory Summarization Pipeline**

Aggregate enriched memories for prompt construction:
```python
def build_prompt(memories):
    context = "\n".join([f"{m['timestamp']}: {m['actor']} {m['action']} ({','.join(m['tags'])})" for m in memories])
    return (
        "You are a sports commentator AI. Summarize the following NFL simulation events into a dramatic narrative:\n"
        f"{context}"
    )
```

---

## 3. **LLM Invocation Layer**

Invoke OpenAI, Azure OpenAI, or local LLMs for narrative generation:
```python
def generate_narrative(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]
```

---

## 4. **Narrative Storage & Retrieval**

Store and retrieve generated narratives:
```python
def persist_narrative(sim_id, narrative_text, db):
    db.narratives.insert_one({
        "sim_id": sim_id,
        "text": narrative_text,
        "timestamp": datetime.utcnow()
    })
```

---

## 5. **Highlight & Emotional Scoring (Optional)**

Leverage LLMs for highlight/emotional impact scoring:
```python
def score_event(event):
    prompt = f"Rate the emotional impact of this event (1-10): {event}"
    score = call_llm(prompt)
    return int(score)
```

---

## 6. **API Endpoint**

Expose narrative generation through REST:
```
POST /api/v1/simulations/{sim_id}/narrative/generate
Body: { "mode": "highlight", "timeframe": "last_5_plays" }
```
Route handler should:
- Collect relevant memories
- Build prompt and generate narrative
- Persist and return the result

---

## 7. **TTS/Voiceover Pipeline (Optional)**

### **Overview**
Convert generated narratives into audio using TTS providers (e.g., ElevenLabs, Azure Speech).

**Example Workflow:**
```python
def generate_voiceover(narrative_text, tts_client):
    audio = tts_client.synthesize_speech(
        text=narrative_text,
        voice="en-US-sport-announcer",
        output_format="mp3"
    )
    return audio  # Save or stream to dashboard/UI
```

**Suggested Providers:**
- [ElevenLabs TTS](https://elevenlabs.io/)
- [Azure Speech Service](https://azure.microsoft.com/en-us/products/ai-services/text-to-speech)

**Enhancements:**
- Generate multi-perspective narratives (coach, player, analyst)
- Use fine-tuned LLMs for sport-specific tone and style
- Real-time streaming of both text and voiceover to dashboard

---

## 8. **Summary Table**

| Step                  | Module/Function                | Description                                 |
|-----------------------|-------------------------------|---------------------------------------------|
| Trigger Points        | `should_trigger_narrative`     | When to generate narrative                  |
| Summarization         | `build_prompt`                 | Aggregate memories for LLM prompt           |
| LLM Invocation        | `generate_narrative`           | Generate narrative with GPT/OpenAI etc.     |
| Storage               | `persist_narrative`            | Store generated narratives                  |
| Scoring (optional)    | `score_event`                  | Highlight or emotional scoring              |
| API                   | `/narrative/generate` endpoint | On-demand or scheduled narrative generation |
| TTS/Voiceover         | `generate_voiceover`           | Convert narrative to audio                  |

---

**For code scaffolds, see `engine/llm_narrative.py` or request additional endpoints or TTS integration samples.