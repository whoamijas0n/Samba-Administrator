# Samba Administrator 

A command-line interface (CLI) administration tool designed to simplify routine system resource monitoring and Samba server management on Linux systems.

## Overview

This Bash script provides an interactive menu-driven interface that allows system administrators to quickly check system health, monitor active Samba connections, manage Samba user access, control shared directory permissions, and safely control the Samba daemon

## Requirements

- **Operating System:** Linux (Debian or compatible distributions)
- **Shell:** Bash 4.0 or later
- **Samba:** Package `samba` installed and configured (`smbd`, `nmbd`)
- **Privileges:** Root or `sudo` access is required for most operations
- **Dependencies:** The following system utilities must be available in `$PATH`:

---

## Installation

1. Clone or download the repository to the target server:

```bash
git clone https://github.com/whoamijas0n/samba-administrator.git
cd samba-administrator
```

2. Grant execution permissions to the script:

```bash
chmod +x sysadmin.sh
```

3. Run the script as root or with elevated privileges:

```bash
sudo ./sysadmin.sh
```

---

## Usage

Upon execution, the script presents an interactive main menu with the following options:

```
[1] Resource Monitoring (CPU, RAM, Disk)
[2] Samba Connection Monitoring (smbstatus)
[3] Access Administration (Create/Delete Users)
[4] Directory Permissions Administration
[5] Samba Service Status and Control
[6] Exit
```

Navigate by entering the number corresponding to the desired module and pressing `Enter`. Each module returns to the main menu after execution.

---

## Module Reference

### 1. Resource Monitoring

Displays a snapshot of current system resource consumption, including:

- **RAM usage** — output from `free -h`, showing total, used, free, and available memory.
- **Disk space** — output from `df -h`, filtered to show only physical and logical block devices.
- **Top 5 CPU processes** — sorted by CPU usage, displaying PID, parent PID, command, memory percentage, and CPU percentage.

No user input is required beyond pressing `Enter` to return.

---

### 2. Samba Connection Monitoring

Executes `smbstatus` to display the current state of the Samba server, including:

- Active client connections with usernames, IP addresses, and session details.
- Files currently locked by connected clients.
- Share access information.

This module is read-only and does not modify any system state.

---

### 3. Access Administration

Provides a sub-menu for managing Samba user accounts:

| Option | Action | Command Used |
|---|---|---|
| 1 | List registered Samba users | `pdbedit -L -v` |
| 2 | Add a new Samba user | `smbpasswd -a <username>` |
| 3 | Delete an existing Samba user | `smbpasswd -x <username>` |
| 4 | Return to main menu | — |

> **Note:** When adding a user, the corresponding Linux system account must already exist. `smbpasswd` maps Samba credentials to an existing OS user. Creating a new system user is outside the scope of this script.

---

### 4. Directory Permissions Administration

Allows the administrator to inspect and modify the ownership and permissions of a shared directory.

**Workflow:**

1. Enter the absolute path to the shared folder (e.g., `/srv/samba/shared`).
2. The script verifies the path exists and displays the current owner, group, and permissions using `ls -ld`.
3. Choose a modification action:

| Option | Action | Command Used |
|---|---|---|
| 1 | Change owner and group | `chown -R <owner>:<group> <path>` |
| 2 | Change permissions | `chmod -R <octal> <path>` |
| 3 | Exit without changes | — |

> **Warning:** Both `chown` and `chmod` are applied recursively with the `-R` flag. Exercise caution when targeting directories with a large number of subdirectories or files, as this operation cannot be automatically undone.

---

### 5. Samba Service Status and Control

Displays the current status of the `smbd` service (limited to the first 15 lines of `systemctl status` output) and offers a controlled restart option.

**Restart behavior:**

Before restarting, the script validates the Samba configuration file using `testparm -s`. The restart proceeds only if no syntax errors are detected. If the configuration is invalid, the service is not restarted in order to prevent unplanned downtime.

On a successful validation, both `smbd` and `nmbd` are restarted:

```bash
systemctl restart smbd nmbd
```

---

## Security Considerations

- This script must be executed with root privileges. Restrict access to the script file and the directory it resides in to prevent unauthorized execution.
- User input passed to `smbpasswd`, `chown`, and `chmod` is not sanitized. Avoid using this script in environments where the terminal may be accessed by untrusted parties.
- Recursive permission changes (`chown -R`, `chmod -R`) are irreversible without prior backup of ownership and mode metadata. Always verify the target path before confirming changes.
- Samba credentials and session data displayed by `smbstatus` and `pdbedit` may be sensitive. Ensure the terminal session is secured and access-logged in production environments.



