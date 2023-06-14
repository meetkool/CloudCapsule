#!/usr/bin/env python3

import subprocess
import sys

def display_help():
    help_banner = """
        __                        __                           
        ) ) _   _ ( _   _   _ )   ) ) _ _   _   )  _  _)_ _    
       /_/ (_( (   ) ) )_) (_(   /_/ ) (_) )_) (  )_) (_ (     
               _)     (_                  (      (_      _)    

    This is the CLI tool to manage your Droplets, but works for all docker containers.

    To get started, try any of the following parameters:
         -c | --check <container>         This will tell you if your droplet is running or not.
         -s | --start <container>         This will start your droplet - and all its processes.
         -d | --stop <container>          This will turn off your droplet.
         -r | --restart <container>       This will restart your droplet and all its processes.
         -n | --new <container> <type>    This will create a new droplet with the name and hostname <container>, and type <type>.
                                            [ apache2 | ubuntu ]
         -i | --ips                       This will list all containers and their corresponding IP addresses (local network only).
        -ip | --ip <container>            This will return the IP address of a specific droplet.
         -b | --backup <container>        This will backup your droplet in a snapshot style.
         -h | --help                      This displays this help prompt.
         -a | --all                       List all the container names only with their images.
        -at | --alltime                   List all the container names only with their images and time.
    """
    print(help_banner)

def run_command(command):
    try:
        return subprocess.check_output(command, shell=True).decode().strip()
    except subprocess.CalledProcessError as e:
        return str(e)


def check_container(container):
    status = run_command(f"docker container inspect -f '{{{{.State.Status}}}}' {container}")
    return "True" if status == "running" else "False"


# def create_container(container, container_type, port_number, second_port, ssh_port):
#     if container_type == "ubuntu":
#         run_command(f"docker run --restart unless-stopped -d --name {container} -h {container} onionz/ubuntu:latest sleep infinity")
#         run_command(f"docker exec -it {container} bash ddrun")
#     else:
#         run_command(f"docker create --restart unless-stopped -p {port_number}:80 -p {second_port}:7662 -p {ssh_port}:22 --name {container} -h {container} kooljool/droplet:latest")
#         run_command(f"docker start {container}")
#         run_command(f"docker exec -it {container} /bin/bash /usr/bin/ddrun")
#     return f"Created {container}"


def create_container(container, container_type, port_number, second_port, ssh_port):
    results = []

    if container_type == "ubuntu":
        result1 = run_command(f"docker run --restart unless-stopped -d --name {container} -h {container} onionz/ubuntu:latest sleep infinity")
        result2 = run_command(f"docker exec -it {container} bash ddrun")
        results.append(result1)
        results.append(result2)
    else:
        result1 = run_command(f"docker create --restart unless-stopped -p {port_number}:80 -p {second_port}:7662 -p {ssh_port}:22 --name {container} -h {container} kooljool/droplet:latest")
        result2 = run_command(f"docker start {container}")
        result3 = run_command(f"bash -c './dockerrun {container}' ")
        link = run_command(f"docker exec {container} cat /var/www/dump/files.hostname")
        result4 = f"{link}/info.server.php"
        # results.append(result1)
        # results.append(result2)
        results.append(result4)
    
    results.append(f"Created {container}")
    return "\n".join(results)

def get_link(container):
    link = run_command(f"docker exec {container} cat /var/www/dump/files.hostname")
    return f"{link}/info.server.php"

def backup_container(container):
    run_command(f"docker stop {container}")
    image_exist = run_command(f"docker images -q onionz/backups:{container}")
    if image_exist:
        run_command(f"docker rmi onionz/backups:{container}")
    run_command(f"docker commit {container} onionz/backups:{container}")
    run_command(f"docker push onionz/backups:{container}")
    run_command(f"docker rmi onionz/backups:{container}")
    run_command(f"docker start {container}")
    run_command(f"docker exec -it {container} /bin/bash /usr/bin/ddrun")
    print(f"Backed up {container}")


def delete_container(container):
    run_command(f"docker stop {container}")
    run_command(f"docker rm {container}")
    print(f"Started {container}")    


def start_container(container):
    run_command(f"docker start {container}")
    run_command(f"docker exec -it {container} /bin/bash /usr/bin/ddrun")
    print(f"Started {container}")


def stop_container(container):
    run_command(f"docker stop {container}")
    print(f"Stopped {container}")


def restart_container(container):
    run_command(f"docker stop {container}")
    run_command(f"docker start {container}")
    run_command(f"docker exec -it {container} /bin/bash /usr/bin/ddrun")
    print(f"Restarted {container}")


def list_ips():
    return run_command("docker ps | awk 'NR>1{ print $1 }' | xargs docker inspect -f '{{range .NetworkSettings.Networks}}{{$.Name}}{{\" \"}}{{.IPAddress}}{{end}}'")


def list_ip(container):
    return run_command(f"docker inspect -f '{{{{ .NetworkSettings.IPAddress }}}}' {container}")


def list_all():
    return run_command("docker ps -a --format 'table {{.Names}}\t{{.Image}}'")


def list_alltime():
    return run_command("docker ps -a --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.RunningFor}}'")


def main():
    args = sys.argv[1:]
    while args:
        arg = args.pop(0)
        if arg in ['-c', '--check']:
            container = args.pop(0)
            print(check_container(container))
        elif arg in ['-n', '--new']:
            container = args.pop(0)
            container_type = args.pop(0)
            port_number = args.pop(0)
            second_port = args.pop(0)
            ssh_port = args.pop(0)
            print(create_container(container, container_type, port_number, second_port, ssh_port))  # add print statement here

        elif arg in ['-s', '--start']:
            container = args.pop(0)
            start_container(container)
        elif arg in ['-d', '--stop']:
            container = args.pop(0)
            stop_container(container)
        elif arg in ['-r', '--restart']:
            container = args.pop(0)
            restart_container(container)
        elif arg in ['-i', '--ips']:
            print(list_ips())
        elif arg in ['-ip', '--ip']:
            container = args.pop(0)
            print(list_ip(container))
        elif arg in ['-b', '--backup']:
            container = args.pop(0)
            backup_container(container)
        elif arg in ['-a', '--all']:
            print(list_all())
        elif arg in ['-at', '--alltime']:
            print(list_alltime())
        elif arg in ['-h', '--help']:
            display_help()
        else:
            print("Invalid argument. Please check the command-line arguments and try again.")
            sys.exit(1)

if __name__ == '__main__':
    main()
