#SBATCH --job-name=olympus2scratch_test
#SBATCH --nodes=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8GB
#SBATCH --time=6:00:00

# make is so that all new files created in 
# olympus have the smapp group
chmod g+s /scratch/olympus

# set all files already in olympus
# to have the smapp group
chown -R $USER:smapp * .[^.]*

# update the permissions to rwxr-x--- for all files and folders
# inside olympus recursively, this is rwx for user and r-x for
# the gourp which should be smapp
find /scratch/olympus -type d -exec chmod -R 750 {} \;
find /scratch/olympus -type f -exec chmod -R  750 {} \;

# author @yvan
# sets all permissions on directories to rwxr-x---
# sets all permissions on files rwxr-x--
# also make sure all files are owned by the smapp group
# https://superuser.com/questions/102253/how-to-make-files-created-in-a-directory-owned-by-directory-group