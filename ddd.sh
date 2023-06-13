#!/bin/bash

# Dashed Droplet Manager
container=
help () {
    echo;
    echo;
    echo "    __                        __                           ";
    echo "    ) ) _   _ ( _   _   _ )   ) ) _ _   _   )  _  _)_ _    ";
    echo "   /_/ (_( (   ) ) )_) (_(   /_/ ) (_) )_) (  )_) (_ (     ";
    echo "           _)     (_                  (      (_      _)    ";
    echo;
    echo;
    echo "This is the CLI tool to manage your Droplets, but works for all docker containers.";
    echo;
    echo "To get started, try any of the following parameters:";
    echo "     -c | --check <container>         This will tell you if your droplet is running or not.";
    echo "     -s | --start <container>         This will start your droplet - and all it's processes.";
    echo "     -d | --stop <container>          This will turn off your droplet.";
    echo "     -r | --restart <container>       This will restart your droplet and all it's processes.";
    echo "     -n | --new <container> <type>    This will create a new droplet with the name and hostname <container>, and type <type>.";
    echo "                            [ apache2 | ubuntu ]";
    echo "     -i | --ips                       This will list all containers and their corresponding ip addressess (local network only).";
    echo "    -ip | --ip <container>            This will return the ip address of a specific droplet."
    echo "     -b | --backup <container>        This will backup your droplet in a snapshot style.";
    echo "     -h | --help                      This displays this help prompt.";
    echo "     -a | --all                       list all the container names only with there images"
    echo "     -at | --alltime                  list all the container names only with there images and time "
    echo;
    echo;
    echo;
    echo;
    echo;
    echo;
    echo;
}

check () {
    if [ "$( docker container inspect -f '{{.State.Status}}' $container )" == "running" ]; then
        echo "True"
    else
        echo "False"
    fi
}
create () {
    if [ $type == "ubuntu" ]; then
        docker run --restart unless-stopped -d --name $container -h $container onionz/ubuntu:latest sleep infinity;
        docker exec -it $container bash ddrun;
    else
	# read -p "Enter the port number to map: " port_number
	# read -p "Enter the first port number to map: " second_port
	# read -p "Enter the second port number to map: " ssh_port
        docker create --restart unless-stopped -p $port_number:80 -p $second_port:7662 -p $ssh_port:22 --name $container -h $container kooljool/droplet:latest;
        docker start $container;
        docker exec -it $container /bin/bash /usr/bin/ddrun;
    fi
    echo "Created "$container
}

backup () {
    docker stop $container;
    test=$( sudo docker images -q onionz/backups:$container );
    if [[ -n "$test" ]]; then
        docker rmi onionz/backups:$container;
    fi
    docker commit $container onionz/backups:$container;
    docker push onionz/backups:$container;
    docker rmi onionz/backups:$container;
    docker start $container;
    docker exec -it $container /bin/bash /usr/bin/ddrun
    echo "Backed up "$container
}

start_container () {
    docker start $container;
    docker exec -it $container /bin/bash /usr/bin/ddrun
    echo "Started "$container
}

stop_container () {
    docker stop $container;
    echo "Stopped "$container
}

restart_container () {
    docker stop $container;
    docker start $container;
    docker exec -it $container /bin/bash /usr/bin/ddrun
    echo "Restarted "$container
}

list_ips () {
    docker ps | awk 'NR>1{ print $1 }' | xargs docker inspect -f '{{range .NetworkSettings.Networks}}{{$.Name}}{{" "}}{{.IPAddress}}{{end}}';
}

list_ip () {
    docker inspect -f '{{ .NetworkSettings.IPAddress }}' $container;
}

usage () {
    echo "usage: ddd [[[-c | --check] | [-s | --start] | [-d | --stop] | [-r | --restart] | [-n | --new] | [-b | --backup]] <container> (<type>)?]  | [-h | --help]]"
}

while [ "$1" != "" ]; do
    case $1 in
        -c | --check )          shift
                                container="$1"
                                check
                                ;;
        -n | --new )            shift
                                container="$1"
                                shift
                                type=${1:-"null"}
                                shift
                                $port_number="$3"
                                $second_port="$4"
                                $ssh_port="$5"
                                create
                                ;;
        -s | --start )          shift
                                container="$1"
                                start_container
                                ;;
        -d | --stop )           shift
                                container="$1"
                                stop_container
                                ;;
        -r | --restart )        shift
                                container="$1"
                                restart_container
                                ;;
        -i | --ips  )           shift
                                list_ips
                                ;;
        -ip | --ip  )           shift
                                container="$1"
                                list_ip
                                ;; 
       -b | --backup )         shift
                                container="$1"
                                backup
                                ;;
       -a | --all )         	shift
                                docker ps -a --format "table {{.Names}}\t{{.Image}}"
                                ;;
       -at | --alltime )         shift
                               docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.RunningFor}}"
                                
                                ;;
        -h | --help )           help
                                exit
                                ;;
        * )                     usage
                                exit 1
    esac
    shift
done
