import psutil
import os
import signal
import subprocess
import sys

## Get a list of all the PIDs of a all the running process
## whose name contains the given string process name
def get_process_id_by_name(process_name: str) -> int:
    process_list: list[str] = []
    
    # Iterate over the all the running process
    for process in psutil.process_iter():
        try:
            process_info = process.as_dict(attrs=['pid', 'name', 'create_time'])

            # Check if process name contains the given name string.
            if process_name.lower() in process_info['name'].lower() :
                process_list.append(process_info)

        except (psutil.NoSuchProcess, psutil.AccessDenied , psutil.ZombieProcess): pass

    return process_list[0]["pid"]


## Kill a process tree (icnluding grandchildren) with signal
def kill_proc_tree(pid: int) -> None:
    sig=signal.SIGTERM
    include_parent=True,
    timeout=None
    on_terminate=None
    
    assert pid != os.getpid(), "won't kill myself"

    parent = psutil.Process(pid)
    children = parent.children(recursive=True)

    if include_parent:
        children.append(parent)
        
    for process in children:
        try:
            process.send_signal(sig)
        except psutil.NoSuchProcess: pass

        gone, alive = psutil.wait_procs(children, timeout=timeout, callback=on_terminate)

    return (gone, alive)

## Run application with path
def run_application(path: str) -> None:
    subprocess.Popen(path, shell=True)

if __name__ == "__main__":
    application_name: str = sys.argv[1]

    try:
        # Kill the origin process
        print(f"Kill the original {application_name} process")
        kill_proc_tree(get_process_id_by_name(application_name))
    except IndexError:
        print(f"{application_name} is not currently running !!!")
        sys.exit(1)
    
    # Create a new process
    print(f"Create the new {application_name} process")
    run_application(application_name)
