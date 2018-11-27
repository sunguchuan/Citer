#!/bin/bash
i=0
j=0
h=0
k=0
# Generate and register nodes
for (( i = 0 ; i < $1 ; i = i + 1 ))
do
  echo "#!/bin/bash" >> tmp.sh
  echo "cd /Users/user/Desktop/sgc/Project/Data/code" >> tmp.sh
  j=`expr $i + 5000`
  echo "python3 project.py -p $j" >> tmp.sh
  open -a Terminal ./tmp.sh
  sleep 1
  echo "" > tmp.sh
done

# Generate an authority node
# echo "#!/bin/bash" >> tmp.sh
# echo "cd /Users/user/Desktop/sgc/Project/Data/code" >> tmp.sh
# echo "python3 authority.py -p 6000" >> tmp.sh
# open -a Terminal ./tmp.sh
# sleep 1
# echo "" > tmp.sh

# Generate a security node
# echo "#!/bin/bash" >> tmp.sh
# echo "cd /Users/user/Desktop/sgc/Project/Data/code" >> tmp.sh
# echo "python3 security.py -p 7000" >> tmp.sh
# open -a Terminal ./tmp.sh
# sleep 1
# echo "" > tmp.sh

for ((i = 0 ; i < $1 ; i = i + 1))
do
  h=`expr $i + 5000`
  for ((j = `expr $i + 1` ; j < $1 ; j = j + 1))
  do
    k=`expr $j + 5000`
    Curl -X POST -H "Content-Type:application/json" -d '{"nodes":["http://localhost:'$k'/"]}' "http://localhost:$h/nodes/register"
  done
done


# sleep 15
#
# for (( i = 1 ; i < 5 ; i = i + 1 ))
# do
#   j=`expr 2 \* $i`
#   curl -X POST -H "Content-Type:application/json" -d '{"image": "pic'$j'.png", "govpri": "govpri.pem", "user_pubkey": "pubkey'$j'.pub","node":"localhost:500'$i'"}' "http://localhost:6000/hsign"
#   # k=`expr 5000 + $i`
#   # curl -X POST -H "Content-Type:application/json" -d '{"pubkey":"/Users/user/Desktop/sgc/Project/Data/code/test/pubkey'$j'.pub", "info":"/Users/user/Desktop/sgc/Project/Data/code/test/info'$j'.txt", "govsig": "/Users/user/Desktop/sgc/Project/Data/code/test/fromgov'$j'.bin"}' "http://localhost:500$i/data/new"
#
#   # sleep 30
#
#   j=`expr $j + 1`
#   curl -X POST -H "Content-Type:application/json" -d '{"image": "pic'$j'.png", "govpri": "govpri.pem", "user_pubkey": "pubkey'$j'.pub","node":"localhost:500'$i'"}' "http://localhost:6000/hsign"
#   # curl -X POST -H "Content-Type:application/json" -d '{"pubkey":"/Users/user/Desktop/sgc/Project/Data/code/test/pubkey'$j'.pub", "info":"/Users/user/Desktop/sgc/Project/Data/code/test/info'$j'.txt", "govsig": "/Users/user/Desktop/sgc/Project/Data/code/test/fromgov'$j'.bin"}' "http://localhost:500$i/data/new"
# done
