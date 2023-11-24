import concurrent.futures
import time
import streamlit as st

def run_task(cnt, container):
    print("Task", cnt, "Started")
    time.sleep(5)
    print("Task", cnt, "End")
    container.success(f"Task {cnt} Done")

def main():
    button = st.button("Run Tasks")
    if button:
        with concurrent.futures.ProcessPoolExecutor() as executor:
            cnts = list(range(5))
            containers = [st.empty() for i in range(5)]
            executor.map(run_task, cnts, containers)

if __name__ == "__main__":
    main()