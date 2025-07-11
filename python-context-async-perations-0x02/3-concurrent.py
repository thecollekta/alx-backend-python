import asyncio
import aiosqlite


async def async_fetch_users():
    """An asynchronous coroutine to fetch all users."""
    print("Starting to fetch all users...")
    async with aiosqlite.connect("users.db") as db:
        cursor = await db.execute("SELECT * FROM users")
        results = await cursor.fetchall()
        print("...Finished fetching all users.")
        return results


async def async_fetch_older_users():
    """An asynchronous coroutine to fetch users over 40."""
    print("Starting to fetch older users...")
    async with aiosqlite.connect("users.db") as db:
        cursor = await db.execute("SELECT * FROM users WHERE age > ?", (40,))
        results = await cursor.fetchall()
        print("...Finished fetching older users.")
        return results


async def fetch_concurrently():
    """The main coroutine that orchestrates the concurrent tasks."""
    task1 = async_fetch_users()
    task2 = async_fetch_older_users()

    # Running them concurrently with asyncio.gather
    all_results = await asyncio.gather(task1, task2)
    print("\n--- Concurrent execution complete ---")
    print("Results from all users:", all_results[0])
    print("Results from older users:", all_results[1])


# The entry point that starts the entire async process
if __name__ == "__main__":
    asyncio.run(fetch_concurrently())
