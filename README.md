# Switch Mode

- [Switch Mode](#switch-mode)
  - [Overview](#overview)
    - [Features](#features)
  - [Requirements](#requirements)
  - [**Installation**](#installation)
  - [Usage](#usage)
    - [ShowTech](#showtech)
    - [HistoryTech](#historytech)
    - [ShowTechExtended](#showtechextended) 
  - [**Updates**](#updates) {check here for added new updates}
  - [**Feature Requests and Bugs**](#feature-requests-and-bugs)

## Overview

SwitchMode is a script that takes in a show tech file and creates an interface similar to the switch CLI for enhanced and faster troubleshooting.

### Features

- Switch CLI like User Interface
- IPv4 Route Lookup
- Linux Pipelining
- Custom Commands Support

## Requirements

- [Git](https://git-scm.com/download/mac)
  - `brew install git`
- [Python3](https://www.python.org/downloads/macos/)
  - Python3 should be installed by default on MAC (atleast 3.10 is required)
  - `$(which python3) --version`

## Installation

Installing SwitchMode and to get it running is pretty simple and straighforward.

Download this repository, using zip/tar or git clone.

```shell
cd ~/Downloads

git clone https://gitlab.aristanetworks.com/roshan/switch_mode.git

cd switch_mode
```

Once in the repository, we can use the following commands to add the alias to invoke the script. 

```shell
echo "alias sw='python3 $PWD/Main.py \$1'" >> ~/.zshrc
echo "alias ew='python3 $PWD/Evpn.py \$1'" >> ~/.zshrc
echo "alias hdiff='python3 $PWD/hdiff.py \$1 \$2'" >> ~/.zshrc 
source ~/.zshrc
```
<b>Note: we could use any custom alias in here. Just replace the keywords 'sw'/'ew'/'hdiff' with the keywords of your choice to invoke the script.<b>

## Usage

To run the script, type the following command.

`sw <file-name>` <- For show tech files

`ew <file-name>` <- For show tech extended files 

`hdiff <directory path containing the history techs> <command to check>` <- To run a command across history tech support files

## ShowTech

```shell
Eliot:~/Desktop/Logs$ sw showtech.log

Switch#
```

*** Gzip files are now supported ***

```shell
Eliot:~/Desktop/Logs$ sw showtech.log.gz

Switch#
```

- Once into switch mode, just type the commands as you would in a typical switch.

```shell
Switch# show mac address-table
------------- show mac address-table -------------

          Mac Address Table
------------------------------------------------------------------

Vlan    Mac Address       Type        Ports      Moves   Last Move
----    -----------       ----        -----      -----   ---------
   5    001c.73de.cade    DYNAMIC     Vx1        1       104 days, 0:26:19 ago
   5    2cdd.e95a.b9d3    DYNAMIC     Vx1        1       0:01:22 ago
   5    b47a.f1ae.2d00    DYNAMIC     Vx1        1       104 days, 0:26:19 ago
<truncated>
```

- The switch mode also enables linux pipelining.

```shell
Switch# show version detail | head -n 10
------------- show version detail -------------

Arista DCS-7050CX3-32S-F
Hardware version:      11.10
Deviations:
Serial number:         JPE21263009
Hardware MAC address:  2cdd.e97e.e73d
System MAC address:    2cdd.e97e.e73d

Software image version: 4.24.4M
```
```
Switch# show version detail | cat > ~/Desktop/myloganalyis
```

- In case if you are unsure of the command, you could use "?" and type enter.

```shell
? used immediately after a commmand

Switch# show int?
interfaces
interface
```

```shell
? used after the command with a space in between

Switch# show interfaces ?
status
switchport
phy
```

```shell
if ?? is used

Switch# show interfaces ??
show interfaces status
show interfaces status errdisabled
show interfaces switchport
show interfaces phy detail
show interfaces counters queue | nz
<truncated>
```
- Ip route output supported for per vrf.
```shell
For default vrf

Switch: show ip route
VRF: default
Codes: C - connected, S - static, K - kernel,  +
 +
       O - OSPF, IA - OSPF inter area, E1 - OSPF external type 1,
       E2 - OSPF external type 2, N1 - OSPF NSSA external type 1,
       N2 - OSPF NSSA external type2, B - BGP, B I - iBGP, B E - eBGP,
       R - RIP, I L1 - IS-IS level 1, I L2 - IS-IS level 2,
       O3 - OSPFv3, A B - BGP Aggregate, A O - OSPF Summary,
       NG - Nexthop Group Static Route, V - VXLAN Control Service,
       DH - DHCP client installed default route, M - Martian,
       DP - Dynamic Policy Route, L - VRF Leaked,
       G  - gRIBI, RC - Route Cache Route

Gateway of last resort:
 B E      0.0.0.0/0 [20/0] via 10.53.13.150, Ethernet97 Uplink to Spine-01
                           via 10.53.13.158, Ethernet99 Uplink to Spine-02

 M        0.0.0.0/8 is directly connected, <Internal>
 C        1.1.1.0/30 is directly connected, Vlan4094
 <truncated>
 ```
 ```shell
 For non-deafult vrf

Switch: show ip route vrf management
VRF: management
Codes: C - connected, S - static, K - kernel,  +
 +
       O - OSPF, IA - OSPF inter area, E1 - OSPF external type 1,
       E2 - OSPF external type 2, N1 - OSPF NSSA external type 1,
       N2 - OSPF NSSA external type2, B - BGP, B I - iBGP, B E - eBGP,
       R - RIP, I L1 - IS-IS level 1, I L2 - IS-IS level 2,
       O3 - OSPFv3, A B - BGP Aggregate, A O - OSPF Summary,
       NG - Nexthop Group Static Route, V - VXLAN Control Service,
       DH - DHCP client installed default route, M - Martian,
       DP - Dynamic Policy Route, L - VRF Leaked,
       G  - gRIBI, RC - Route Cache Route

Gateway of last resort:
 S        0.0.0.0/0 [1/0] via 10.53.2.1, Management1 management

 M        0.0.0.0/8 is directly connected, <Internal>
 C        10.53.2.0/24 is directly connected, Management1 management
 M        127.0.0.1/32 is directly connected, <Internal>
 M        127.0.0.0/8 is directly connected, <Internal>
 ```
- SwitchMode also supports IPv4 route look up in default and non-deafult vrf.

```shell
Switch: show ip route 192.168.92.57
VRF: default
B E      192.168.92.56/30 [20/0] via 10.53.13.150, Ethernet97 Uplink to Spine-01
                               via 10.53.13.158, Ethernet99 Uplink to Spine-02
```

```shell
Switch: show ip route vrf management 10.53.2.1
VRF: management
 C        10.53.2.0/24 is directly connected, Management1 management
 ```
- Ipv6 route(and lookup) output supported for per vrf.
```shell
Switch: show ipv6 route 2a01:b747:8108:1000::1
VRF: default
 B        2a01:b747:8108:1000::/56 [20/10]
           via 2620:149:bb:4710::21, Port-Channel200.201 P1-TO-USSEA4-BBISP-GW1|-|PO200.201|-|-|BB
           via 2620:149:bb:4720::21, Port-Channel201.201 P1-TO-USSEA4-BBISP-GW2|-|PO201.201|-|-|BB
```

```shell
Switch: show ipv6 route vrf GLOBAL 2a01:b747:8108:1000::1
VRF: GLOBAL
 B        ::/0 [20/10]
           via 2620:149:bb:710::21, Port-Channel200.101 P1-TO-USSEA4-BBISP-GW1|-|PO200.101|-|-|BB
           via 2620:149:bb:720::21, Port-Channel201.101 P1-TO-USSEA4-BBISP-GW2|-|PO201.101|-|-|BB
 ```


## HistoryTech

- History Tech-supports diff output can now be generated as follows (make sure there's no space in the filename or file path since it's behaviour is different on different os versions).

`hdiff <directory of History-tech> <command in quotes>`

```shell
~/Desktop/Logs/Mingsoong❯ hdiff schedule/tech-support/ 'show clock | head -n 2'                                                                                            

uk-wat-eci-npmgmtsw02_tech-support_2023-12-02.1904.log.gz
------------- show clock -------------
Sat Dec  2 19:04:32 2023

********************

uk-wat-eci-npmgmtsw02_tech-support_2023-12-02.1804.log.gz
------------- show clock -------------
Sat Dec  2 18:04:32 2023

<truncated>
 ```

```
~/Desktop/Logs/Barclays/mnt/flash/schedule/tech-support❯ hdiff ./ "show ip int br | grep -v 1500"                                 

SMU-7280-ARISTA-2_tech-support_2024-02-02.0450.log.gz
Interface          IP Address              Status       Protocol             MTU
------------------ ----------------------- ------------ -------------------- -----------
Loopback1          10.1.255.1/32           up           up                   65535
Vlan4092           10.100.102.102/30       up           up                   9214
Vlan4093           10.100.101.102/30       up           up                   9214


********************

SMU-7280-ARISTA-2_tech-support_2024-02-02.0550.log.gz
Interface          IP Address              Status       Protocol             MTU
------------------ ----------------------- ------------ -------------------- -----------
Loopback1          10.1.255.1/32           up           up                   65535
Vlan4092           10.100.102.102/30       up           up                   9214
Vlan4093           10.100.101.102/30       up           up                   9214
<truncated>
```

## ShowTechExtended 

Switch mode also supports EVPN parsing.

`ew <filename>`

```Test/tmp/support-bundle-cmds
❯ ~/Desktop/Bofa/tmp/support-bundle-cmds$ ew show-tech-support-extended-evpn
switch:
```
- Question mark supported as with show tech.

```
switch: show bgp ??
show bgp evpn
show bgp evpn detail
show bgp evpn instance
show bgp evpn next-hop <next-hop>
show bgp evpn rd <rd> detail
show bgp evpn rd <rd> vni <vni>
show bgp evpn rd <rd> vni <vni> next-hop <next-hop>
show bgp evpn route-type <route-type> <route> detail
show bgp evpn route-type <route-type> <route> next-hop <next-hop> rd <rd> vni <vni>
show bgp evpn route-type <route-type> <route> next-hop <next-hop> vni <vni> rd <rd>
show bgp evpn route-type <route-type> <route> rd <rd> detail
<truncated>
```
- Fine tune the output as per your need. Linux pipelining is supported as well here.

```
switch: show bgp evpn route-type mac-ip b47a.f168.7109
 * >      RD: 10.184.0.109:633 mac-ip b47a.f168.7109
                                 10.184.0.109          -       100     0       65203.1006 i
 * >      RD: 10.184.0.109:633 mac-ip b47a.f168.7109 10.184.210.215
                                 10.184.0.109          -       100     0       65203.1006 i
 * >      RD: 10.184.0.110:633 mac-ip b47a.f168.7109
                                 10.184.0.110         -       100     0       65203.1006 i
 * >      RD: 10.184.0.110:633 mac-ip b47a.f168.7109 10.184.210.215
                                 10.184.0.110        -       100     0       65203.1006 i
```

```
switch: show bgp evpn route-type mac-ip b47a.f168.7109 rd 10.184.0.109:633
 * >      RD: 10.184.0.109:633 mac-ip b47a.f168.7109
                                 10.184.0.109          -       100     0       65203.1006 i
 * >      RD: 10.184.0.109:633 mac-ip b47a.f168.7109 10.184.210.215
                                 10.184.0.109          -       100     0       65203.1006 i
```

```
switch: show bgp evpn route-type mac-ip b47a.f168.7109 rd 10.184.0.109:633 | wc - l

   4
```

## Updates
- Exceptions are now notified to a centralized server.
- Better error handling.
- Fine tuned question mark specific commands.
- Command autocomplete is supported.
- IPv6 route lookup is now supported (all or per vrf)
- BGP outputs are supported per vrf
- IPv4 routes can now be looked up in all vrfs at once
- Ip(v4/v6) host/summary routes can be outputted per vrf

## Feature Requests and Bugs 

Please use [this document](https://docs.google.com/document/d/1Q3eoH3ynrmpqYQKKeLTei0jDfon1XjQioH8IpdOBtZU/edit?usp=sharing) for filing any BUGs or feautre Requests (RFEs).
