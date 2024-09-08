import os

cwd = os.getcwd()

VERSION = "development"

for root, directories, files in os.walk(cwd):
    for file in files:
        if file == "midori_program_ver.txt":
            with open(os.path.join(root, file), 'r') as f:
                VERSION = f.read()

if VERSION == "development":
    print("No version file found. Using development version.")

def news(blank_line, Fore):
    print(blank_line)
    print(Fore.GREEN + "News" + Fore.WHITE)
    print(blank_line)
    print(Fore.LIGHTRED_EX + "Midori AI - As of Ver ->| 24.9.8.0 |<-")
    print(Fore.GREEN + 'We have started moving from ubuntu based docker images to' + Fore.WHITE)
    print(Fore.GREEN + 'PixelArch containerd images, thank you for the waiting!' + Fore.WHITE)
    print(blank_line)
    print(Fore.RED + "Dev Notes" + Fore.WHITE)
    print('Please report bugs to the github or email so we can fix them!')
    print('Thank you all so much for helping with the beta! <3')
    print(blank_line)
    input("Press enter to go to main menu: ")