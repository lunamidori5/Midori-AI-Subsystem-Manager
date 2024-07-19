import os
import json
import requests

import support as s

from colorama import Fore

class backend_programs_manager:
    def __init__(self, ver_os_info, client, about_model_size, about_model_q_size, client_openai):
        self.client = client
        self.ver_os_info = ver_os_info
        self.client_openai = client_openai
        self.about_model_size = about_model_size
        self.about_model_q_size = about_model_q_size
    
    def main_menu(self):
        ### LocalAI (10s)
        ### Ollma (40s)
        ### Invoke AI (30s)
        ### On Subsystem Programs
            ### Axlot (60s)
            ### Auto111
            ### Llama.cpp? (command line maybe?)
        backend_checker = s.backends_checking()
        installed_backends = backend_checker.check_json()

        menu_list_opt = []
        valid_answers = []

        localai_list = ["10", "11", "12", "13"]
        windows_list = ["20", "21", "22"]
        invokeai_list = ["30", "31", "32"]
        ollama_list = ["40", "41"]

        memgpt_list = ["50", "51"]

        if self.ver_os_info == "windows":
            menu_list_opt.append("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            menu_list_opt.append("ONLY USE IF YOU HAVE YOUR WSL BACKED UP")
            menu_list_opt.append("``20`` - WSL (Backup Docker Data)")
            menu_list_opt.append("``21`` - WSL (Move Docker Data)")
            menu_list_opt.append("``22`` - WSL (Purge Docker Data)")
            menu_list_opt.append("ONLY USE IF YOU HAVE YOUR WSL BACKED UP")
            for item in windows_list:
                valid_answers.append(item)
        
        if "localai" in installed_backends:
            menu_list_opt.append("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            menu_list_opt.append("``10`` - LocalAI (Install Models)")
            menu_list_opt.append("``11`` - LocalAI (Edit Models)")
            menu_list_opt.append("``12`` - LocalAI (Remove Models)")
            menu_list_opt.append("``13`` - LocalAI (Backup Models)")
            for item in localai_list:
                valid_answers.append(item)
        
        if "invokeai" in installed_backends:
            menu_list_opt.append("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            menu_list_opt.append("``30`` - InvokeAI (Install in Subsystem)")
            menu_list_opt.append("``31`` - InvokeAI (Install on Host OS)")
            menu_list_opt.append("``32`` - InvokeAI (Start Invoke AI on Host OS)")
            #menu_list_opt.append("``33`` - InvokeAI (Placeholder WIP Start Webserver)")
            for item in invokeai_list:
                valid_answers.append(item)
        
        if "ollama" in installed_backends:
            menu_list_opt.append("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            menu_list_opt.append("``40`` - Ollama (Install Models)")
            menu_list_opt.append("``41`` - Ollama (Uninstall Models)")
            for item in ollama_list:
                valid_answers.append(item)
        
        if "memgpt" in installed_backends:
            menu_list_opt.append("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            menu_list_opt.append("``50`` - Setup and Config MemGPT")
            menu_list_opt.append("``51`` - Run MemGPT")
            for item in memgpt_list:
                valid_answers.append(item)

        menu_list_opt.append("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        valid_answers.append("back")

        s.log("This menu will only show items supported and that are installed.")
    
        for line in menu_list_opt:
            s.log(line)

        s.log("``back`` - Go back to the main menu")

        questionbasic = "What would you like to do?: "
        temp_cxt = "This is the menu for running backend programs in the Midori AI subsystem"
        temp_cxt += f"\nThe numbers are the menu items that they can type into this menu, it only supports ``python ints``"
        temp_cxt += f"\nHere is a list of options the user can choose from:\n{', '.join(menu_list_opt).title()}"
        temp_cxt += f"\nIf there is nothing in that list, they dont have backends installed into the subsystem."
        temp_cxt += f"\ntell them to type ``back`` and then hit ``2`` to install a new backend to the subsystem"
        answerstartup = s.check_str(questionbasic, valid_answers, "no", None, None, temp_cxt, self.client_openai)

        if answerstartup.lower() == "back":
            return

        answerstartup = int(answerstartup)

        if 9 <= answerstartup <= 20:
            localai = localai_model_manager(self.ver_os_info, self.client, self.about_model_size, self.about_model_q_size, self.client_openai)

            if answerstartup == 10:
                localai.install_models()

            if answerstartup == 11:
                localai.edit_models()

            if answerstartup == 12:
                localai.remove_models()

            if answerstartup == 13:
                localai.backup_models()

        if 19 <= answerstartup <= 30:
            windows_wsl = windows_wsl_moder(self.ver_os_info, self.client, self.client_openai)

            if answerstartup == 20:
                windows_wsl.backup_wsl_docker_drives()

            if answerstartup == 21:
                windows_wsl.move_wsl_docker_drives()

            if answerstartup == 22:
                windows_wsl.purge_wsl_docker_drives()

        if 29 <= answerstartup <= 40:
            invokeai = invoke_ai(self.ver_os_info, self.client, self.client_openai)

            if answerstartup == 30:
                invokeai.install_in_subsystem()

            if answerstartup == 31:
                invokeai.install_on_host()

            if answerstartup == 32:
                invokeai.run()

        if 39 <= answerstartup <= 50:
            ollama = ollama_model_manager(self.ver_os_info, self.client, self.client_openai)

            if answerstartup == 40:
                ollama.install_models()

            if answerstartup == 41:
                ollama.uninstall_models()

        if 49 <= answerstartup <= 60:
            memgpt = memgpt_command_line(self.ver_os_info, self.client, self.client_openai)

            if answerstartup == 50:
                memgpt.install_via_commandline()

            if answerstartup == 51:
                memgpt.run_via_commandline()

class localai_model_manager:
    def __init__(self, ver_os_info, client, about_model_size, about_model_q_size, client_openai):
        self.client = client
        self.ver_os_info = ver_os_info
        self.client_openai = client_openai
        self.about_model_size = about_model_size
        self.about_model_q_size = about_model_q_size
    
    def check_for_backend(self, containers, docker_name):

        s.log(f"Checking for Docker Image")

        for container in containers:
            s.log(f"Checking Name: {container.name}, ID: {container.id}")

            # Check if there is a container with a name containing `service_name`
            if docker_name in str(container.name):
                # Get the container object
                s.log(f"Found {docker_name}, Linking the Subsystem to: {container.name} / {container.id}")
                container = self.client.containers.get(container.name)
                named_docker = container.name
                s.log(f"Midori AI Subsystem linked to {named_docker}")
                return named_docker, container

        for container in containers:
            print("--------------------------------------")
            s.log(f"Showing Name: {container.name}")
            print("--------------------------------------")

        s.log(f"Switching to manually typed mode, please enter the name of the docker image you are wishing to fork into ({docker_name}).")
        docker_name_manual = input("Enter Docker Image Name: ")

        is_gpu = input("Is this a GPU supported image? (yes or no): ")

        for container in containers:
            s.log(f"Checking Name: {container.name}, ID: {container.id}")

            # Check if there is a container with a name containing `service_name`
            if docker_name_manual in str(container.name):
                # Get the container object
                s.log(f"Found {docker_name}, Linking the Subsystem to: {container.name} / {container.id}")
                container = self.client.containers.get(container.name)
                named_docker = container.name
                s.log(f"Midori AI Subsystem linked to {named_docker}")
                
                if is_gpu.lower() == "yes":
                    docker_name_manual = docker_name_manual + "-gpu"

                return named_docker, container

        s.log(f"I could not find {docker_name}... is that installed?")
        input("Press Enter to go back to the menu: ")
        return None, None

    def install_models(self):
        containers = self.client.containers.list()

        ver_os_info = self.ver_os_info
        client_openai = self.client_openai
        about_model_size = self.about_model_size
        about_model_q_size = self.about_model_q_size

        models_folder_container = "/models"

        named_docker, container = self.check_for_backend(containers, "localai-midori-ai-backend")

        if named_docker is None:
            return
    
        s.clear_window(ver_os_info)

        s.log("Alright, now that I am logged into the docker, lets get you started with installing the model...")
        s.log("For more info on the models used, or links to the models, go to ``https://io.midori-ai.xyz/models/onsite_models/``")
        s.log(f"I am going to save our chat here and every thing I do to a file called ``{s.log_file_name}``, check it out if you like <3")
        s.log("Here are a few questions to find out what model you would like to try")

        use_gpu = True

        answer4_name = ""

        use_sd = "false"
        use_tts = "false"

        use_enbed = "false"
        use_llava = "false"

        use_llava = "false"
        use_enbed = "false"

        answerencrypted = "false"

        questionbasic = "Would you like to install a LLM?: "
        sd_valid_answers = ["yes", "no", "true", "false"]
        
        context_temp = "The user was asked if they would like to install a large language model for LocalAI, its a yes or no question"
            
        answerbasic = s.check_str(questionbasic, sd_valid_answers, "none", None, None, context_temp, client_openai)

        if answerbasic.lower() == "no":
            answerbasic = "False"
                
        if answerbasic.lower() == "yes":
            answerbasic = "True"

        answerbasic = answerbasic.lower()

        s.clear_window(ver_os_info)

        if answerbasic == "true":

            s.clear_window(ver_os_info)

            s.log(about_model_size)
            valid_answers2 = ["id", "huggingface", "base"]
            question2 = f"What size of known and supported model would you like to setup ({', '.join(valid_answers2)}): "
            
            context_temp = "The user was asked what size of model they would like to install... here is a list of sizes they can pick from "
            context_temp = f"{context_temp}\n{about_model_size}"
                
            answer2 = s.check_str(question2, valid_answers2, "none", None, None, context_temp, client_openai)
            answer2 = str(answer2.lower())

            valid_answers1 = ["q3", "q4", "q5", "q6", "q8"] 
            added_valid_answers1 = ["q4-k-m", "q5-k-m"]
            added_valid_answers2 = ["none"]

            answerbasic = "false".lower()

            if answer2.lower() == "8x7b":
                valid_answers1.extend(added_valid_answers1)
            
            if answer2.lower() != "id":
                valid_answers1.extend(added_valid_answers2)

            if answer2.lower() == "id":
                s.clear_window(ver_os_info)
                valid_answers2 = s.check_model_ids_file()
                question2 = f"What is the id of the model you would like to install? ({', '.join(valid_answers2)}): "
                    
                context_temp = f"this is a offsite model request, this is not recommended by midori ai. Here is a list of models they can install {valid_answers2}"

                answer2 = s.check_str(question2, valid_answers2, "none", None, None, context_temp, client_openai)
                answer2 = str(answer2.lower())

            s.clear_window(ver_os_info)

            if answer2.lower() == "huggingface":
                s.log("For huggingface models from the site, please copy and paste the link from the model page you with to download. Like")
                s.log("https://huggingface.co/macadeliccc/laser-dolphin-mixtral-2x7b-dpo-GGUF/resolve/main/laser-dolphin-mixtral-2x7b-dpo.q4_k_m.gguf?download=true")
                
                answer1 = "huggingface"
                answerbasic = "false".lower()

                huggingface_model_install = input("Paste Requested huggingface URL: ")
                huggingface_model_install = huggingface_model_install.replace("https://huggingface.co/", "")
                huggingface_model_install = huggingface_model_install.replace("/resolve/main", "")
                huggingface_model_install = huggingface_model_install.replace("?download=true", "")
                #https://huggingface.co/mlabonne/gemma-7b-it-GGUF/resolve/main/gemma-7b-it.Q2_K.gguf?download=true

                s.log(str(huggingface_model_install))

                # Split the link into parts
                huggingface_parts = huggingface_model_install.split("/")

                s.log(str(huggingface_parts))

                # Extract the user, repo name, and model filename
                user = huggingface_parts[0]
                repo_name = huggingface_parts[1]
                model_filename = huggingface_parts[2]

                # Print the extracted information
                s.log(f"User: {user}")
                s.log(f"Repo name: {repo_name}")
                s.log(f"Model filename: {model_filename}")
                                
                url = f"https://tea-cup.midori-ai.xyz/huggingface/model/{model_filename}"

                # Construct the cURL command
                curl_command = f"hf-downloader -un {user} -r {repo_name} -m {model_filename}"

            elif answer2.lower() == "base":
                s.log("For base models from the site, you can type all of the ones you want, like ``all-minilm-l6-v2 bert-cpp``")
                s.log("https://localai.io/basics/getting_started/")
                answer1 = "base"
                base_model_install = input("Type Requested Base Models: ")

            elif answer2.lower() != "base":
                question4 = "What would you like to name the models file?: \n"

                answer4 = input(question4)
                
                answer4 = str(answer4.lower())

                s.log(about_model_q_size)

                question = f"What type of quantised model would you like to setup? ({', '.join(valid_answers1)}): "
                
                context_temp = "The user was asked what type of quantised model they would like to install... here is a list of quantised model they can pick from "
                context_temp = f"{context_temp}\n{about_model_q_size}"
                    
                answer1 = s.check_str(question, valid_answers1, "none", None, None, context_temp, client_openai)

                if answer1.lower() == "none":
                    answer1 = str(answer1.lower())
                else:
                    answer1 = str(answer1.upper())

                # Check if the word "model" is in the answer
                if "model" in answer4:
                    # Remove the word "model"  from the answer
                    answer4 = answer4.replace("model", "")

                    # Print a message to the user
                    s.log("\nThe word 'model' has been removed from the file name.")

                # Check if GPU is turned on
                if "-gpu" in named_docker:
                    s.clear_window(ver_os_info)
                    # Ask the user the third question
                    if not answer1 == "none":
                        question = "\nNumber of GPU layers to give the model?  (0 to 2000): \n"
                        
                        answer3 = input(question)

                        answer3 = int(answer3)
                        use_gpu = True
                else:
                    answer3 = 0
                    answer3 = int(answer3)
                    use_gpu = False
                    
                s.clear_window(ver_os_info)

                if not answer1 == "none":
                    question = "\nNumber of CPU Cores to give the model? (0 to 2000): \n"
                        
                    answercpu = input(question)

                    answercpu = int(answercpu)

                s.clear_window(ver_os_info)

                if "-gpu" in named_docker:
                    question = "Would you like me to install a few Text to Speech models?: "
                    sd_valid_answers = ["yes", "no", "true", "false"]

                    context_temp = "The user was asked if they would like to install a TTS or Text to Speach model. This is a yes or no question"
                
                    answertts = s.check_str(question, sd_valid_answers, "none", None, None, context_temp, client_openai)

                    if answertts.lower() == "no":
                        answertts = "False"
                        
                    if answertts.lower() == "yes":
                        answertts = "True"

                    answertts = answertts.lower()
                    use_tts = answertts

                    s.clear_window(ver_os_info)

                question = "Would you like me to install the embedding model?: "
                sd_valid_answers = ["yes", "no", "true", "false"]
                    
                context_temp = "The user was asked if they would like to install the vector store embedding model. This is a yes or no question"
                    
                answerenbed = s.check_str(question, sd_valid_answers, "none", None, None, context_temp, client_openai)

                if answerenbed.lower() == "no":
                    answerenbed = "False"
                        
                if answerenbed.lower() == "yes":
                    answerenbed = "True"

                answerenbed = answerenbed.lower()
                use_enbed = answerenbed

                s.clear_window(ver_os_info)

                if "-gpu" in named_docker:
                    question = "Would you like me to install a Stable diffusion model?: "
                    sd_valid_answers = ["yes", "no", "true", "false"]
                
                    context_temp = "The user was asked if they would like to install a Stable diffusion (for making photos) model. This is a yes or no question"

                    answersd = s.check_str(question, sd_valid_answers, "none", None, None, context_temp, client_openai)

                    if answersd.lower() == "no":
                        answersd = "False"
                    
                    if answersd.lower() == "yes":
                        answersd = "True"

                    answersd = answersd.lower()
                    use_sd = answersd

                    s.clear_window(ver_os_info)
                    
                    question = "Would you like me to install the Llava model?: "
                    sd_valid_answers = ["yes", "no", "true", "false"]
                
                    context_temp = "The user was asked if they would like to install the llava model, its a sight based model to help programs see photos. This is a yes or no question"

                    answerllava = s.check_str(question, sd_valid_answers, "none", None, None, context_temp, client_openai)

                    if answerllava.lower() == "no":
                        answerllava = "False"
                    
                    if answerllava.lower() == "yes":
                        answerllava = "True"

                    answerllava = answerllava.lower()
                    use_llava = answerllava

                    s.clear_window(ver_os_info)
                else:
                    s.log("Looks like you are running on CPU only, Skipping: Stable diffusion, Llava, Huggingface Models")
                    
                    question = "Would you like to use our slower but encrypted endpoint for LocalAI to serve and setup the model's files (Not the models file itself)?: "
                    sd_valid_answers = ["yes", "no", "true", "false"]
                    
                    context_temp = "The user was asked if they would like to use Midori AI slower but encrypted endpoint. This is a yes or no question"

                    answerencrypted = s.check_str(question, sd_valid_answers, "none", None, None, context_temp, client_openai)

                    if answerencrypted.lower() == "no":
                        answerencrypted = "False"
                    
                    if answerencrypted.lower() == "yes":
                        answerencrypted = "True"

                    answerencrypted = answerencrypted.lower()

                    s.clear_window(ver_os_info)


        s.log(f"I am now going to install everything you requested, please wait for me to get done. As ill be running commands inside of your docker image.")
        s.log("Hit enter to start")

        input()

        s.clear_window(ver_os_info)

        inside_model_folder = models_folder_container

        if answerbasic == "true":
            s.log(f"The type of model you want to setup is: {answer1}")
            s.log(f"The size of the known model you want to setup is: {answer2}")
            s.log(f"The amount of GPU layers you want to give it is: {answer3}")
            s.log(f"You named the model: {answer4}")

            if answer2 == "8x7b":
                answer2 = "43b"

            if answer2 == "2x7b":
                answer2 = "14b"
            temp_chat_path =  inside_model_folder + "/localai-chat.tmpl"
            temp_chatmsg_path = inside_model_folder + "/localai-chatmsg.tmpl"
            model_path_temp = inside_model_folder + f"/{answer4}.gguf"
            yaml_path_temp = inside_model_folder + f"/{answer4}.yaml"

            docker_commands_cpu = [
                ["echo", f"Setting up the {answer2} model you requested"],
                ["apt-get", "-y", "install", "wget"],
                ["rm", "-f", f"{inside_model_folder}/{answer4}.gguf"],
                ["rm", "-f", f"{inside_model_folder}/localai-chat.tmpl"],
                ["rm", "-f", f"{inside_model_folder}/localai-chatmsg.tmpl"],
                ["rm", "-f", f"{inside_model_folder}/{answer4}.yaml"],
                ["wget", "--show-progress=no", "-O", f"localai-chat.tmpl", f"https://tea-cup.midori-ai.xyz/download/localai-chat.tmpl"],
                ["wget", "--show-progress=no", "-O", f"localai-chatmsg.tmpl", f"https://tea-cup.midori-ai.xyz/download/localai-chatmsg.tmpl"],
                ["wget", "--show-progress=no", "-O", f"{answer4}.yaml", f"https://tea-cup.midori-ai.xyz/download/models.yaml"],
                ["echo", f"This next step will take 10+ mins, please do not exit or close this program"],
                ["wget", "--show-progress=no", "-O", f"{answer4}.gguf", f"https://tea-cup.midori-ai.xyz/download/{answer2}model{answer1}.gguf"],
                ["cp", f"localai-chat.tmpl", f"{temp_chat_path}"],
                ["cp", f"localai-chatmsg.tmpl", f"{temp_chatmsg_path}"],
                ["cp", f"{answer4}.yaml", f"{yaml_path_temp}"],
                ["cp", f"{answer4}.gguf", f"{model_path_temp}"],
                ["sed", "-i", f"s/name.*/name: {answer4}/g", f"{yaml_path_temp}"],
                ["sed", "-i", f"s/threads.*/threads: {answercpu}/g", f"{yaml_path_temp}"],
                ["sed", "-i", f"s/model.*/model: {answer4}.gguf/g", f"{yaml_path_temp}"],
                ["echo", f"Catting the yaml for easyer debuging..."],
                ["cat", f"{yaml_path_temp}"],
                ["rm", "-f", "localai-chat.tmpl"],
                ["rm", "-f", "localai-chatmsg.tmpl"],
                ["rm", "-f", f"{answer4}.yaml"],
                ["rm", "-f", f"{answer4}.gguf"],
            ]

            docker_commands_gpu = [
                ["echo", f"Setting up the {answer2} model you requested"],
                ["apt-get", "-y", "install", "wget"],
                ["rm", "-f", f"{inside_model_folder}/{answer4}.gguf"],
                ["rm", "-f", f"{inside_model_folder}/localai-chat.tmpl"],
                ["rm", "-f", f"{inside_model_folder}/localai-chatmsg.tmpl"],
                ["rm", "-f", f"{inside_model_folder}/{answer4}.yaml"],
                ["wget", "--show-progress=no", "-O", f"localai-chat.tmpl", f"https://tea-cup.midori-ai.xyz/download/localai-chat.tmpl"],
                ["wget", "--show-progress=no", "-O", f"localai-chatmsg.tmpl", f"https://tea-cup.midori-ai.xyz/download/localai-chatmsg.tmpl"],
                ["wget", "--show-progress=no", "-O", f"{answer4}.yaml", f"https://tea-cup.midori-ai.xyz/download/models-gpu.yaml"],
                ["echo", f"This next step will take 10+ mins, please do not exit or close this program"],
                ["wget", "--show-progress=no", "-O", f"{answer4}.gguf", f"https://tea-cup.midori-ai.xyz/download/{answer2}model{answer1}.gguf"],
                ["cp", f"localai-chat.tmpl", f"{temp_chat_path}"],
                ["cp", f"localai-chatmsg.tmpl", f"{temp_chatmsg_path}"],
                ["cp", f"{answer4}.yaml", f"{yaml_path_temp}"],
                ["cp", f"{answer4}.gguf", f"{model_path_temp}"],
                ["sed", "-i", f"s/name.*/name: {answer4}/g", f"{yaml_path_temp}"],
                ["sed", "-i", f"s/threads.*/threads: {answercpu}/g", f"{yaml_path_temp}"],
                ["sed", "-i", f"s/gpu_layers.*/gpu_layers: {answer3}/g", f"{yaml_path_temp}"],
                ["sed", "-i", f"s/model.*/model: {answer4}.gguf/g", f"{yaml_path_temp}"],
                ["echo", f"Catting the yaml for easyer debuging..."],
                ["cat", f"{yaml_path_temp}"],
                ["rm", "-f", "localai-chat.tmpl"],
                ["rm", "-f", "localai-chatmsg.tmpl"],
                ["rm", "-f", f"{answer4}.yaml"],
                ["rm", "-f", f"{answer4}.gguf"],
            ]

            docker_commands_vllm = [
                ["echo", f"Setting up the {answer2} model you requested"],
                ["apt-get", "-y", "install", "wget"],
                ["rm", "-f", f"{inside_model_folder}/{answer4}.yaml"],
                ["wget", "--show-progress=no", "-O", f"{answer4}.yaml", f"https://tea-cup.midori-ai.xyz/download/models-{answer2}-vllm.yaml"],
                ["cp", f"{answer4}.yaml", f"{yaml_path_temp}"],
                ["sed", "-i", f"s/name.*/name: {answer4}/g", f"{yaml_path_temp}"],
                ["echo", f"Catting the yaml for easyer debuging..."],
                ["cat", f"{yaml_path_temp}"],
                ["rm", "-f", f"{answer4}.yaml"],
            ]
            
            encrypted_docker_commands_cpu = [
                ["echo", f"Setting up the {answer2} model you requested"],
                ["apt-get", "-y", "install", "wget"],
                ["pip", "install", "psutil", "requests", "diskcache", "cryptography", "aiohttp"],
                ["rm", "-f", f"{inside_model_folder}/{answer4}.gguf"],
                ["rm", "-f", f"{inside_model_folder}/localai-chat.tmpl"],
                ["rm", "-f", f"{inside_model_folder}/localai-chatmsg.tmpl"],
                ["rm", "-f", f"{inside_model_folder}/{answer4}.yaml"],
                ["rm", "-f", "helper_app.py"],
                ["wget", "--show-progress=no", "-O", "helper_app.py", "https://tea-cup.midori-ai.xyz/download/helper_app.py"],
                ["python3", "helper_app.py", "localai-chat.tmpl"],
                ["python3", "helper_app.py", "localai-chatmsg.tmpl"],
                ["python3", "helper_app.py", "models.yaml"],
                ["echo", f"This next step will take 10+ mins, please do not exit or close this program"],
                ["wget", "--show-progress=no", "-O", f"{answer2}model{answer1}.gguf", f"https://tea-cup.midori-ai.xyz/download/{answer2}model{answer1}.gguf"],
                ["cp", f"localai-chat.tmpl", f"{temp_chat_path}"],
                ["cp", f"localai-chatmsg.tmpl", f"{temp_chatmsg_path}"],
                ["cp", f"models.yaml", f"{yaml_path_temp}"],
                ["cp", f"{answer2}model{answer1}.gguf", f"{model_path_temp}"],
                ["sed", "-i", f"s/name.*/name: {answer4}/g", f"{yaml_path_temp}"],
                ["sed", "-i", f"s/threads.*/threads: {answercpu}/g", f"{yaml_path_temp}"],\
                ["sed", "-i", f"s/model.*/model: {answer4}.gguf/g", f"{yaml_path_temp}"],
                ["echo", f"Catting the yaml for easyer debuging..."],
                ["cat", f"{yaml_path_temp}"],
                ["rm", "-f", "localai-chat.tmpl"],
                ["rm", "-f", "localai-chatmsg.tmpl"],
                ["rm", "-f", f"models.yaml"],
                ["rm", "-f", f"{answer2}model{answer1}.gguf"],
            ]

            encrypted_docker_commands_gpu = [
                ["echo", f"Setting up the {answer2} model you requested"],
                ["apt-get", "-y", "install", "wget"],
                ["pip", "install", "psutil", "requests", "diskcache", "cryptography", "aiohttp"],
                ["rm", "-f", f"{inside_model_folder}/{answer4}.gguf"],
                ["rm", "-f", f"{inside_model_folder}/localai-chat.tmpl"],
                ["rm", "-f", f"{inside_model_folder}/localai-chatmsg.tmpl"],
                ["rm", "-f", f"{inside_model_folder}/{answer4}.yaml"],
                ["rm", "-f", "helper_app.py"],
                ["wget", "--show-progress=no", "-O", "helper_app.py", "https://tea-cup.midori-ai.xyz/download/helper_app.py"],
                ["python3", "helper_app.py", "localai-chat.tmpl"],
                ["python3", "helper_app.py", "localai-chatmsg.tmpl"],
                ["python3", "helper_app.py", "models-gpu.yaml"],
                ["echo", f"This next step will take 10+ mins, please do not exit or close this program"],
                ["wget", "--show-progress=no", "-O", f"{answer2}model{answer1}.gguf", f"https://tea-cup.midori-ai.xyz/download/{answer2}model{answer1}.gguf"],
                ["cp", f"localai-chat.tmpl", f"{temp_chat_path}"],
                ["cp", f"localai-chatmsg.tmpl", f"{temp_chatmsg_path}"],
                ["cp", f"models-gpu.yaml", f"{yaml_path_temp}"],
                ["cp", f"{answer2}model{answer1}.gguf", f"{model_path_temp}"],
                ["sed", "-i", f"s/name.*/name: {answer4}/g", f"{yaml_path_temp}"],
                ["sed", "-i", f"s/threads.*/threads: {answercpu}/g", f"{yaml_path_temp}"],
                ["sed", "-i", f"s/gpu_layers.*/gpu_layers: {answer3}/g", f"{yaml_path_temp}"],
                ["sed", "-i", f"s/model.*/model: {answer4}.gguf/g", f"{yaml_path_temp}"],
                ["echo", f"Catting the yaml for easyer debuging..."],
                ["cat", f"{yaml_path_temp}"],
                ["rm", "-f", "localai-chat.tmpl"],
                ["rm", "-f", "localai-chatmsg.tmpl"],
                ["rm", "-f", f"models-gpu.yaml"],
                ["rm", "-f", f"{answer2}model{answer1}.gguf"],
            ]

        else:
            docker_commands_cpu = []
            docker_commands_gpu = []

        if answerencrypted == "true":
            docker_commands_cpu = encrypted_docker_commands_cpu
            docker_commands_gpu = encrypted_docker_commands_gpu

        if use_gpu:
            docker_commands = docker_commands_gpu
        else:
            docker_commands = docker_commands_cpu

        if answer1 == "none":
            docker_commands = docker_commands_vllm

        if answer1 == "huggingface":
            huggingface_commands = [
                ["hf-downloader", "-un", user, "-r", repo_name, "-m", model_filename],
                ["cp", f"\"{model_filename}\"", f"\"{inside_model_folder}/{model_filename}\""],
                ["rm", "-f", f"{model_filename}"],
            ]
            docker_commands.extend(huggingface_commands)

        if use_tts == "true":
            tts_commands = [
                ["apt-get", "-y", "install", "wget"],
                ["wget", "--show-progress=no", "-O", inside_model_folder + f"/en_US-amy-medium.onnx.json", f"https://tea-cup.midori-ai.xyz/download/en_US-amy-medium.onnx.json"],
                ["wget", "--show-progress=no", "-O", inside_model_folder + f"/en_US-amy-medium.onnx", f"https://tea-cup.midori-ai.xyz/download/en_US-amy-medium.onnx"],
                ["wget", "--show-progress=no", "-O", inside_model_folder + f"/en-us-kathleen-low.onnx.json", f"https://tea-cup.midori-ai.xyz/download/en-us-kathleen-low.onnx.json"],
                ["wget", "--show-progress=no", "-O", inside_model_folder + f"/en-us-kathleen-low.onnx", f"https://tea-cup.midori-ai.xyz/download/en-us-kathleen-low.onnx"],
            ]
            docker_commands.extend(tts_commands)

        if use_sd == "true":
            sd_commands = [
                ["apt-get", "-y", "install", "wget"],
                ["wget", "--show-progress=no", "-O", inside_model_folder + f"/diffusers.yaml", f"https://tea-cup.midori-ai.xyz/download/diffusers.yaml"]
            ]
            docker_commands.extend(sd_commands)

        if use_enbed == "true":
            embed_commands = [
                ["apt-get", "-y", "install", "wget"],
                ["wget", "--show-progress=no", "-O", inside_model_folder + f"/embedding.yaml", f"https://tea-cup.midori-ai.xyz/download/bert-embeddings.yaml"],
                ["wget", "--show-progress=no", "-O", inside_model_folder + f"/bert-MiniLM-L6-v2q4_0.bin", f"https://tea-cup.midori-ai.xyz/download/bert-MiniLM-L6-v2q4_0.bin"],
            ]
            docker_commands.extend(embed_commands)

        if use_llava == "true":
            llava_commands = [
                ["echo", f"This next step will take 5+ mins, please do not exit or close this program"],
                ["apt-get", "-y", "install", "wget"],
                ["wget", "--show-progress=no", "-O", inside_model_folder + f"/ggml-model-q4_k.gguf", f"https://huggingface.co/PsiPi/liuhaotian_llava-v1.5-13b-GGUF/resolve/main/llava-v1.5-13b-Q6_K.gguf"],
                ["wget", "--show-progress=no", "-O", inside_model_folder + f"/mmproj-model-f16.gguf", f"https://huggingface.co/mys/ggml_bakllava-1/resolve/main/mmproj-model-f16.gguf"],
                ["wget", "--show-progress=no", "-O", inside_model_folder + f"/chat-simple.tmpl", f"https://github.com/mudler/LocalAI/blob/b8240b4c1839089b9d06a3e2b1c629a294cff87e/examples/configurations/llava/chat-simple.tmpl"],
                ["wget", "--show-progress=no", "-O", inside_model_folder + f"/llava.yaml", f"https://github.com/mudler/LocalAI/blob/b8240b4c1839089b9d06a3e2b1c629a294cff87e/examples/configurations/llava/llava.yaml"],
            ]
            docker_commands.extend(llava_commands)
        
        if answer1 == "base":
            base_commands = [
                ["./local-ai", f"{base_model_install}", "&"],
            ]
            docker_commands.extend(base_commands)

        # Run a command inside the container
        s.log("Downloading and setting up model into the docker")
        for command in docker_commands:
            s.log(f"Running {command}: ")
            void, stream = container.exec_run(command, stream=True)
            for data in stream:
                s.log(data.decode())

        s.log("All done, I am now rebooting LocalAI")
        container.restart()
        s.log("Thank you! Please enjoy your new models!")
        input("Press Enter to return")

    def edit_models(self):
        containers = self.client.containers.list()

        ver_os_info = self.ver_os_info
        client_openai = self.client_openai

        models_folder_container = "/models"
        docker_commands = []

        s.log(f"Checking for Subsystem")

        named_docker, container = self.check_for_backend(containers, "localai-midori-ai-backend")
        
        if named_docker is None:
            return
        
        bearer_token = str(input("If you have a API Key, please put it here. Else type no: "))

        while True:
            try:
                ip_address = str(input("What is the LocalAI's IP? (192.168.x.x): "))
                if "localhost" in ip_address:
                    raise ValueError("Localhost is not a valid IP address.")
                break
            except ValueError as e:
                s.log(f"Error: {e}. Please try again.")

        models_ports = str("38080")

        headers = {"Authorization": f"Bearer {bearer_token}"}

        response = requests.get(f"http://{ip_address}:{models_ports}/models", headers=headers)

        if response.status_code == 200:
            response_data = json.loads(response.text)
            models = response_data["data"]

            # Extract model IDs
            model_ids = [model["id"] for model in models]

            filtered_model_ids = model_ids

            s.log(filtered_model_ids)

            filtered_model_ids.append("exit")
            
            s.clear_window(ver_os_info)

            while True:
                s.log(f"Available model IDs: {filtered_model_ids}")
                s.log("Type ``exit`` to exit")

                question = "What model would you like to edit?: "
                valid_answers = filtered_model_ids
        
                context_temp = f"The user was asked what model they would like to edit. Please tell them to pick from the list.\n{str(valid_answers)}"
                    
                answeryamleditor = s.check_str(question, valid_answers, "none", None, None, context_temp, client_openai)

                if ".yaml" in answeryamleditor or ".gguf" in answeryamleditor:
                    answeryamleditor = answeryamleditor.replace(".yaml", "").replace(".gguf", "")

                if answeryamleditor == "exit":
                    s.log("exiting...")
                    return
                
                s.clear_window(ver_os_info)

                valid_answers = ["gpu_layers", "f16", "threads", "low_vram", "mmap", "mmlock", "name", "cuda", "numa", "no_mulmatq"]
                question = f"{str(valid_answers)}\nWhat setting would you like to edit?: "

                context_temp = f"The user was asked what setting of the {answeryamleditor} llm model they have installed would they like to edit. Here is a full list of thing they can edit"
                context_temp = f"{context_temp}\ngpu_layers = How much GPU the model can use, recommended starting at 5 then adding more if there is free vram"
                context_temp = f"{context_temp}\nthreads = CPU cores for the model, recommended to keep this to under 50% their real core count"
                context_temp = f"{context_temp}\nname = the name that the model goes by when being requested by OpenAI V1"
                context_temp = f"{context_temp}\ncuda = For the model to use the GPU or Not, is a bool"
                context_temp = f"{context_temp}\nlow_vram = Sets the model into low vram use mode, recommended for lower end computers, is a bool"
                context_temp = f"{context_temp}\nmmap = mmap is a system call that maps the model into memory, allowing direct access to the models files, is a bool"
                context_temp = f"{context_temp}\nmmlock = mmlock is a Linux kernel feature that allows users to lock pages in memory, keeping the model in memory, is a bool"
                context_temp = f"{context_temp}\nno_mulmatq = The ``no_mulmtq`` parameter controls whether or not XLA's MatMul will be used. Setting this to True may save memory, but may reduce performance and/or numerical precision. Is a bool"
                context_temp = f"{context_temp}\nnuma = NUMA (Non-Uniform Memory Access) optimizes memory access in systems with multiple memory controllers, improving performance by ensuring processes access data from the closest memory node, is a bool"
                    
                answeryamleditor_two = s.check_str(question, valid_answers, "none", None, None, context_temp, client_openai)
                
                s.clear_window(ver_os_info)

                questionbasic = f"What would you like to set ``{answeryamleditor_two}`` to (NO TYPECHECKING use at your own risk)?: "
                answeryamleditor_three = str(input(questionbasic))
                
                s.clear_window(ver_os_info)

                inside_model_folder = models_folder_container
                yaml_path_temp = inside_model_folder + f"/{answeryamleditor}.yaml"

                docker_commands = [
                    ["yaml_edit", "-i", answeryamleditor_two, "-d", f"{answeryamleditor_three.lower()}", yaml_path_temp],
                ]

                # Run a command inside the container
                s.log("editing model from inside the docker")
                for command in docker_commands:
                    s.log(f"Running {command}: ")
                    command_output = container.exec_run(command)
                    s.log(command_output.output.decode("utf-8", errors="ignore"))

                s.log("All done, I am now rebooting LocalAI")
                container.restart()
                s.log("Thank you! Models edited!")

    def remove_models(self):
        containers = self.client.containers.list()
        s.log(f"Checking for Subsystem")

        named_docker, container = self.check_for_backend(containers, "midori_ai_subsystem")
        
        if named_docker is None:
            return

        # Run a command inside the container
        command = "ls models/"
        s.log(f"Running {command}: ")
        void, stream = container.exec_run(command, stream=True)
        for data in stream:
            s.log(data.decode())
        
        docker_commands = []
        
        s.log("Please type in the model you wish to remove with out the ``gguf`` or ``yaml``")
        s.log("You may list more than one, To delete all type ``*``")
        remove_model_str = input("Remove model: ")
        remove_model_list = remove_model_str.split()

        for item in remove_model_list:
            docker_commands.append(f"rm -rf models/{item}.*")

        # Run a command inside the container
        s.log("Removing the listed models")
        for command in docker_commands:
            s.log(f"Running {command}: ")
            void, stream = container.exec_run(command, stream=True)
            for data in stream:
                s.log(data.decode())

        s.log("All done, I am now rebooting LocalAI")
        container.restart()
        s.log("Thank you!")
        input("Press Enter to return")

    def backup_models(self):
        containers = self.client.containers.list()

        for container in containers:
            s.log(f"Checking Name: {container.name}, ID: {container.id}")

            # Check if there is a container with a name containing `service_name`
            if "midori_ai_subsystem" in container.name:
                # Get the container object
                s.log(f"Found LocalAI, Linking the Subsystem to: {container.name} / {container.id}")
                container = self.client.containers.get(container.name)
                s.log(f"Midori AI Subsystem linked to LocalAI")
                s.log(f"Midori AI Subsystem linked to Ollama")
                break

        if container is None:
            s.log(f"I could not find localai... did you install that backend?")
            input("Press Enter to go back to the menu: ")
            return
        
        docker_commands = [
            "mkdir files/backup",
            "mkdir files/backup/models",
            "chmod -R 777 files/backup",
            "cp files/localai/models files/backup/models"
        ]

        # Run a command inside the container
        s.log("Backing up models into the subsystem files")
        for command in docker_commands:
            s.log(f"Running {command}: ")
            void, stream = container.exec_run(command, stream=True)
            for data in stream:
                s.log(data.decode())

        input("Press Enter to return")

class invoke_ai:
    def __init__(self, ver_os_info, client, client_openai):
        self.client = client
        self.ver_os_info = ver_os_info
        self.client_openai = client_openai
    
    def install_in_subsystem(self):
        container = s.get_subsystem(self.client)
        container_id = container.id
        s.clear_window(self.ver_os_info)
        s.log(f"Reminder to install InvokeAI into the files/invokeai folder for easier running")
        input("Press enter to start the install...")
        os.system(f"docker exec -it {container_id} apt-get update && apt-get install python3.11-venv")
        os.system(f"docker exec -it {container_id} ./files/invokeai/InvokeAI-Installer/install.sh")
        file_install_json = os.path.join("files", "invokeai", "installed")
        file_install_old = os.path.join("files", "invokeai", "InvokeAI-Installer")
        
        with open(file_install_json, "w") as f:
            f.write("docker")
        
        os.remove(file_install_old)

        s.log(f"Leaving the subsystem shell, returning to host os...")
    
    def install_on_host(self):
        s.clear_window(self.ver_os_info)
        s.log(f"Reminder to install InvokeAI into the files/invokeai folder for easier running")
        input("Press enter to start the install...")

        installer_base = os.path.join("files", "invokeai", "InvokeAI-Installer")
        
        if self.ver_os_info == 'windows':
            os.system(f'call {os.path.join(installer_base, "install.bat")}')
        if self.ver_os_info == 'linux':
            os.system('chmod +x ./files/invokeai/InvokeAI-Installer/install.sh')
            os.system(f'./files/invokeai/InvokeAI-Installer/install.sh')

        file_install_json = os.path.join("files", "invokeai", "installed")
        file_install_old = os.path.join("files", "invokeai", "InvokeAI-Installer")
        
        with open(file_install_json, "w") as f:
            f.write("os")
        
        os.remove(file_install_old)

        s.log(f"All done, going back to main menu")
    
    def run(self):
        file_install_json = os.path.join("files", "invokeai", "installed")
        file_folder_json = os.path.join("files", "invokeai", "folder")

        try:
            with open(file_install_json, "r") as f:
                install = f.read()

        except Exception as e:
            s.log("InvokeAI is not installed on this subsystem")
            input("Please hit enter to go back to the main menu: ")
        
        
        if install == "os":
            if os.path.exists(file_folder_json):
                with open(file_folder_json, "r") as f:
                    invoke_folder_loco = f.read()
            else:
                while True:
                    s.log("Where did you install InvokeAI? Please paste the folder here.")
                    invoke_folder_loco = input("InvokeAI Folder: ")
                    
                    if os.path.exists(invoke_folder_loco):
                        
                        if os.name == 'nt':
                            invoke_file = os.path.join(invoke_folder_loco, "invoke.bat")
                        else:
                            invoke_file = os.path.join(invoke_folder_loco, "invoke.sh")

                        if os.path.exists(invoke_file):
                            venv_path = os.path.join(invoke_folder_loco, ".venv")
                            if os.path.exists(venv_path):
                                with open(file_folder_json, "w") as f:
                                    f.write(invoke_folder_loco)

                                break
                    else:
                        s.log(f"You inputted {invoke_folder_loco}")
                        s.log("Error, folder or invoke runner not found please try again")
            
        if install == "os":
            s.log(f"Running the `{invoke_file}` for this install on OS")
                    
            if os.name == 'nt':
                os.system(f"call {invoke_file}")
            else:
                os.system(f"{invoke_file}")
        
        if install == "docker":
            container = s.get_subsystem(self.client)
            container_id = container.id
            s.log("Dropping you into the subsystem shell for you to run the invoke.sh file")
            os.system(f"docker exec -it {container_id} /bin/bash && cd files/invokeai")
            input("Please hit enter to go back to the main menu: ")

class windows_wsl_moder:
    def __init__(self, ver_os_info, client, client_openai):
        self.client = client
        self.ver_os_info = ver_os_info
        self.client_openai = client_openai

    def make_folder(self, folder_path):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
    
    def backup_wsl_docker_drives(self):
        print("WARNING THIS CODE IS STILL IN TESTING. THIS CODE MOSTLIKELY MAY NUKE YOUR WSL INSTALL! USE AT YOUR OWN RISK")
        input("Hit enter to nuke your wsl install: ")

        print(Fore.RED + 'If you have alot of installed dockers, \nthis may take up to 2 to 6 hours, do not stop the manager once the backup has started' + Fore.WHITE)
        print(Fore.RED + 'Do not restart docker desktop, the manager will restart it when ready' + Fore.WHITE)

        s.log("Please paste the windows folder you would like to back up the docker data OS to")
        backup_folder = os.path.normpath(str(input("Backup Folder: ")))

        input(f"Hit enter to move your Docker Data / Docker OS Backup to {backup_folder}: ")

        folders = backup_folder.split(os.path.sep)
        current_path = folders[0]

        for folder in folders[1:]:
            current_path = os.path.join(current_path, folder)
            self.make_folder(current_path)
        
        tarfile = os.path.join(backup_folder, 'docker-desktop-data.tar')

        os.system(f"wsl --shutdown")

        input("Please click \"quit\" on the docker desktop popup, then press enter here: ")

        os.system(f"wsl --export docker-desktop-data {tarfile}")

        os.system("\"C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe\"")

        s.log(f"The docker data os was backed up to ``{tarfile}``")
        input("Hit Enter to go Back")
    
    def move_wsl_docker_drives(self):
        print("WARNING THIS CODE IS STILL IN TESTING. THIS CODE MOSTLIKELY MAY NUKE YOUR WSL INSTALL! USE AT YOUR OWN RISK")
        input("Hit enter to nuke your wsl install: ")

        print(Fore.RED + 'If you have a lot of installed dockers, \nthis may take up to 2 hours, do not stop the manager once the move has started' + Fore.WHITE)
        print(Fore.RED + 'Do not restart docker desktop, the manager will restart it when ready' + Fore.WHITE)

        s.log("Requesting target folder for Docker data relocation...")
        working_folder = os.path.normpath(str(input("Working Folder: ")))

        input(f"Hit enter to move your Docker Data / Docker OS install to {working_folder}: ")

        folders = working_folder.split(os.path.sep)
        current_path = folders[0]

        for folder in folders[1:]:
            current_path = os.path.join(current_path, folder)
            self.make_folder(current_path)
        
        tarfile = os.path.join(working_folder, 'docker-desktop-data.tar')
        tarfile2 = os.path.join(working_folder, 'docker-desktop.tar')

        os.system(f"wsl --shutdown")

        input("Please click \"quit\" on the docker desktop popup, then press enter here: ")

        s.log("Exporting WSL Docker data to a tar archive...")
        s.log(f"wsl --export docker-desktop-data \"{tarfile}\"")
        os.system(f"wsl --export docker-desktop-data \"{tarfile}\"")

        s.log("Unregistering the WSL Docker data distribution...")
        s.log(f"wsl --unregister docker-desktop-data")
        os.system(f"wsl --unregister docker-desktop-data")

        s.log("Importing WSL Docker data from the tar archive to the new location...")
        s.log(f"wsl --import docker-desktop-data \"{working_folder}\" \"{tarfile}\" --version 2")
        os.system(f"wsl --import docker-desktop-data \"{working_folder}\" \"{tarfile}\" --version 2")
        os.remove(tarfile)

        s.log("Exporting WSL Docker to a tar archive...")
        s.log(f"wsl --export docker-desktop \"{tarfile2}\"")
        os.system(f"wsl --export docker-desktop \"{tarfile2}\"")

        s.log("Unregistering the WSL Docker distribution...")
        s.log(f"wsl --unregister docker-desktop")
        os.system(f"wsl --unregister docker-desktop")

        s.log("Importing WSL Docker from the tar archive to the new location...")
        s.log(f"wsl --import docker-desktop \"{working_folder}\" \"{tarfile2}\" --version 2")
        os.system(f"wsl --import docker-desktop \"{working_folder}\" \"{tarfile2}\" --version 2")
        os.remove(tarfile2)

        os.system("\"C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe\"")

        input("Hit Enter to go Back")
    
    def purge_wsl_docker_drives(self):
        print("WARNING THIS CODE IS STILL IN TESTING. THIS CODE MOSTLIKELY MAY NUKE YOUR WSL INSTALL! USE AT YOUR OWN RISK")
        input("Hit enter to nuke your docker data install: ")

        print(Fore.RED + 'If you have a lot of installed dockers, \nthis may take up to 2 hours, do not stop the manager once the move has started' + Fore.WHITE)
        print(Fore.RED + 'Do not restart docker desktop, the manager will restart it when ready' + Fore.WHITE)

        input("Hit enter to nuke your docker data install: ")

        os.system(f"wsl --shutdown")

        input("Please click \"quit\" on the docker desktop popup, then press enter here: ")

        s.log("Unregistering the WSL Docker data distribution...")
        s.log(f"wsl --unregister docker-desktop-data")
        os.system(f"wsl --unregister docker-desktop-data")

        s.log("Unregistering the WSL Docker distribution...")
        s.log(f"wsl --unregister docker-desktop")
        os.system(f"wsl --unregister docker-desktop")

        os.system("\"C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe\"")

        input("Hit Enter to go Back")

class ollama_model_manager:
    def __init__(self, ver_os_info, client, client_openai):
        self.client = client
        self.ver_os_info = ver_os_info
        self.client_openai = client_openai   

    def check_for_backend(self, containers, docker_name):

        s.log(f"Checking for Docker Image")

        for container in containers:
            s.log(f"Checking Name: {container.name}, ID: {container.id}")

            # Check if there is a container with a name containing `service_name`
            if docker_name in str(container.name):
                # Get the container object
                s.log(f"Found {docker_name}, Linking the Subsystem to: {container.name} / {container.id}")
                container = self.client.containers.get(container.name)
                named_docker = container.name
                s.log(f"Midori AI Subsystem linked to {named_docker}")
                return named_docker, container

        for container in containers:
            print("--------------------------------------")
            s.log(f"Showing Name: {container.name}")
            print("--------------------------------------")

        s.log(f"Switching to manually typed mode, please enter the name of the docker image you are wishing to fork into ({docker_name}).")
        docker_name_manual = input("Enter Docker Image Name: ")

        for container in containers:
            s.log(f"Checking Name: {container.name}, ID: {container.id}")

            # Check if there is a container with a name containing `service_name`
            if docker_name_manual in str(container.name):
                # Get the container object
                s.log(f"Found {docker_name}, Linking the Subsystem to: {container.name} / {container.id}")
                container = self.client.containers.get(container.name)
                named_docker = container.name
                s.log(f"Midori AI Subsystem linked to {named_docker}")

                return named_docker, container

        s.log(f"I could not find {docker_name}... is that installed?")
        input("Press Enter to go back to the menu: ")
        return None, None

    def install_models(self):
        containers = self.client.containers.list()

        ver_os_info = self.ver_os_info
        client_openai = self.client_openai

        named_docker, container = self.check_for_backend(containers, "ollama-midori-ai-backend")

        if named_docker is None:
            return
        
        s.log("Please check ollamas site for supported models")
        s.log("You can install more than one model by typeing each name with a space")
        model_to_install = input("Type the model(s) you would like to install: ")
        docker_commands = []
        ollama_commands = []
        models_to_install = model_to_install.split()
        for model in models_to_install:
            ollama_commands.append (["ollama", "run", model])
        docker_commands.extend(ollama_commands)

        # Run a command inside the container
        s.log("Downloading and setting up model into the docker")
        for command in docker_commands:
            s.log(f"Running {command}: ")
            void, stream = container.exec_run(command, stream=True)
            for data in stream:
                s.log(data.decode())

        s.log("All done, I am now rebooting Ollama")
        container.restart()
        s.log("Thank you! Please enjoy your new models!")
        input("Press Enter to return")
        
    def uninstall_models(self):
        containers = self.client.containers.list()

        ver_os_info = self.ver_os_info
        client_openai = self.client_openai

        named_docker, container = self.check_for_backend(containers, "ollama-midori-ai-backend")

        if named_docker is None:
            return
        
        s.log("Please check ollamas site for supported models")
        s.log("You can install more than one model by typeing each name with a space")
        model_to_uninstall = input("Type the model(s) you would like to uninstall: ")
        docker_commands = []
        ollama_commands = []
        model_to_uninstall = model_to_uninstall.split()
        for model in model_to_uninstall:
            ollama_commands.append (["ollama", "rm", model])
        docker_commands.extend(ollama_commands)

        # Run a command inside the container
        s.log("Downloading and setting up model into the docker")
        for command in docker_commands:
            s.log(f"Running {command}: ")
            void, stream = container.exec_run(command, stream=True)
            for data in stream:
                s.log(data.decode())

        s.log("All done, I am now rebooting Ollama")
        container.restart()
        input("Press Enter to return")
        
class memgpt_command_line:
    def __init__(self, ver_os_info, client, client_openai):
        self.client = client
        self.ver_os_info = ver_os_info
        self.client_openai = client_openai   

    def check_for_backend(self, containers, docker_name):

        s.log(f"Checking for Docker Image")

        for container in containers:
            s.log(f"Checking Name: {container.name}, ID: {container.id}")

            # Check if there is a container with a name containing `service_name`
            if docker_name in str(container.name):
                # Get the container object
                s.log(f"Found {docker_name}, Linking the Subsystem to: {container.name} / {container.id}")
                container = self.client.containers.get(container.name)
                named_docker = container.name
                s.log(f"Midori AI Subsystem linked to {named_docker}")
                return named_docker, container

        for container in containers:
            print("--------------------------------------")
            s.log(f"Showing Name: {container.name}")
            print("--------------------------------------")

        s.log(f"Switching to manually typed mode, please enter the name of the docker image you are wishing to fork into ({docker_name}).")
        docker_name_manual = input("Enter Docker Image Name: ")

        for container in containers:
            s.log(f"Checking Name: {container.name}, ID: {container.id}")

            # Check if there is a container with a name containing `service_name`
            if docker_name_manual in str(container.name):
                # Get the container object
                s.log(f"Found {docker_name}, Linking the Subsystem to: {container.name} / {container.id}")
                container = self.client.containers.get(container.name)
                named_docker = container.name
                s.log(f"Midori AI Subsystem linked to {named_docker}")

                return named_docker, container

        s.log(f"I could not find {docker_name}... is that installed?")
        input("Press Enter to go back to the menu: ")
        return None, None
    
    def install_via_commandline(self):
        containers = self.client.containers.list()

        named_docker, container = self.check_for_backend(containers, "memgpt_server_midori_ai_backend")

        container_id = container.id

        s.clear_window(self.ver_os_info)
        s.log(f"Installing and Starting MemGPT Config")
        input("Press enter to start the install and config...")
        os.system(f"docker exec -it {container_id} pip install -U pymemgpt")
        os.system(f"docker exec -it {container_id} pip install llama-index-embeddings-huggingface llama-index-llms-huggingface llama-index-core -U")
        os.system(f"docker exec -it {container_id} memgpt configure")
        os.system(f"docker exec -it {container_id} memgpt run --debug --agent demo")

        s.log(f"Leaving the subsystem shell, returning to host os...")
    
    def run_via_commandline(self):
        containers = self.client.containers.list()

        named_docker, container = self.check_for_backend(containers, "memgpt_server_midori_ai_backend")

        container_id = container.id

        s.clear_window(self.ver_os_info)
        s.log(f"Starting MemGPT")
        input("Press enter to start MemGPT commandline chat...")
        os.system(f"docker exec -it {container_id} memgpt run --debug --agent demo")

        s.log(f"Leaving the subsystem shell, returning to host os...")
    

if __name__ == "__main__":
    print("last line of setup_models")