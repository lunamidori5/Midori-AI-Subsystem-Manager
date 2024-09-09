## The goal of this rework is to remove the need for docker from all backends, things like AnythingLLM will not play nice with this
## But I am hopeing that we can get this worked out, only remove these comments if we have done this and this is live

import os
import asyncio
import subprocess

from nicegui import ui, app
from nicegui.events import ValueChangeEventArguments

temp_menu = False

async def update_system():
    ui.notify('Asynchronous task started')
    await asyncio.sleep(5)
    ui.notify('Asynchronous task finished')

async def subsystem_update():
    # Create a new subprocess to run the update command
    n = ui.notification(timeout=None)
    n.message = f'Starting Install... Please wait...'
    n.spinner = True
    await asyncio.sleep(5)

    tempcommand_str = "docker run -v /var/run/docker.sock:/var/run/docker.sock -it lunamidori5/pixelarch:subsystem /usr/bin/yay -Syu --noconfirm"
    command_str = "docker run -v /var/run/docker.sock:/var/run/docker.sock lunamidori5/pixelarch:subsystem \"/usr/bin/yay -Syu --noconfirm\""
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
        n.message = f"Output: {output}"
        command_outerr = stderr.decode('utf-8')

        # Check if the process has finished running
        if process.returncode is not None:
            break

    # Wait for the process to finish running
    await asyncio.sleep(5)

    n.message = 'Done!'
    n.spinner = False
    await asyncio.sleep(15)
    n.dismiss()

def on_button_click(sender):
    print(f"You clicked button {sender}!")

v = ui.checkbox('Boot Subsystem?', value=temp_menu)

dark = ui.dark_mode()
dark.enable()

with ui.row():
    ui.label('Switch mode:')
    ui.button('Dark', on_click=dark.enable)
    ui.button('Light', on_click=dark.disable)

with ui.row().bind_visibility_from(v, 'value'):
    with ui.column():
        ui.label("Subsystem Actions:")
        ui.button("1 - Midori AI Subsystem Repair", on_click=subsystem_update)
        ui.button("2 - Install Backends to Subsystem", on_click=on_button_click)
        ui.button("3 - Update Backends in Subsystem", on_click=on_button_click)
        ui.button("4 - Uninstall Backends from Subsystem", on_click=on_button_click)
        ui.button("5 - Backend Programs (install models / edit backends)", on_click=on_button_click)
        ui.button("6 - Subsystem and Backend News", on_click=on_button_click)

ui.run()