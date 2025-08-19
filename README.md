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

Create a Python3 script that reads a kathara lab.conf file as input and will output all the kathara startup files.

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

Let me know if you want a deeper dive into IS-IS packet types, configuration examples, or comparisons to other protocols like OSPF!

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
