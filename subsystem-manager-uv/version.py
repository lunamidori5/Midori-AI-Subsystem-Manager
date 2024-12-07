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
    print(Fore.LIGHTRED_EX + "Midori AI")
    print(Fore.RED + 'Due to our ongoing development efforts towards V2' + Fore.WHITE)
    print(Fore.RED + 'this ver of the subsystem manager will be deprecated as of 1/1/25' + Fore.WHITE)
    print(Fore.WHITE + 'Thank you for using v1 of the subsystem manager!' + Fore.WHITE)
    print(Fore.WHITE + 'V2 with its new GUI and easyer to use system and no docker import is coming soon!' + Fore.WHITE)
    print(blank_line)
    input("Press enter to go to main menu: ")