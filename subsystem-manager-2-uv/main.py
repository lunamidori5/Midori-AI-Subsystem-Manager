## The goal of this rework is to remove the need for docker from all backends, things like AnythingLLM will not play nice with this
## But I am hopeing that we can get this worked out, only remove these comments if we have done this and this is live

import os
import asyncio
import configparser

from halo import Halo

from nicegui import ui, app
from nicegui.events import ValueChangeEventArguments

temp_menu = False

image_download = "lunamidori5/midori_ai_subsystem"
image_name = "midori_ai_subsystem_pixelarch"

spinner = Halo(text='Loading', spinner='dots', color='green')

config = configparser.ConfigParser()
config.read('config.ini')

docker_command = config['docker']['command']
docker_sock = config['docker']['sock']

#docker_command = "docker"
#docker_sock = "/var/run/docker.sock"

docker_sock_command = f"-v {docker_sock}:/var/run/docker.sock"

docker_run_command = "run --restart always"

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
        self.image = image_name
        self.dockerexec = f"{self.command_base} exec {self.image}"
        self.dockerbuilder = f"{self.dockerexec}" 
        self.port = 30000
        self.use_gpu = False
    
    def check_type(self, command_in):
        if self.type == "Ephemeral":
            print("Not installing")
        elif self.type == 'Install':
            print("Installing")
        elif self.type == 'Purge':
            print("Purging")
    
    def change_port(self, port):
        try:
            self.port = int(port)
        except Exception as error:
            self.port = 30000
    
    def reset_image(self):
        self.image = image_name
        self.dockerexec = f"{self.command_base} exec {self.image}"
        self.dockerbuilder = f"{self.dockerexec}" 
    
    def change_image(self, new_image):
        self.image = new_image
        self.dockerexec = f"{self.command_base} exec {self.image}"
        self.dockerbuilder = f"{self.dockerexec}" 

manager = Manager_mode()

