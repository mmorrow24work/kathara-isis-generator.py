# kathara-isis-generator.py

Mick Morrow  | Solutions Architect
Email: Mick.Morrow@telent.com
Mobile: 07974398922
Web: www.telent.com

Creating the startup files for a complex kathara network would be very difficult and very time consuming if done manually,
so best practice is to create them using a programmatic method in the same way we create startup scripts for routers and switches.

A common method is to use a spreadsheet which contains all the logic and access to the lab.conf data; another is to create a 
program which will use the lab.conf as an input and output all the startup files. 

Both methods have their pros and cons, but we have chosen to use Python3 scripts because it allowed us to use AI to create 
the code based on prompts that describe the requirement.

This code was created using AI (https://claude.ai/) based on the following prompt:

***

Create a Python3 script ( kathara-isis-generator.py ) that reads a kathara lab.conf file as input and will output all the kathara startup files.

Use IS-IS routing and assign IPs to all interfaces and check that they are online and use the most appropriate subnet masks - 
e.g. use /30 networks for point-to-point connections and /29 networks elsewhere if possible, otherwise use /28 or /27 etc. 

Include debug code and comments to help with troubleshooting.

Ensure snmp_manager which will run Zabbix server has the IP 192.168.1.7 because the Zabbix agents will be configured to respond to the Zabbix agents.

***

IS-IS (Intermediate System to Intermediate System) is a **link-state interior gateway routing protocol** designed to efficiently exchange routing information within a single autonomous system (AS). Here's a concise overview:

***

### What is IS-IS?

- **IS-IS** is a link-state routing protocol used primarily in large service provider and enterprise networks.
- It operates within a single AS to distribute routing information among routers (called Intermediate Systems).
- Originally designed for routing OSI CLNP packets, it was later adapted to support IP.

***

### How IS-IS Works

- Each router creates Link-State Packets (LSPs) containing information about itself and its directly connected neighbors.
- Routers flood these LSPs across the network, building a complete map of the topology in a Link State Database (LSDB).
- Each router runs the Shortest Path First (SPF) algorithm (Dijkstra’s) on the LSDB to determine efficient paths to all networks.
- IS-IS supports a two-level hierarchy for scalability:
  - **Level 1:** intra-area routing (within a single area)
  - **Level 2:** inter-area routing (connecting multiple areas)
- Routers can be Level 1, Level 2, or both (Level 1-2).

***

### Key Features

- **Scalability:** Designed to handle very large networks with hierarchical areas.
- **Fast convergence:** Rapidly adapts to network changes using SPF recalculations.
- **Efficient flooding:** Uses LSPs to minimize unnecessary control traffic.
- **Extensibility:** Supports extensions like Segment Routing (SR-MPLS).
- **Vendor-neutral:** Open standard widely supported across networking vendors.

***

### Use Cases

- Popular in large ISP backbones and data center networks.
- Sometimes preferred over OSPF for greater scalability and simpler protocol operations.

***

### Summary Table

| Aspect           | Description                                  |
|------------------|----------------------------------------------|
| Protocol Type    | Link-state interior gateway protocol         |
| Routing Metric   | Cost based, shortest path first (SPF)        |
| Architecture    | Hierarchical with Level 1 (intra-area) and Level 2 (inter-area) |
| Operational Scope | Within a single Autonomous System (AS)       |
| Convergence     | Fast via link-state updates and SPF recomputation |
| Usage           | Large service providers, enterprise networks |

***

### Reference material:

[1] https://jumpcloud.com/it-index/what-is-is-is-intermediate-system-to-intermediate-system
[2] https://30dayscoding.com/blog/isis-routing-protocol-guide
[3] https://info.support.huawei.com/info-finder/encyclopedia/en/IS-IS.html
[4] https://networklessons.com/is-is/introduction-to-is-is
[5] https://en.wikipedia.org/wiki/IS-IS
[6] https://www.juniper.net/documentation/us/en/software/junos/is-is/topics/concept/is-is-routing-overview.html
[7] https://cciedump.spoto.net/newblog/understanding-is-is:-a-deep-dive-into-intermediate-system-to-intermediate-system-routing-protocol.html
[8] https://www.cisco.com/site/us/en/products/networking/software/ios-nx-os/intermediate-system-to-intermediate-system-is-is/index.html
[9] https://www.pynetlabs.com/introduction-to-is-is-protocol/
[10] https://www.routeralley.com/guides/isis.pdf

***

A Docker container running **FRR** (FRRouting) with **IS-IS** protocol enabled acts as a **Layer 3 router**, *not* a Layer 2 switch.

### Why?

- **IS-IS** is a Layer 3 (network layer) routing protocol. It is used for exchanging IP routing information between routers to build dynamic IP routing tables and make Layer 3 forwarding decisions.[1][2][3]
- The default use-case for **FRR** and IS-IS is to route packets between different networks and subnets based on IP addresses, not to perform Layer 2 switching (which forwards Ethernet frames inside the same subnet or VLAN).

### Details:

- A Layer 3 router (using IS-IS in FRR) makes decisions based on destination IP addresses and routes traffic between subnets.
- A Layer 2 switch operates at the data link layer (Ethernet), forwarding traffic based on MAC addresses—FRR and IS-IS do *not* provide this capability natively.
- Docker containers running FRR/IS-IS communicate via routed (L3) interfaces; bridging and switching would require extra Linux bridge configuration outside of FRR.

### Both?
FRR can participate in some Layer 2 features (e.g., bridging, VXLAN, EVPN using BGP), but **IS-IS** is strictly a Layer 3 protocol. Unless you specifically add Linux bridging into the networking setup (outside of FRR), a container running only FRR+IS-IS will not serve as a switch.[2][1]

***

**Summary:**  
A Docker container running FRR with IS-IS enabled is a **Layer 3 router**, not a Layer 2 switch. It routes IP packets between networks using the IS-IS protocol.[1][2]

### Reference material:

[1] https://isis.bgplabs.net/basic/0-frrouting/
[2] https://docs.frrouting.org/en/stable-8.0/isisd.html
[3] https://docs.frrouting.org/en/latest/isisd.html
[4] https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/iproute_isis/configuration/15-sy/irs-15-sy-book/irs-ipv4-lfafrr.html
[5] https://github.com/FRRouting/frr/issues/12793
[6] https://www.cisco.com/c/en/us/td/docs/routers/asr920/configuration/guide/mpls/17-1-1/b-mp-l2-vpns-xe-17-1-asr920/m_loop-free-asr920.html
[7] https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/iproute_isis/configuration/15-s/irs-15-s-book/irs-rmte-lfa-frr.pdf
[8] https://github.com/FRRouting/frr/issues/6965
[9] ttps://github.com/FRRouting/frr/issues/4872
[10] https://support.huawei.com/enterprise/en/doc/EDOC1100459443/ff483841/example-for-configuring-is-is-auto-frr-ip-protecting-ip
[11] https://docs.frrouting.org/en/stable-8.3/installation.html
[12] https://documentation.nokia.com/html/0_add-h-f/93-0267-HTML/7X50_Advanced_Configuration_Guide/MPLS-LDP-FRR.html
[13] https://documentation.nokia.com/html/0_add-h-f/93-0267-HTML/7X50_Advanced_Configuration_Guide/MPLS-LDP-FRR.pdf
[14] https://github.com/FRRouting/frr/issues/13950
[15] https://info.support.huawei.com/hedex/api/pages/EDOC1100277644/AEM10221/04/resources/vrp/feature_0003998201.html
[16] https://lists.fd.io/g/vpp-dev/topic/isis_with_vpp_frr/93683140
[17] https://isis.bgplabs.net/1-setup/
[18] https://www.uni-koeln.de/~pbogusze/posts/FRRouting_IS-IS_Segment_Routing_tech_demo.html
[19] https://www.cisco.com/c/en/us/td/docs/routers/ncs4200/configuration/guide/mpls/mp-l2-vpns-ncs4200-book/mp-l2-vpns-ncs4200-book_chapter_0101.html
[20] https://www.juniper.net/documentation/us/en/software/junos/is-is/topics/concept/isis-node-link-protection-understanding.html
