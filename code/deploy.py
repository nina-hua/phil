import paramiko
from os.path import expanduser
from user_definition import *


# ## Assumption : Anaconda, Git (configured)

def ssh_client():
    """Return ssh client object"""
    return paramiko.SSHClient()


def ssh_connection(ssh, ec2_address, user, key_file):
    """Connect to an SSH server and authenticate """
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ec2_address, username=user,
                key_filename=expanduser("~") + key_file)
    return ssh


def create_or_update_environment(ssh):
    """Create environment if non-existent,
    otherwise update the environment using the .yml file"""
    stdin, stdout, stderr = \
        ssh.exec_command("conda env create -f "
                         "~/" + git_repo_name + "/environment.yml")
    if (b'already exists' in stderr.read()):
        stdin, stdout, stderr = \
            ssh.exec_command("conda env update -f "
                             "~/" + git_repo_name + "/environment.yml")


def git_clone(ssh):
    """Clone a git repository - defined in user_definition.py"""
    stdin, stdout, stderr = ssh.exec_command("git --version")
    if (b"" is stderr.read()):
        # for a classroom repo
        git_clone_command = "git clone https://" + \
                            git_user_id + "@github.com/" + \
                            git_repo_owner + "/" + git_repo_name + ".git"

        # for a regular repo
        # git_clone_command = "git clone https://github.com/" + \
        #                     git_user_id + "/" + git_repo_name + ".git"

        stdin, stdout, stderr = ssh.exec_command(git_clone_command)

        if (b'already exists' in stderr.read()):
            git_pull_command = "git -C /home/ec2-user/" \
                               + git_repo_name + " pull"
            stdin, stdout, stderr = ssh.exec_command(git_pull_command)


def set_crontab(ssh):
    """set a crontab to run google_search.py and event_brite.py every minute"""
    stdin, stdout, stderr = ssh.exec_command("crontab -r")  # remove crobtab

    # run google once a month
    google_cron = "0 0 1 * * ~/.conda/envs/phil/bin/python " + \
        "/home/ec2-user/" + git_repo_name + "/code/api/google_search.py"

    # run eventbrite once a week
    eventbrite_cron = "0 0 * * 0 ~/.conda/envs/phil/bin/python" + \
        "/home/ec2-user/" + git_repo_name + "/code/api/eventbrite_search.py"

    cronline = google_cron + '\n' + eventbrite_cron
    stdin, stdout, stderr = ssh.exec_command("crontab -l | { cat; echo \""
                                             + cronline + "\"; } | crontab -")


def run_app(ssh):
    """1. kill existing gunicorn processes
    2. make daemon bash script executable
    3. run app as daemon process
    4. print app's port number"""
    # kill all old gunicorns
    kill_command = 'pkill -f gunicorn'
    stdin, stdout, stderr = ssh.exec_command(kill_command)

    # make bash file executable
    make_executable = "chmod +x " + git_repo_name + "/run_daemon.sh"
    stdin, stdout, stderr = ssh.exec_command(make_executable)

    # run flask app as daemon (on port 8080)
    execute = git_repo_name + "/run_daemon.sh"
    stdin, stdout, stderr = ssh.exec_command(execute)

    print(8080)  # app running on port 8080


def main():
    """Implement ssh protocol to connect remotely to amazon server"""
    ssh = ssh_client()
    ssh_connection(ssh, ec2_address, user, key_file)
    git_clone(ssh)
    create_or_update_environment(ssh)
    set_crontab(ssh)
    run_app(ssh)
    ssh.close()  # logout


if __name__ == '__main__':
    main()