def handle_toggle_change(toggle):
    value = toggle.value
    if value == 'Update':
        manager.type = 'Update'
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
        print(command_str)
        spinner.start(text=f'Running: {command_str}')
        n.message = f'Running: {command_str}'
        command_list = command_str.split()

        process = await asyncio.create_subprocess_exec(
            *command_list,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        while True:
            stdout, stderr = await process.communicate()

            output = stdout.decode('utf-8')
            command_outerr = stderr.decode('utf-8')

            if process.returncode is not None:
                spinner.succeed(text=f"Output: {output}")
                print(output)
                await asyncio.sleep(2)
                break
            else:
                spinner.fail(text=f"Output: {output} : {command_outerr}")
                print(output)
                await asyncio.sleep(2)
                break

    await asyncio.sleep(5)

    n.message = 'Done!'
    n.spinner = False
    markdown_box.update()
    await asyncio.sleep(25)

    n.dismiss()

async def subsystem_repair():
    # Create a new subprocess to run the install command
    n = ui.notification(timeout=None)
    n.message = f'Starting Install... Please wait... Check command line for more info...'
    n.spinner = True
    spinner.start(text='Starting Install... Please wait...')

    full_image_name_command = f"--name {manager.image}"

    command_pre_list = [
        f"{manager.command_base} pull {image_download}",
        f"{manager.command_base} {docker_run_command} -d {docker_sock_command} {full_image_name_command} {image_download} sleep infinity",
        f"{manager.dockerexec} yay -Syu --noconfirm"
        ]
    
    await run_commands_async(n, command_pre_list)

async def subsystem_update():
    n = ui.notification(timeout=None)
    n.message = f'Starting Install... Please wait...'
    n.spinner = True

    manager.reset_image()

    command_pre_list = [
        f"{manager.dockerexec} yay -Syu --noconfirm",
        f"{manager.dockerexec} sudo midori-ai-updater"
        ]
    
    await run_commands_async(n, command_pre_list)

async def localai_install():
    n = ui.notification(timeout=None)
    n.message = f'Starting... Please wait...'
    manager.change_image("midori-ai-local-ai")
    run_command = ""
    n.spinner = True

    if manager.port == 30000:
        local_port_offset = 8080
    else:
        local_port_offset = 0
    
    port_to_use = manager.port + local_port_offset
    full_image_name_command = f"--name {manager.image}"

    print(manager.type)

    command_pre_list = []

    if manager.type == "Purge":
        run_command = f"{manager.command_base} stop {manager.image} && {manager.command_base} rm {manager.image}"
    
    else:
        if manager.use_gpu:
            run_command = f"{manager.command_base} {docker_run_command} -d --gpus all -p {port_to_use}:8080 {full_image_name_command} -ti localai/localai:latest-aio-gpu-nvidia-cuda-11"
        else:
            run_command = f"{manager.command_base} {docker_run_command} -d -p {port_to_use}:8080 {full_image_name_command} -ti localai/localai:latest-aio-cpu"
    
    command_pre_list.append(f"{run_command} ")
        
    await run_commands_async(n, command_pre_list)

    manager.reset_image()

async def bigagi_install():
    n = ui.notification(timeout=None)
    n.message = f'Starting... Please wait...'
    manager.change_image("midori-ai-big-agi")
    run_command = ""
    n.spinner = True

    if manager.port == 30000:
        local_port_offset = 3000
    else:
        local_port_offset = 0
    
    port_to_use = manager.port + local_port_offset
    full_image_name_command = f"--name {manager.image}"

    print(manager.type)

    command_pre_list = []

    if manager.type == "Purge":
        run_command = f"{manager.command_base} stop {manager.image} && {manager.command_base} rm {manager.image}"
    else:
        run_command = f"{manager.command_base} {docker_run_command} -d -p {port_to_use}:3000 {full_image_name_command} -ti ghcr.io/enricoros/big-agi"
    
    command_pre_list.append(f"{run_command} ")
        
    await run_commands_async(n, command_pre_list)

    manager.reset_image()

async def bigagi_two_install():
    n = ui.notification(timeout=None)
    n.message = f'Starting... Please wait...'
    runsh_path = os.path.join(".", "run.sh")
    manager.change_image("midori-ai-big-agi")
    n.spinner = True

    if manager.port == 30000:
        local_port_offset = 3000
    else:
        local_port_offset = 0
    
    image_download = "lunamidori5/pixelarch:amethyst"
    
    port_to_use = manager.port + local_port_offset
    full_image_name_command = f"--name {manager.image}"

    print(manager.type)

    starter_builder_command_list = [
        f"{manager.command_base} pull {image_download}",
        f"{manager.command_base} {docker_run_command} -d {docker_sock_command} -p {port_to_use}:3000 {full_image_name_command} {image_download} sleep infinity",
        f"{manager.dockerexec} yay -Syu --noconfirm nodejs nvm"
        ]
    
    command_pre_list = []
    builder_command_list = []

    if manager.type == "Purge":
        command_pre_list.append(f"{manager.command_base} stop {manager.image}")
        command_pre_list.append(f"{manager.command_base} rm {manager.image}")
    else:

        for command in starter_builder_command_list:
            command_pre_list.append(command)

        builder_command_list.append("git clone -b v2-dev https://github.com/enricoros/big-AGI.git")
        builder_command_list.append("cd big-AGI")
        builder_command_list.append("source /usr/share/nvm/init-nvm.sh")
        builder_command_list.append("nvm install 20.0 && nvm use 20.0")
        builder_command_list.append("npm ci")
        builder_command_list.append("npm run build")
        builder_command_list.append("next start --port 3000 &")

        with open(runsh_path, "w") as f:
            for line in builder_command_list:
                f.write(line)
                f.write("\n")
        
        command_pre_list.append(f"{manager.command_base} cp {runsh_path} {manager.image}:/home/midori-ai/run.sh")
        command_pre_list.append(f"{manager.dockerexec} chmod +x run.sh")
        command_pre_list.append(f"{manager.dockerexec} ls -lha")
        command_pre_list.append(f"{manager.dockerexec} bash ./run.sh")
        
    await run_commands_async(n, command_pre_list)

    os.remove(runsh_path)

    manager.reset_image()

async def anythingllm_install():
    n = ui.notification(timeout=None)
    n.message = f'Starting... Please wait...'
    runsh_path = os.path.join(".", "run.sh")
    manager.change_image("midori-ai-anythingllm")
    n.spinner = True

    if manager.port == 30000:
        local_port_offset = 3001
    else:
        local_port_offset = 0
    
    image_download = "lunamidori5/pixelarch:amethyst"
    
    port_to_use = manager.port + local_port_offset
    full_image_name_command = f"--name {manager.image}"

    print(manager.type)
    
    command_pre_list = []

    if manager.type == "Purge":
        command_pre_list.append(f"{manager.command_base} stop {manager.image}")
        command_pre_list.append(f"{manager.command_base} rm {manager.image}")
    else:
        command_pre_list.append(f"{manager.command_base} {docker_run_command} -d -p {port_to_use}:3001 {full_image_name_command} --cap-add SYS_ADMIN -v anythingllm:/app/server/storage -e STORAGE_DIR=\"/app/server/storage\" mintplexlabs/anythingllm")
        
    await run_commands_async(n, command_pre_list)

    manager.reset_image()

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
            ui.input(label='Port Number', placeholder='Edit to change port', on_change=lambda e: manager.change_port(e.value))
            with ui.column():
                ui.label("LocalAI:")
                ui.button("LocalAI", on_click=localai_install)

            with ui.column():
                ui.label("Big AGI:")
                ui.button("Big-AGI V1 (Stable)", on_click=bigagi_install)
                ui.button("Big-AGI V2 (Beta - MUST REINSTALL EACH REBOOT)", on_click=bigagi_two_install)

            with ui.column():
                ui.label("AnythingLLM:")
                ui.button("AnythingLLM", on_click=anythingllm_install)

        #ui.button("3 - Update Backends in Subsystem", on_click=on_button_click)
        #ui.button("4 - Uninstall Backends from Subsystem", on_click=on_button_click)
        #ui.button("5 - Backend Programs (install models / edit backends)", on_click=on_button_click)
        #ui.button("6 - Subsystem and Backend News", on_click=on_button_click)

ui.run()