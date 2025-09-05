import asyncio
from typing import List, Dict, Any
from prefect import flow, task, get_run_logger
from prefect.tasks import task_input_hash
from datetime import timedelta

# =============== Example External Integrations =============== #
# Install dependencies:
# pip install aiobotocore motor redis asyncio

import aiobotocore
import motor.motor_asyncio
import redis.asyncio as aioredis

# ----------- S3/MinIO Async Client Example ----------- #
async def upload_to_s3(bucket: str, key: str, data: bytes, endpoint_url=None):
    session = aiobotocore.get_session()
    async with session.create_client(
        "s3",
        endpoint_url=endpoint_url,
        region_name="us-east-1",
        aws_secret_access_key="minioadmin",
        aws_access_key_id="minioadmin",
    ) as client:
        await client.put_object(Bucket=bucket, Key=key, Body=data)

# ----------- MongoDB Async Client Example ----------- #
async def insert_to_mongo(document: dict, db_url="mongodb://localhost:27017", db_name="sim", collection="events"):
    client = motor.motor_asyncio.AsyncIOMotorClient(db_url)
    db = client[db_name]
    return await db[collection].insert_one(document)

# ----------- Redis Async Client Example ----------- #
async def cache_in_redis(key: str, value: str, redis_url="redis://localhost:6379/0"):
    redis = aioredis.from_url(redis_url)
    await redis.set(key, value)

# ================== Prefect Tasks ================== #

@task(name="Terminate Simulation", retries=2, retry_delay_seconds=3)
async def terminate_simulation(sim_id: str):
    logger = get_run_logger()
    try:
        # Imagine calling your API here
        logger.info(f"Terminating simulation {sim_id}")
        await asyncio.sleep(0.05)
        logger.info(f"Simulation {sim_id} terminated.")
    except Exception as e:
        logger.error(f"Failed to terminate simulation: {e}")
        raise

@task(name="Persist Final Events and Memories", retries=2, retry_delay_seconds=3, cache_key_fn=task_input_hash, cache_expiration=timedelta(minutes=5))
async def persist_events_and_memories(sim_id: str, tenant_id: str) -> List[Dict]:
    logger = get_run_logger()
    try:
        # Example: Fetch final events from MongoDB
        events = [
            {"event_id": 1, "type": "score", "details": "TD"},
            {"event_id": 2, "type": "penalty", "details": "Offside"},
        ]
        enriched = []
        for event in events:
            # Enrich and persist to MongoDB
            event["enriched"] = True
            await insert_to_mongo(event)
            enriched.append(event)
        logger.info(f"{len(enriched)} events enriched and persisted to MongoDB.")
        return enriched
    except Exception as e:
        logger.error(f"Enrichment/persistence failed: {e}")
        raise

@task(name="Archive Results", retries=2)
async def archive_results(sim_id: str, include: List[str]):
    logger = get_run_logger()
    try:
        archive_content = f"Archive for {sim_id} includes: {include}".encode()
        await upload_to_s3(
            bucket="simulation-archives",
            key=f"{sim_id}/archive.txt",
            data=archive_content,
            endpoint_url="http://localhost:9000"  # MinIO example
        )
        logger.info(f"Archive for simulation {sim_id} uploaded to S3/MinIO.")
    except Exception as e:
        logger.error(f"Archiving failed: {e}")
        raise

@task(name="Generate Narrative", retries=2)
async def generate_and_persist_narrative(sim_id: str):
    logger = get_run_logger()
    try:
        # Simulate narrative generation
        narrative = f"Narrative for simulation {sim_id}"
        # Cache narrative in Redis for quick dashboard retrieval
        await cache_in_redis(f"narrative:{sim_id}", narrative)
        logger.info(f"Narrative for {sim_id} cached in Redis.")
        return narrative
    except Exception as e:
        logger.error(f"Narrative generation/storage failed: {e}")
        raise

@task(name="Collect Analytics and Metrics", retries=2)
async def collect_analytics_and_metrics(sim_id: str):
    logger = get_run_logger()
    try:
        stats = {"sim_id": sim_id, "possessions": 12, "scores": 3}
        # Imagine persisting to MongoDB or another analytics backend
        await insert_to_mongo(stats, collection="analytics")
        logger.info(f"Analytics for {sim_id} stored in MongoDB.")
        return stats
    except Exception as e:
        logger.error(f"Analytics failed: {e}")
        raise

@task(name="Post-Simulation Hooks", retries=2)
async def post_simulation_hooks(sim_id: str):
    logger = get_run_logger()
    try:
        # Example: send webhook or trigger model training
        logger.info(f"Post-simulation hooks for {sim_id} executed.")
    except Exception as e:
        logger.error(f"Post-simulation hooks failed: {e}")
        raise

@flow(name="Async Finalize Simulation Pipeline")
async def finalize_simulation_pipeline(sim_id: str, tenant_id: str):
    logger = get_run_logger()
    await terminate_simulation(sim_id)
    enriched_events = await persist_events_and_memories(sim_id, tenant_id)
    narrative = await generate_and_persist_narrative(sim_id)
    stats = await collect_analytics_and_metrics(sim_id)
    await archive_results(sim_id, include=["memories", "narrative", "stats"])
    await post_simulation_hooks(sim_id)
    logger.info(f"Simulation finalization complete for {sim_id}")

if __name__ == "__main__":
    import asyncio
    sim_id = "SIM123"
    tenant_id = "tenant_abc"
    asyncio.run(finalize_simulation_pipeline(sim_id, tenant_id))