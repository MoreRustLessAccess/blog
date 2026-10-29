# General info
There is several different competing specs
# Active vs Passive
Passive doens't activate LACP until the other peer (required to be active) sends an LACP packet
# How connections are routed (conversation hashing)
Standard-compliant mode is hashing together mac addresses

NOTE: Is this a per dev mac, or for the bond itself?

# Balance modes

# What happens when switching master?
ARP broadcast is sent (https://wiki.wireshark.org/Gratuitous_ARP)
