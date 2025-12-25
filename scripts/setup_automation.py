#!/usr/bin/env python3
"""
Windows Task Scheduler Setup Helper

Creates Windows Task Scheduler commands for automated collection management.

Usage:
    python scripts/setup_automation.py
    python scripts/setup_automation.py --show-only
"""

import sys
from pathlib import Path
import argparse


def get_python_path() -> str:
    """Get the Python executable path."""
    venv_python = Path(__file__).parent.parent / ".venv" / "Scripts" / "python.exe"
    
    if venv_python.exists():
        return str(venv_python.absolute())
    else:
        return sys.executable


def get_project_path() -> str:
    """Get the project root path."""
    return str(Path(__file__).parent.parent.absolute())


def create_task_command(script_name: str, script_args: str = "", task_name: str = None) -> dict:
    """Create task scheduler command."""
    
    python_exe = get_python_path()
    project_path = get_project_path()
    script_path = f"scripts\\{script_name}"
    
    if not task_name:
        task_name = f"MyManaBox-{script_name.replace('.py', '').replace('_', '-')}"
    
    # PowerShell command to create scheduled task
    ps_command = f'''
$action = New-ScheduledTaskAction -Execute "{python_exe}" -Argument "{script_path} {script_args}" -WorkingDirectory "{project_path}"
$trigger = New-ScheduledTaskTrigger -Daily -At 9:00AM
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive
Register-ScheduledTask -TaskName "{task_name}" -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force
    '''.strip()
    
    return {
        'name': task_name,
        'python': python_exe,
        'script': script_path,
        'args': script_args,
        'working_dir': project_path,
        'ps_command': ps_command
    }


def print_task_info(task: dict, index: int = None):
    """Print task information."""
    
    prefix = f"{index}. " if index else ""
    
    print(f"\n{'=' * 60}")
    print(f"{prefix}Task: {task['name']}")
    print('=' * 60)
    print(f"Python:  {task['python']}")
    print(f"Script:  {task['script']}")
    if task['args']:
        print(f"Args:    {task['args']}")
    print(f"Workdir: {task['working_dir']}")
    print(f"Schedule: Daily at 9:00 AM")
    
    print(f"\nTo create this task, run in PowerShell (as Administrator):")
    print(f"\n{task['ps_command']}")


def print_manual_setup():
    """Print manual Task Scheduler setup instructions."""
    
    python_exe = get_python_path()
    project_path = get_project_path()
    
    print(f"\n{'=' * 60}")
    print("Manual Task Scheduler Setup (Alternative Method)")
    print('=' * 60)
    
    print("""
1. Open Task Scheduler (taskschd.msc)
2. Click "Create Basic Task..."
3. Configure:
   - Name: MyManaBox Daily Enrichment
   - Trigger: Daily at 9:00 AM
   - Action: Start a program
""")
    
    print(f"""   Program/script:  {python_exe}
   Add arguments:   scripts\\auto_enrich.py --backup --quiet
   Start in:        {project_path}
""")
    
    print("""
4. After creation, edit the task:
   - Check "Run whether user is logged on or not"
   - Check "Do not store password"
   - Settings tab:
     ☑ Allow task to be run on demand
     ☑ Run task as soon as possible after scheduled start is missed
     ☑ If task fails, restart every: 1 hour
     ☑ Stop task if it runs longer than: 3 hours
""")


def main():
    """Main entry point."""
    
    parser = argparse.ArgumentParser(
        description="Setup Windows Task Scheduler for automated MyManaBox tasks",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--show-only",
        action="store_true",
        help="Only show commands, don't prompt for creation"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("MyManaBox - Automation Setup Helper")
    print("=" * 60)
    
    # Define automation tasks
    tasks = [
        create_task_command(
            "auto_enrich.py",
            "--backup --quiet",
            "MyManaBox-Daily-Enrichment"
        ),
    ]
    
    # Print task information
    for i, task in enumerate(tasks, 1):
        print_task_info(task, i)
    
    # Print manual setup instructions
    print_manual_setup()
    
    # Print summary
    print(f"\n{'=' * 60}")
    print("Quick Setup Commands")
    print('=' * 60)
    
    print("\n# Copy and paste into PowerShell (Run as Administrator):\n")
    for task in tasks:
        print(f"# {task['name']}")
        print(task['ps_command'])
        print()
    
    print("\n# To verify tasks were created:")
    print("Get-ScheduledTask | Where-Object {$_.TaskName -like 'MyManaBox*'}")
    
    print("\n# To run a task manually:")
    for task in tasks:
        print(f"Start-ScheduledTask -TaskName '{task['name']}'")
    
    print("\n# To remove a task:")
    for task in tasks:
        print(f"Unregister-ScheduledTask -TaskName '{task['name']}' -Confirm:$false")
    
    # Additional automation ideas
    print(f"\n{'=' * 60}")
    print("Additional Automation Ideas")
    print('=' * 60)
    
    print("""
Weekly Price Update:
  Schedule: Weekly on Sunday at 9:00 AM
  Command:  python scripts/auto_enrich.py --backup --quiet

Monthly Backup:
  Schedule: Monthly on 1st at 2:00 AM
  Command:  python scripts/backup_collection.py --archive

Pre-Event Scan:
  Schedule: Before FNM (Friday 5:00 PM)
  Command:  python scripts/export_collection.py --format moxfield

Reminder to Import Mobile Scans:
  Schedule: Daily at 8:00 PM
  Action:   Display notification (use Task Scheduler message)
    """)
    
    print(f"\n{'=' * 60}")
    print("Next Steps")
    print('=' * 60)
    print("""
1. Copy one of the PowerShell commands above
2. Open PowerShell as Administrator
3. Paste and run the command
4. Verify with: Get-ScheduledTask | Where-Object {$_.TaskName -like 'MyManaBox*'}
5. Test with: Start-ScheduledTask -TaskName 'MyManaBox-Daily-Enrichment'
6. Check task history in Task Scheduler to verify it ran successfully

Your collection will now automatically update daily at 9:00 AM!
    """)


if __name__ == "__main__":
    main()
