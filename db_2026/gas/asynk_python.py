import asyncio
from asyncio import run, create_task

from loguru import logger


async def ai_job(prompt: str):
    logger.info(f"Running AI job with prompt: {prompt}")
    await asyncio.sleep(1)
    logger.info(f"AI job completed for prompt: {prompt}")


async def main():
    logger.info("Hello, world!")
    # await ai_job("prompt1")
    # await ai_job("prompt2")
    # await ai_job("prompt3")

    prompts = [f'prompt{i}' for i in range(1, 4)]
    tasks = [create_task(ai_job(p)) for p in prompts]
    logger.info("Waiting for all tasks to complete...")
    await asyncio.gather(*tasks)
    logger.info("All tasks completed.")

if __name__ == '__main__':
    run(main())
