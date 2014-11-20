#!/bin/bash
SSH_AUTH_SOCK=/tmp/ssh-JjqTGz3468/agent.3468; export SSH_AUTH_SOCK;
scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@wundngw.arl.wustl.edu:/home/ndnops/ndn-ops/NOC/bin/ndnops_diag.log /home/research/jdd/.www-docs/ndnstatus/ndn_diag/diag_wu.html
scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@titan.cs.memphis.edu:/home/ndnops/ndn-ops/NOC/bin/ndnops_diag.log /home/research/jdd/.www-docs/ndnstatus/ndn_diag/diag_memphis.html
scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@ndn0.eecs.umich.edu:/home/ndnops/ndn-ops/NOC/bin/ndnops_diag.log /home/research/jdd/.www-docs/ndnstatus/ndn_diag/diag_michigan.html
scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@ndn.netsec.colostate.edu:/home/ndnops/ndn-ops/NOC/bin/ndnops_diag.log /home/research/jdd/.www-docs/ndnstatus/ndn_diag/diag_csu.html
scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@spurs.cs.ucla.edu:/home/ndnops/ndn-ops/NOC/bin/ndnops_diag.log /home/research/jdd/.www-docs/ndnstatus/ndn_diag/diag_ucla.html
scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@hobo.cs.arizona.edu:/home/ndnops/ndn-ops/NOC/bin/ndnops_diag.log /home/research/jdd/.www-docs/ndnstatus/ndn_diag/diag_arizona.html
scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@aleph.ndn.ucla.edu:/home/ndnops/ndn-ops/NOC/bin/ndnops_diag.log /home/research/jdd/.www-docs/ndnstatus/ndn_diag/diag_remap.html
scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@ndnx.cs.illinois.edu:/home/ndnops/ndn-ops/NOC/bin/ndnops_diag.log /home/research/jdd/.www-docs/ndnstatus/ndn_diag/diag_uiuc.html
#scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@ndnhub.ics.uci.edu:/home/ndnops/ndn-ops/NOC/bin/ndnops_diag.log /home/research/jdd/.www-docs/ndnstatus/ndn_diag/diag_uci.html
scp tb-uci:/home/ndnops/ndn-ops/NOC/bin/ndnops_diag.log /home/research/jdd/.www-docs/ndnstatus/ndn_diag/diag_uci.html
scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@click.caida.org:/home/ndnops/ndn-ops/NOC/bin/ndnops_diag.log /home/research/jdd/.www-docs/ndnstatus/ndn_diag/diag_caida.html
scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@162.105.146.26:/home/ndnops/ndn-ops/NOC/bin/ndnops_diag.log /home/research/jdd/.www-docs/ndnstatus/ndn_diag/diag_pku.html
scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@129.10.52.193:/home/ndnops/ndn-ops/NOC/bin/ndnops_diag.log /home/research/jdd/.www-docs/ndnstatus/ndn_diag/diag_neu.html
scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@cnlab.tongji.edu.cn:/home/ndnops/ndn-ops/NOC/bin/ndnops_diag.log /home/research/jdd/.www-docs/ndnstatus/ndn_diag/diag_tongji.html
scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@ndnhub.ipv6.lip6.fr:/home/ndnops/ndn-ops/NOC/bin/ndnops_diag.log /home/research/jdd/.www-docs/ndnstatus/ndn_diag/diag_lip6.html
scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@161.105.195.18:/home/ndnops/ndn-ops/NOC/bin/ndnops_diag.log /home/research/jdd/.www-docs/ndnstatus/ndn_diag/diag_orange1.html
scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@114.247.165.44:/home/ndnops/ndn-ops/NOC/bin/ndnops_diag.log /home/research/jdd/.www-docs/ndnstatus/ndn_diag/diag_bupt.html
scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@insula.gsyc.es:/home/ndnops/ndn-ops/NOC/bin/ndnops_diag.log /home/research/jdd/.www-docs/ndnstatus/ndn_diag/diag_urjc.html
scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@ndn.cs.unibas.ch:/home/ndnops/ndn-ops/NOC/bin/ndnops_diag.log /home/research/jdd/.www-docs/ndnstatus/ndn_diag/diag_basel.html
scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@133.9.73.66:/home/ndnops/ndn-ops/NOC/bin/ndnops_diag.log /home/research/jdd/.www-docs/ndnstatus/ndn_diag/diag_waseda.html
scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@systemx-ndn-1.enst.fr:/home/ndnops/ndn-ops/NOC/bin/ndnops_diag.log /home/research/jdd/.www-docs/ndnstatus/ndn_diag/diag_systemx.html
scp -o "StrictHostKeyChecking no" -i ~/.ssh/all_planetlab_id_rsa ndnops@pasta10.cs.byu.edu:/home/ndnops/ndn-ops/NOC/bin/ndnops_diag.log /home/research/jdd/.www-docs/ndnstatus/ndn_diag/diag_byu.html

ALL_FILES="diag_wu.html diag_memphis.html diag_michigan.html diag_csu.html diag_ucla.html diag_arizona.html diag_remap.html diag_uiuc.html diag_uci.html diag_caida.html diag_pku.html diag_neu.html diag_tongji.html diag_lip6.html diag_orange1.html diag_bupt.html diag_urjc.html diag_basel.html diag_waseda.html diag_systemx.html diag_byu.html"
cd /home/research/jdd/.www-docs/ndnstatus/ndn_diag/
cat diag_header.html $ALL_FILES diag_trailer.html > diag.html
