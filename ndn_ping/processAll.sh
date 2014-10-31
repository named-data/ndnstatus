#!/bin/bash


if [ $# -ne 1 ]
then
  echo "Usage: $0 <logfile name>"
  echo " e.g.: $0 ndnping.log.export"
  exit 0
else
  LOGFILE=$1
fi
NODENAME=`grep "Node:" $LOGFILE | cut -d':' -f 2`

PREFIXES=(`grep "Ping Statistics For " $LOGFILE | cut -d' ' -f 6`)

PACKET_LOSS=(`grep "Packet Loss" $LOGFILE | cut -d',' -f 3 | cut -d'=' -f 2 | cut -d'%' -f 1`)

MIN=(`grep "Min" $LOGFILE | cut -d'(' -f 3 | cut -d')' -f 1 | cut -d'/' -f 1`)
MAX=(`grep "Min" $LOGFILE | cut -d'(' -f 3 | cut -d')' -f 1 | cut -d'/' -f 2`)
AVG=(`grep "Min" $LOGFILE | cut -d'(' -f 3 | cut -d')' -f 1 | cut -d'/' -f 3`)
MDEV=(`grep "Min" $LOGFILE | cut -d'(' -f 3 | cut -d')' -f 1 | cut -d'/' -f 4`)

echo "NODENAME $NODENAME"
#echo "PREFIXES: $PREFIXES"
#echo "PACKET_LOSS: $PACKET_LOSS"

NUM_PREFIXES=${#PREFIXES[@]}
NUM_PACKET_LOSS=${#PACKET_LOSS[@]}
echo "NUM_PREFIXES=$NUM_PREFIXES"
echo "NUM_PACKET_LOSS=$NUM_PACKET_LOSS"

NUM_MIN=${#MIN[@]}
echo "NUM_MIN=$NUM_MIN"

if [ $NUM_PREFIXES -ne $NUM_PACKET_LOSS ]
then
  echo "something went wrong. NUM_PREFIXES=$NUM_PREFIXES NUM_PACKET_LOSS=$NUM_PACKET_LOSS"
  exit 0
fi

i=0
skip=0
while [ $i -lt $NUM_PREFIXES ]
do
  echo -n "$NODENAME ${PREFIXES[i]} ${PACKET_LOSS[i]}"
  if [ ${PACKET_LOSS[i]} == 100 ]
  then
    skip=$((skip+1))
    echo " 0 0 0 0 "
  else
    echo " ${MIN[i-skip]} ${MAX[i-skip]} ${AVG[i-skip]} ${MDEV[i-skip]} "
  fi

  i=$(($i+1))
done
