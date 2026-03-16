#!/bin/bash

# Function to pause and wait for the user
pause_script() {
    echo ""
    read -p "[-] Press [Enter] to continue..."
}

# 1. Resource Monitoring (CPU, RAM, Disk)
resource_monitoring() {
    clear
cat << "EOF"
                 _________
                / ======= \
               / __________\
              | ___________ |
              | | -       | |
              | |         | |
              | |_________| |__________________
              \=____________/                  )
              / """"""""""" \                 /
             / ::::::::::::: \            =D-'
            (_________________)

EOF

    echo "[-] RESOURCE MONITORING (CPU, RAM, Storage)"
    echo ""
    echo "[-] RAM Memory Usage:"
    free -h
    echo ""
    echo "[-] Disk Space (Main folders):"
    df -h | grep -E '^/dev|Filesystem'
    echo ""
    echo "[-] Top 5 CPU Consuming Processes:"
    ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%cpu | head -n 6
    pause_script
}

# 2. Samba System Monitoring (Connections and Files)
samba_monitoring() {
    clear
    
cat << "EOF"
                  /\                 /\
                 / \'._   (\_/)   _.'/ \
                 |.''._'--(o.o)--'_.''.|
                  \_ / `;=/ " \=;` \ _/
                    `\__| \___/ |__/`
                        \(_|_)/
                         " ` "

EOF
    echo "[-] CONNECTION STATUS AND LOCKED FILES (Samba)"
    echo ""
    echo "[-] This command shows who is connected and which files are in use."
    echo ""
    smbstatus
    pause_script
}

# 3. Access Administration (Samba Users)
access_administration() {
    clear
cat << "EOF"
                  |\      _,,,---,,_
             ZZZzz /,`.-'`'     -.  ;-;;,_
                  |,4-  ) )-,_. ,\ (  `'-'
                 '---''(_/--'  `-'\_)  

EOF

    echo "[-] SAMBA USER ADMINISTRATION"
    echo ""
    echo "[1] List current users (pdbedit)"
    echo "[2] Add a new user (smbpasswd)"
    echo "[3] Delete a user (smbpasswd)"
    echo "[4] Back to main menu"
    echo ""
    read -p "[-] Select an option: " sub_option

    case $sub_option in
        1)
            echo "Users registered in Samba:"
            pdbedit -L -v | grep -E 'Unix username|Account desc'
            ;;
        2)
            read -p "Enter the username (must exist in the Linux system): " new_user
            smbpasswd -a $new_user
            ;;
        3)
            read -p "Enter the name of the user to delete from Samba: " del_user
            smbpasswd -x $del_user
            ;;
        *)
            ;;
    esac
    pause_script
}

# 4. Permission Control in Shared Folders
permission_administration() {
    clear
cat << "EOF"
                    -=====-                         -=====-
                     _..._                           _..._
                   .~     `~.                     .~`     ~.
           ,_     /           }                   {          \     _,
          ,_\'--, \   _.'`~~/                     \~~`'._   / ,--'/_,
           \'--,_`{_,}    -(                       )-    {,_}`_,--'/
            '.`-.`\;--,___.'_                     _'.___,--;/`.-`.'
              '._`/    |_ _{@}                   {@}_ _|    \`_.'
                 /     ` |-';/             _      \;'-| `     \
                /   \    /  |       _   {@}_      |  \    /   \
               /     '--;_       _ {@}  _Y{@}        _;--'     \
              _\          `\    {@}\Y/_{@} Y/      /`          /_
             / |`-.___.    /    \Y/\|{@}Y/\|//     \    .___,-'| \
   ^^---^^`--`------'`--`^^^^^^^^^^^^^^^^^^^^^^^^^`--`'------`--`^^^^^^^

EOF
    echo "[-] PERMISSIONS AND OWNERSHIP CONTROL"
    echo ""
    read -p "[-] Enter the absolute path of the shared folder (e.g., /srv/samba/shared): " folder_path
    
    if [ -d "$folder_path" ]; then
        echo ""
        echo "[-] Current permissions for $folder_path:"
        ls -ld $folder_path
        echo ""
        echo "[-] Modification options:"
        echo "[1] Change owner and group (chown)"
        echo "[2] Change read/write permissions (chmod)"
        echo "[3] Exit without changes"
        echo ""
        read -p "[-] Select an action: " permission_action

        case $permission_action in
            1)
                read -p "Enter the new Owner:Group (e.g., root:smbgroup): " new_owner
                chown -R $new_owner $folder_path
                echo "Owner updated."
                ;;
            2)
                read -p "Enter permissions in octal format (e.g., 775 or 777): " new_permissions
                chmod -R $new_permissions $folder_path
                echo "Permissions updated."
                ;;
            *)
                echo "No changes were made."
                ;;
        esac
    else
        echo "Error: The directory $folder_path does not exist."
    fi
    pause_script
}

# 5. Base Service Monitoring
service_monitoring() {
    clear
cat << "EOF"
                        __
             ..=====.. |==|
             ||     || |= |
          _  ||     || |^*| _
         |=| o=,===,=o |__||=|
         |_|  _______)~`)  |_|
             [=======]  ()       ldb

EOF
    echo "[-] SAMBA SERVICE STATUS (smbd)"
    systemctl status smbd --no-pager | head -n 15
    echo ""
    echo "[-] Service options:"
    echo ""
    echo "[1] Restart Samba (apply changes in smb.conf)"
    echo "[2] Back to menu"
    echo ""
    read -p "[-] Option: " service_option

    if [ "$service_option" == "1" ]; then
        echo "Checking smb.conf syntax before restarting..."
        testparm -s > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            systemctl restart smbd nmbd
            echo "Samba restarted successfully."
        else
            echo "Error in smb.conf. The service will not be restarted to avoid downtime."
        fi
    fi
    pause_script
}

# =========================================================================
# Main Menu Loop
# =========================================================================
while true; do
    clear

cat << "EOF"
             _____                 _                          
            /  ___|               | |                         
            \ `--.  __ _ _ __ ___ | |__   __ _                 
             `--. \/ _` | '_ ` _ \| '_ \ / _` |                
            /\__/ / (_| | | | | | | |_) | (_| |                
            \____/ \__,_|_| |_| |_|_.__/ \__,_|                
                                                                    
                                                                    
  ___      _           _       _     _             _             
 / _ \    | |         (_)     (_)   | |           | |            
/ /_\ \ __| |_ __ ___  _ _ __  _ ___| |_ _ __ __ _| |_ ___  _ __ 
|  _  |/ _` | '_ ` _ \| | '_ \| / __| __| '__/ _` | __/ _ \| '__|
| | | | (_| | | | | | | | | | | \__ \ |_| | | (_| | || (_) | |   
\_| |_/\__,_|_| |_| |_|_|_| |_|_|___/\__|_|  \__,_|\__\___/|_|   

EOF

echo -e "\033[33m                         welcome again! $USER\033[0m"
echo ""
echo "[-] Created by:              |         N0kyapi (whoamijas0n)"
echo "[-] Version:                 |         1.0.0"
echo "[-] Github:                  |         https://github.com/whoamijas0n"
echo ""

    echo "[1] Resource Monitoring (CPU, RAM, Disk)"
    echo "[2] Samba Connection Monitoring (smbstatus)"
    echo "[3] Access Administration (Create/Delete Users)"
    echo "[4] Directory Permissions Administration"
    echo "[5] Samba Service Status and Control"
    echo "[6] Exit"
    echo ""
    read -p "[-] Select an option [1-6]: " option

    case $option in
        1) resource_monitoring ;;
        2) samba_monitoring ;;
        3) access_administration ;;
        4) permission_administration ;;
        5) service_monitoring ;;
        6) echo "[-] Exiting administrator. See you soon!"; exit 0 ;;
        *) echo "[-] Invalid option. Please try again."; sleep 2 ;;
    esac
done