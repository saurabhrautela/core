
files=(celery_broker_password.txt celery_broker_username.txt email_password.txt email_username.txt pdb_password.txt pdb_username.txt secret_key.txt)

for file in "${files[@]}"
do
    touch "$file"
done
