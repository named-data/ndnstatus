#!/bin/bash
SSH_AUTH_SOCK=/tmp/ssh-JjqTGz3468/agent.3468; export SSH_AUTH_SOCK;
scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@wundngw.arl.wustl.edu:/home/ndnops/ndn-ops/NOC/test_scripts/ndnping.log.export /home/research/jdd/.www-docs/ndnstatus/ndn_ping/ping_wu.raw
#scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@titan.cs.memphis.edu:/home/ndnops/ndn-ops/NOC/test_scripts/ndnping.log.export /home/research/jdd/.www-docs/ndnstatus/ndn_ping/ping_memphis.raw
#scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@ndn0.eecs.umich.edu:/home/ndnops/ndn-ops/NOC/test_scripts/ndnping.log.export /home/research/jdd/.www-docs/ndnstatus/ndn_ping/ping_michigan.raw
#scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@ndn.netsec.colostate.edu:/home/ndnops/ndn-ops/NOC/test_scripts/ndnping.log.export /home/research/jdd/.www-docs/ndnstatus/ndn_ping/ping_csu.raw
#scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@spurs.cs.ucla.edu:/home/ndnops/ndn-ops/NOC/test_scripts/ndnping.log.export /home/research/jdd/.www-docs/ndnstatus/ndn_ping/ping_ucla.raw
#scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@hobo.cs.arizona.edu:/home/ndnops/ndn-ops/NOC/test_scripts/ndnping.log.export /home/research/jdd/.www-docs/ndnstatus/ndn_ping/ping_arizona.raw
scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@aleph.ndn.ucla.edu:/home/ndnops/ndn-ops/NOC/test_scripts/ndnping.log.export /home/research/jdd/.www-docs/ndnstatus/ndn_ping/ping_remap.raw
#scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@ndnx.cs.illinois.edu:/home/ndnops/ndn-ops/NOC/test_scripts/ndnping.log.export /home/research/jdd/.www-docs/ndnstatus/ndn_ping/ping_uiuc.raw
##scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@ndnhub.ics.uci.edu:/home/ndnops/ndn-ops/NOC/test_scripts/ndnping.log.export /home/research/jdd/.www-docs/ndnstatus/ndn_ping/ping_uci.raw
#scp tb-uci:/home/ndnops/ndn-ops/NOC/test_scripts/ndnping.log.export /home/research/jdd/.www-docs/ndnstatus/ndn_ping/ping_uci.raw
#scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@click.caida.org:/home/ndnops/ndn-ops/NOC/test_scripts/ndnping.log.export /home/research/jdd/.www-docs/ndnstatus/ndn_ping/ping_caida.raw
#scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@162.105.146.26:/home/ndnops/ndn-ops/NOC/test_scripts/ndnping.log.export /home/research/jdd/.www-docs/ndnstatus/ndn_ping/ping_pku.raw
#scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@129.10.52.193:/home/ndnops/ndn-ops/NOC/test_scripts/ndnping.log.export /home/research/jdd/.www-docs/ndnstatus/ndn_ping/ping_neu.raw
#scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@cnlab.tongji.edu.cn:/home/ndnops/ndn-ops/NOC/test_scripts/ndnping.log.export /home/research/jdd/.www-docs/ndnstatus/ndn_ping/ping_tongji.raw
#scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@ndnhub.ipv6.lip6.fr:/home/ndnops/ndn-ops/NOC/test_scripts/ndnping.log.export /home/research/jdd/.www-docs/ndnstatus/ndn_ping/ping_lip6.raw
#scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@161.105.195.18:/home/ndnops/ndn-ops/NOC/test_scripts/ndnping.log.export /home/research/jdd/.www-docs/ndnstatus/ndn_ping/ping_orange1.raw
#scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@114.247.165.44:/home/ndnops/ndn-ops/NOC/test_scripts/ndnping.log.export /home/research/jdd/.www-docs/ndnstatus/ndn_ping/ping_bupt.raw
#scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@insula.gsyc.es:/home/ndnops/ndn-ops/NOC/test_scripts/ndnping.log.export /home/research/jdd/.www-docs/ndnstatus/ndn_ping/ping_urjc.raw
#scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@ndn.cs.unibas.ch:/home/ndnops/ndn-ops/NOC/test_scripts/ndnping.log.export /home/research/jdd/.www-docs/ndnstatus/ndn_ping/ping_basel.raw
#scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@133.9.73.66:/home/ndnops/ndn-ops/NOC/test_scripts/ndnping.log.export /home/research/jdd/.www-docs/ndnstatus/ndn_ping/ping_waseda.raw

#ALL_FILES="ping_wu.raw ping_memphis.raw ping_michigan.raw ping_csu.raw ping_ucla.raw ping_arizona.raw ping_remap.raw ping_uiuc.raw ping_uci.raw ping_caida.raw ping_pku.raw ping_neu.raw ping_tongji.raw ping_lip6.raw ping_orange1.raw ping_bupt.raw ping_urjc.raw ping_basel.raw ping_waseda.raw"
#cd /home/research/jdd/.www-docs/ndnstatus/ndn_ping/
#cat ping_header.html $ALL_FILES ping_trailer.html > ping.html
