A Phil Tutorial!
================================
The deploy script will clone/pull a git repository which contains the source code and `environment.yml`.
It will also setup/update an environment according to the `.yml` file.
Additionally, the script will kill existing gunicorn processes and run the application as daemon process.

**Running the deploy script if you are not the Phil team or Diane Woodbridge:**

1. Create an IAM User with permissions for EC2. Login to the IAM User.

2. Launch an EC2

  - Assumes the following:
      - EC2 has anaconda, git, git credentials, and postgres installed
      - at the root of your directory, you have your db password stored in the file `rds_key`, and the `google_key` file

  - Edit the inbound rules for the EC2:
      - add the db's (in our case, the RDS) security group with port 5432 opened
      - open port 8080 to all IP address (so users can access the website)

3. Launch your db (in our case, the RDS)

  - Add EC2's security group with port 5432 opened

4. Edit the `user_definitions.py`

  - Edit ec2_address and key_file to your EC2 address and your local `.pem` file path, respectively

5. Run the `deploy.py` on your local. Application will be running on your <EC2 PUBLIC IP>:8080



**Running the deploy script if you are Diane Woodbridge:**

1. Login to IAM User provided to you

2. Start the EC2 named `ec2-everyone`

3. Edit the `user_definitions.py` variables:

    - Change the ec2_address to the EC2's Public DNS
    - Change the `key_file` to the location of the `phil_key_everyone.pem` file we provided
    - The EC2 already has git configuration, so no need to edit `git_user_id`

4. Run `deploy.py` locally-- Application will be running on your <EC2 PUBLIC IP>:8080
