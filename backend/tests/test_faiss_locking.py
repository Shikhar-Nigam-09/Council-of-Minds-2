import asyncio
import uuid

from app.services.rag.faiss_lock_registry import get_lock


def test_lock_registry_identity():
    """Test that get_lock returns the identical lock instance for the same user ID."""
    user_id_1 = uuid.uuid4()
    user_id_2 = uuid.uuid4()

    lock1a = get_lock(user_id_1)
    lock1b = get_lock(str(user_id_1))
    lock2 = get_lock(user_id_2)

    assert lock1a is lock1b
    assert lock1a is not lock2


def test_concurrent_lock_serialization():
    """Test that concurrent tasks for the same user are serialized cleanly without race conditions."""
    user_id = uuid.uuid4()
    lock = get_lock(user_id)
    execution_order = []

    async def worker(name, delay):
        async with lock:
            execution_order.append(f"start_{name}")
            await asyncio.sleep(delay)
            execution_order.append(f"end_{name}")

    async def run_workers():
        await asyncio.gather(worker("A", 0.05), worker("B", 0.01))

    asyncio.run(run_workers())

    assert execution_order == [
        "start_A",
        "end_A",
        "start_B",
        "end_B",
    ] or execution_order == ["start_B", "end_B", "start_A", "end_A"]
