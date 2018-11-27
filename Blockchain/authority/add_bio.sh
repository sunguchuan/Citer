#!/bin/bash
#Add transactions, 9 in total
curl -X POST -H "Content-Type:application/json" -d '{"image": "pic1.png", "govpri": "govpri.pem", "user_pubkey": "public.pub","node":"localhost:5000"}' "http://localhost:6000/hsign"
# curl -X POST -H "Content-Type:application/json" -d '{"pubkey":"/Users/user/Desktop/sgc/Project/Data/code/test/public.pub", "info":"/Users/user/Desktop/sgc/Project/Data/code/test/info1.txt", "govsig": "/Users/user/Desktop/sgc/Project/Data/code/test/fromgov1.bin"}' "http://localhost:5000/data/new"
#
#
for (( i = 1 ; i < 5 ; i = i + 1 ))
do
  j=`expr 2 \* $i`
  k=`expr 5000 + $i`
  curl -X POST -H "Content-Type:application/json" -d '{"image": "pic'$j'.png", "govpri": "govpri.pem", "user_pubkey": "pubkey'$j'.pub","node":"localhost:'$k'"}' "http://localhost:6000/hsign"
  # k=`expr 5000 + $i`
  # curl -X POST -H "Content-Type:application/json" -d '{"pubkey":"/Users/user/Desktop/sgc/Project/Data/code/test/pubkey'$j'.pub", "info":"/Users/user/Desktop/sgc/Project/Data/code/test/info'$j'.txt", "govsig": "/Users/user/Desktop/sgc/Project/Data/code/test/fromgov'$j'.bin"}' "http://localhost:500$i/data/new"

  # sleep 30

  j=`expr $j + 1`
  curl -X POST -H "Content-Type:application/json" -d '{"image": "pic'$j'.png", "govpri": "govpri.pem", "user_pubkey": "pubkey'$j'.pub","node":"localhost:'$k'"}' "http://localhost:6000/hsign"
  # curl -X POST -H "Content-Type:application/json" -d '{"pubkey":"/Users/user/Desktop/sgc/Project/Data/code/test/pubkey'$j'.pub", "info":"/Users/user/Desktop/sgc/Project/Data/code/test/info'$j'.txt", "govsig": "/Users/user/Desktop/sgc/Project/Data/code/test/fromgov'$j'.bin"}' "http://localhost:500$i/data/new"
done
