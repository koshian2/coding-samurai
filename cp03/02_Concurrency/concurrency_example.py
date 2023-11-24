import asyncio
import streamlit as st
import random

async def run_task(cnt, container):
    print("Task", cnt, "Started")
    await asyncio.sleep(random.randint(50, 80) / 10)
    print("Task", cnt, "End")
    container.success(f"Task {cnt} Done")

async def task_factory():
    tasks = []
    for i in range(5):
        task = asyncio.create_task(run_task(i, st.empty()))
        tasks.append(task)
    await asyncio.gather(*tasks)

def main():
    button = st.button("Run Tasks")
    if button:
        asyncio.run(task_factory())

if __name__ == "__main__":
    main()