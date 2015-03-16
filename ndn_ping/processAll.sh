#!/bin/bash


#ALL_FILES="ping_wu.raw ping_memphis.raw ping_michigan.raw ping_csu.raw ping_ucla.raw ping_arizona.raw ping_remap.raw ping_uiuc.raw ping_uci.raw ping_caida.raw ping_pku.raw ping_neu.raw ping_tongji.raw ping_lip6.raw ping_orange1.raw ping_bupt.raw ping_urjc.raw ping_basel.raw ping_waseda.raw"
ALL_FILES="ping_wu.raw ping_remap.raw "
TEST_FILE="ping_wu.raw"

cd /home/research/jdd/.www-docs/ndnstatus/ndn_ping/

#cat ping_header.html $ALL_FILES ping_trailer.html > ping.html

NODENAME=`grep "Node:" $TEST_FILE | cut -d':' -f 2`

PREFIXES=(`grep "Ping Statistics For " $TEST_FILE | cut -d' ' -f 6`)

PACKET_LOSS=(`grep "Packet Loss" $TEST_FILE | cut -d',' -f 3 | cut -d'=' -f 2 | cut -d'%' -f 1`)

MIN=(`grep "Min" $TEST_FILE | cut -d'(' -f 3 | cut -d')' -f 1 | cut -d'/' -f 1`)
MAX=(`grep "Min" $TEST_FILE | cut -d'(' -f 3 | cut -d')' -f 1 | cut -d'/' -f 2`)
AVG=(`grep "Min" $TEST_FILE | cut -d'(' -f 3 | cut -d')' -f 1 | cut -d'/' -f 3`)
MDEV=(`grep "Min" $TEST_FILE | cut -d'(' -f 3 | cut -d')' -f 1 | cut -d'/' -f 4`)

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
