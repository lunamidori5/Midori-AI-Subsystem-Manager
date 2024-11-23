## The goal of this rework is to remove the need for docker from all backends, things like AnythingLLM will not play nice with this
## But I am hopeing that we can get this worked out, only remove these comments if we have done this and this is live

import os
import asyncio

from halo import Halo

from nicegui import ui, app
from nicegui.events import ValueChangeEventArguments

temp_menu = False

image_download = "lunamidori5/midori_ai_subsystem"
image_name = "midori_ai_subsystem_pixelarch"

spinner = Halo(text='Loading', spinner='dots', color='green')

docker_command = "docker"

docker_sock = "/var/run/docker.sock"
docker_sock_command = f"-v {docker_sock}:/var/run/docker.sock"

def get_docker_json():
    temp_file = "docker_ps_output.md"
    format_info = str("""{{.Names}}: ID - {{.ID}} Command - {{.Command}} \\n""")
    
    os.system(f"{docker_command} ps -a --format \"{format_info}\" > {temp_file}")

    with open(temp_file, "r") as f:
        data = f.read()
        
    os.remove(temp_file)
    return data

class Manager_mode:
    def __init__(self):
        self.type = "unknown"
        self.command_base = docker_command
        self.port = 38080
        self.use_gpu = False
    
    def check_type(self, command_in):
        if self.type == "Ephemeral":
            print("Not installing")
        elif self.type == 'Install':
            print("Installing")
        elif self.type == 'Purge':
            print("Purging")
    
    def change_port(self, port):
        self.port = int(port)

manager = Manager_mode()

def handle_toggle_change(toggle):
    value = toggle.value
    if value == 'Ephemeral':
        manager.type = 'Ephemeral'
    elif value == 'Install':
        manager.type = 'Install'
    elif value == 'Purge':
        manager.type = 'Purge'
    else:
        print(f"Unknown Var: {str(value)}")

def handle_gput_toggle_change(toggle):
    value = toggle.value
    if value == 'Use GPU':
        manager.use_gpu = True
    elif value == 'No GPU':
        manager.use_gpu = False
    else:
        print(f"Unknown Var: {str(value)}")

async def run_commands_async(n, command_pre_list):
    for command_str in command_pre_list:
        spinner.start(text=f'Running: {command_str}')
        n.message = f'Running: {command_str}'
        command_list = command_str.split()

        process = await asyncio.create_subprocess_exec(
            *command_list,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        # Read the output of the process in real time
        while True:
            # Read the stdout and stderr of the process
            stdout, stderr = await process.communicate()

            # Print the output to the console
            output = stdout.decode('utf-8')
            command_outerr = stderr.decode('utf-8')

            # Check if the process has finished running
            if process.returncode is not None:
                spinner.succeed(text=f"Output: {output}")
                break

async def subsystem_repair():
    # Create a new subprocess to run the install command
    n = ui.notification(timeout=None)
    n.message = f'Starting Install... Please wait... Check command line for more info...'
    n.spinner = True
    spinner.start(text='Starting Install... Please wait...')

    full_image_name_command = f"--name {image_name}"

    command_pre_list = [
        f"{manager.command_base} pull {image_download}",
        f"{manager.command_base} run -d {docker_sock_command} {full_image_name_command} {image_download} sleep infinity",
        f"{manager.command_base} exec {image_name} /usr/bin/yay -Syu --noconfirm"
        ]
    
    await run_commands_async(n, command_pre_list)
    
    spinner.succeed(text="All Done!")

    n.dismiss()

async def subsystem_update():
    # Create a new subprocess to run the update command
    n = ui.notification(timeout=None)
    n.message = f'Starting Install... Please wait...'
    n.spinner = True

    command_pre_list = [
        f"{manager.command_base} exec {image_name} /usr/bin/yay -Syu --noconfirm",
        f"sudo midori-ai-updater"
        ]
    
    await run_commands_async(n, command_pre_list)

    # Wait for the process to finish running
    await asyncio.sleep(5)

    n.message = 'Done! Subsystem full installed and updated!'
    n.spinner = False
    markdown_box.update()
    await asyncio.sleep(25)

    n.dismiss()

async def localai_install():
    # Create a new subprocess to run the update command
    n = ui.notification(timeout=None)
    n.message = f'Starting Install... Please wait...'
    run_command = ""
    local_image_download = ""
    n.spinner = True

    print(manager.type)

    command_pre_list = []

    if manager.type == "Purge":
        run_command = f"{manager.command_base} stop midori-ai-local-ai && {manager.command_base} rm midori-ai-local-ai"
    
    else:
        if manager.use_gpu:
            run_command = f"{manager.command_base} run --gpus all -p {manager.port}:8080 --name midori-ai-local-ai -ti localai/localai:latest-aio-gpu-nvidia-cuda-11"
        else:
            run_command = f"{manager.command_base} run -p {manager.port}:8080 --name midori-ai-local-ai -ti localai/localai:latest-aio-cpu"
    
    command_pre_list.append(f"{run_command} ")
        
    await run_commands_async(n, command_pre_list)

    # Wait for the process to finish running
    await asyncio.sleep(5)

    n.message = 'Done! LocalAI full installed and updated!'
    n.spinner = False
    markdown_box.update()
    await asyncio.sleep(25)

    n.dismiss()

ui.separator()

dark = ui.dark_mode(True)

with ui.row():
    ui.label('Switch mode:')
    ui.button('Dark', on_click=dark.enable)
    ui.button('Light', on_click=dark.disable)

ui.separator()

with ui.row():
    ui.label("Manager Mode:")
    toggle = ui.toggle(['Install', 'Purge'])
    toggle_gpu = ui.toggle(['Use GPU', 'No GPU'], value='No GPU')
    toggle.on_value_change(handle_toggle_change) 
    toggle_gpu.on_value_change(handle_gput_toggle_change) 

ui.separator()

with ui.row():
    markdown_box = ui.code(str(get_docker_json()))
    ui.update(markdown_box)
    with ui.column():
        with ui.row():
            ui.label("Subsystem Actions:")
        with ui.row():
            ui.button("Subsystem Install", on_click=subsystem_repair)
            ui.button("Subsystem Repair", on_click=subsystem_repair)
            ui.button("Subsystem Update", on_click=subsystem_update)
        with ui.row():
            ui.label("Install Backends:")
        with ui.row():
            ui.input(label='Port Number', placeholder='start typing', on_change=lambda e: manager.change_port(e.value))
            ui.button("LocalAI", on_click=localai_install)
            ui.button("Big-AGI", on_click=subsystem_repair)
        #ui.button("3 - Update Backends in Subsystem", on_click=on_button_click)
        #ui.button("4 - Uninstall Backends from Subsystem", on_click=on_button_click)
        #ui.button("5 - Backend Programs (install models / edit backends)", on_click=on_button_click)
        #ui.button("6 - Subsystem and Backend News", on_click=on_button_click)

ui.run()