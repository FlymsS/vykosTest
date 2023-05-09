#sftp -i ./clavessh user@8.8.8.8:/home/vinkOS/archivosVisitas <<EOF
#get report*.txt ./uncleanedFiles
#rm report*.txt
#EOF

#exit

python3 ./src/cleaning.py

zip ~/etl/visitas/bckp/$(date -I).zip ./uncleanedFiles/*.txt
rm ./uncleanedFiles/*.txt