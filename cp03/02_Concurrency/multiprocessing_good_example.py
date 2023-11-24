import concurrent.futures
import time
import streamlit as st

def run_task(cnt):
    print("Task", cnt, "Started")
    time.sleep(5) # heavy process
    print("Task", cnt, "End")
    return f"Task {cnt} Done" # dummy result

def main():
    button = st.button("Run Tasks")
    if button:
        with concurrent.futures.ProcessPoolExecutor() as executor:
            cnts = list(range(5))
            results = executor.map(run_task, cnts)

            for result in results:
                st.success(result)

if __name__ == "__main__":
    main()