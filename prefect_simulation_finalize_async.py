import asyncio
from typing import List, Dict, Any
from prefect import flow, task, get_run_logger


# --- Replace these with your actual implementations --- #
async def terminate_simulation_api(sim_id: str):
    # Example: await external_api.terminate_simulation(sim_id)
    await asyncio.sleep(0.1)
    print(f"Simulation {sim_id} terminated.")


async def persist_final_state(sim_id: str):
    await asyncio.sleep(0.1)
    print(f"Final state for {sim_id} persisted.")


async def fetch_final_events(sim_id: str) -> List[Dict]:
    await asyncio.sleep(0.1)
    # Example: return await db.fetch_events(sim_id)
    return [
        {"event_id": 1, "type": "score", "details": "TD"},
        {"event_id": 2, "type": "penalty", "details": "Offside"},
    ]


async def enrich_event(event: Dict) -> Dict:
    # Example enrichment
    event["enriched"] = True
    event["tags"] = ["high_impact"] if event["type"] == "score" else []
    return event


async def persist_memory(event: Dict, tenant_id: str):
    await asyncio.sleep(0.05)
    print(f"Persisted memory: {event['event_id']} for tenant: {tenant_id}")


async def batch_persist_memories(events: List[Dict], tenant_id: str):
    # Example batch write
    await asyncio.sleep(0.1)
    print(f"Batch persisted {len(events)} memories for {tenant_id}")


async def load_memories(sim_id: str) -> List[Dict]:
    await asyncio.sleep(0.1)
    return [
        {"event_id": 1, "summary": "TD by Player 7"},
        {"event_id": 2, "summary": "Offside"},
    ]


async def build_narrative_prompt(memories: List[Dict]) -> str:
    return "Summarize the following events: " + "; ".join(
        [m["summary"] for m in memories]
    )


async def generate_narrative(prompt: str) -> str:
    await asyncio.sleep(0.1)
    return f"Narrative: {prompt}"


async def persist_narrative(sim_id: str, narrative: str):
    await asyncio.sleep(0.05)
    print(f"Narrative for {sim_id} persisted.")


async def compute_simulation_stats(sim_id: str) -> Dict[str, Any]:
    await asyncio.sleep(0.1)
    return {"sim_id": sim_id, "possessions": 12, "scores": 3}


async def save_to_dashboard_db(stats: Dict[str, Any]):
    await asyncio.sleep(0.05)
    print(f"Stats saved to dashboard: {stats}")


async def archive_simulation(sim_id: str, include: List[str]):
    await asyncio.sleep(0.2)
    print(f"Simulation {sim_id} archived with: {include}")


async def notify_dashboard(sim_id: str):
    await asyncio.sleep(0.05)
    print(f"Dashboard notified for {sim_id}")


async def trigger_model_training(sim_id: str):
    await asyncio.sleep(0.05)
    print(f"Model training triggered for {sim_id}")


async def send_webhook(event_type: str, sim_id: str):
    await asyncio.sleep(0.05)
    print(f"Webhook sent: {event_type} for {sim_id}")


# ------------------------------------------------------ #


@task(
    name="Terminate Simulation", retries=2, retry_delay_seconds=3, persist_result=False
)
async def terminate_simulation(sim_id: str):
    await terminate_simulation_api(sim_id)
    await persist_final_state(sim_id)


@task(
    name="Persist Final Events and Memories",
    retries=2,
    retry_delay_seconds=3,
    persist_result=False,
)
async def persist_events_and_memories(sim_id: str, tenant_id: str) -> List[Dict]:
    final_events = await fetch_final_events(sim_id)
    enriched_events = [await enrich_event(e) for e in final_events]
    await batch_persist_memories(enriched_events, tenant_id)
    return enriched_events


@task(name="Generate Narrative", persist_result=False)
async def generate_and_persist_narrative(sim_id: str):
    memories = await load_memories(sim_id)
    prompt = await build_narrative_prompt(memories)
    narrative = await generate_narrative(prompt)
    await persist_narrative(sim_id, narrative)
    return narrative


@task(name="Collect Analytics and Metrics", persist_result=False)
async def collect_analytics_and_metrics(sim_id: str):
    stats = await compute_simulation_stats(sim_id)
    await save_to_dashboard_db(stats)
    return stats


@task(name="Archive Results", persist_result=False)
async def archive_results(sim_id: str, include: List[str]):
    await archive_simulation(sim_id, include)


@task(name="Post-Simulation Hooks", persist_result=False)
async def post_simulation_hooks(sim_id: str):
    await notify_dashboard(sim_id)
    await trigger_model_training(sim_id)
    await send_webhook("simulation_complete", sim_id)


@flow(name="Async Finalize Simulation Pipeline")
async def finalize_simulation_pipeline(sim_id: str, tenant_id: str):
    logger = get_run_logger()
    await terminate_simulation.submit(sim_id)
    enriched_events = await persist_events_and_memories.submit(sim_id, tenant_id)
    narrative = await generate_and_persist_narrative.submit(sim_id)
    stats = await collect_analytics_and_metrics.submit(sim_id)
    await archive_results.submit(sim_id, include=["memories", "narrative", "stats"])
    await post_simulation_hooks.submit(sim_id)
    logger.info(f"Simulation finalization complete for {sim_id}")


if __name__ == "__main__":
    import asyncio

    sim_id = "SIM123"
    tenant_id = "tenant_abc"
    asyncio.run(finalize_simulation_pipeline(sim_id, tenant_id))
