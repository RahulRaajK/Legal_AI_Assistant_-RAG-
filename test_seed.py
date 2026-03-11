import asyncio
from backend.database import async_session
from backend.data.seed_mock_data import seed_mock_domain_data
import traceback

async def main():
    try:
        async with async_session() as db:
            await seed_mock_domain_data(db)
    except Exception as e:
        with open("error_trace.txt", "w") as f:
            f.write(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(main())
