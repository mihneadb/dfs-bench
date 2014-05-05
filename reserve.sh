#!/bin/bash

# $1 - nr of nodes

user=`whoami`

out=`preserve -llist | grep $user | grep node`
if [ $? -ne 0 ]; then
    preserve -1 -# $1 -t 0:10:00
fi

out=`preserve -llist | grep $user | grep node`
while [ $? -ne 0 ]; do
    sleep 1
    out=`preserve -llist | grep $user | grep node`
done

nodes=`echo $out | tr -s [:blank:] ' ' | tr -s ' ' | cut -d ' ' -f 9-1000`

echo "Have nodes: $nodes"
echo "Saving them to './machinefile'."

> machinefile
for node in $nodes; do
    echo $node >> machinefile
done


