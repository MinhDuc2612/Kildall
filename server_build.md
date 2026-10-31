# Kildall Server Build

Updated: 2026-10-29. Consolidated from the latest `/Users/minhduc/Downloads/Server_build.pdf` and the user's subsequent decisions.

## Chosen configuration

- Start with **one AMD Instinct MI210: 64GB HBM2e VRAM**. More GPUs can be added later, subject to slot spacing, EPS12V power and validated server airflow.
- **512GB system RAM: 8 × 64GB DDR4-3200 ECC RDIMM**, filling all eight memory channels and DIMM slots.
- Keep the **2000W PSU** for planned expansion.
- The **WD_BLACK / SanDisk Black 8TB NVMe SSD is already purchased**.
- Use a **4U server chassis**, not a desktop tower.
- Monitor, keyboard and mouse are excluded from the shopping list.
- The PDF's RTX A6000/RTX 8000 and 256GB RAM plan are superseded by the MI210 and **512GB RAM** configuration.

## Components and purchase references

Prices below combine the PDF's estimates with checks made on 2026-10-29; none is a guaranteed checkout total. Overseas prices exclude unverified shipping, Vietnamese taxes and forwarding fees unless explicitly described as an estimated landed price. Rejected or unverified options are labelled.

| Component | Quantity and specification | Estimated VND | Purchase reference / status |
|---|---|---:|---|
| GPU | 1 × AMD Instinct MI210, 64GB HBM2e ECC, PCIe 4.0 ×16, passive dual-slot cooling, 300W | **US$3,969 ≈ 102,640,000 before import; roughly 113,000,000–120,000,000 landed** | [Current eBay listing](https://www.ebay.com/itm/365325170443): used, 10+ shown available, seller in Shenzhen with 99.9% feedback; no returns. Vietnam delivery is not confirmed—message the seller and obtain the complete checkout total, serial number, test report and photos before paying. |
| CPU | AMD EPYC 7543P, 32 cores / 64 threads, socket SP3 | 18,000,000 | [PDF eBay listing](https://www.ebay.com/itm/227569662632): US$715.41, used, 10+ shown available at the 2026-10-29 check. Confirm Vietnam checkout and that the CPU is not vendor-locked. |
| Motherboard | Supermicro H12SSL-I, ATX, socket SP3 | 25,000,000 | [Máy Chủ Việt](https://maychuviet.vn/san-pham/mainboard-supermicro-h12ssl-i/). Confirm current quote, BIOS and included accessories. |
| RAM | 8 × Samsung 64GB DDR4-3200 ECC RDIMM; 512GB total; all eight channels populated | 32,000,000 total | [Trung Tâm Máy Chủ, M393A8G40AB2-CWE](https://trungtammaychu.vn/m393a8g40ab2-cwe-samsung-64gb-ddr4-3200-ecc-rdimm-module.html), listed at 4,000,000 VND each. Buy eight identical modules in one matched batch and confirm availability before paying. |
| PSU | Super Flower Leadex Platinum 2000W, full modular | 10,490,000 | [Tân Doanh](https://tandoanh.vn/super-flower-leadex-platinum-2000w-2000w-80-plus-platinum-full-modular-psu/). Confirm exact model and complete original cable set. |
| CPU cooler | Dynatron A35 active SP3 cooler, 110mm tall, rated up to 280W | 1,000,000 allowance | [PDF purchase reference](https://aaawave.com/products/dynatron-a35-3u-active-cpu-cooler-amd-threadripper-epyc-sp3-tr4-strx4-swrx8). Fit is verified; Vietnam landed price remains unverified. |
| Case | SilverStone RM4A, 4U | 5,200,000 | [Khánh Linh PC](https://khanhlinhpc.vn/server-chassis-silverstone-rm4a-4u.html). Prior discussion found a 5,850,000 listing; confirm current quote. |
| GPU/case cooling | 3 × Arctic P12 Max 120mm front intake; 2 × Arctic P8 Max 80mm rear exhaust; sealed front-to-back MI210 air duct | **3,000,000–5,000,000 provisional** | **New fans are required.** Standard P12/P8 fans are not the qualified plan for a passive MI210. P12 Max provides 81.04CFM and 4.35mmH₂O; P8 Max provides 40CFM and 5.3mmH₂O. The completed duct and fan curve still require thermal validation under sustained load. |
| SSD | 1 × WD_BLACK / SanDisk Black 8TB NVMe M.2 | Already purchased | Confirm exact SKU and whether the purchased version includes a heatsink. No duplicate purchase needed. |
| **Superseded PDF subtotal** | **Old A6000/RTX 8000 plan; excludes owned SSD and assembly extras** | **130,190,000** | **Retained only as historical provenance.** |
| **MI210 subtotal before import** | **One MI210 at US$3,969, 512GB RAM and revised cooling; excludes owned SSD and assembly extras** | **Approximately 197,300,000–199,300,000** | **Shipping and Vietnamese tax are not included.** |
| **Realistic MI210 buy-ready total** | **One MI210 with estimated import cost, 512GB RAM and revised passive-GPU cooling** | **Approximately 208,000,000–217,000,000** | **Final total depends mainly on Vietnam delivery, tax and the required fan/duct solution.** |

If the case costs 5,850,000 rather than 5,200,000, add **650,000 VND** to the relevant subtotal.

## Compatibility and expansion

### CPU, board and RAM

The [H12SSL-I manufacturer specification](https://www.supermicro.com/en/products/motherboard/h12ssl-i) lists socket SP3, EPYC 7002/7003 support, eight DDR4 ECC RDIMM slots and an eight-channel memory bus. Its ATX dimensions are 305 × 244mm.

- EPYC 7543P belongs to the compatible EPYC 7003 platform; confirm the delivered BIOS supports it.
- **DDR5 does not fit this platform.** Using DDR5 would require a different CPU and motherboard.
- Install eight identical 64GB modules according to the [board manual](https://www.supermicro.com/manuals/motherboard/EPYC7000/MNL-2314.pdf). This fills every DIMM slot and all eight EPYC memory channels; future capacity expansion requires replacing modules rather than adding more.
- For a used CPU, ask the seller to confirm it is not vendor-locked and includes its SP3 carrier.

### GPU, storage and slots

The board specification lists **five PCIe 4.0 ×16 slots, two PCIe 4.0 ×8 slots and two PCIe 4.0 ×4 M.2 sockets** supporting 2280/22110 drives. These are expansion connectors, not a promise that seven large GPUs physically fit.

- Start with one MI210. AMD specifies 64GB HBM2e ECC, up to 1.6TB/s memory bandwidth, PCIe 4.0, a 300W board limit and passive cooling in a 266.7mm dual-slot card; see the [official MI210 brief](https://www.amd.com/content/dam/amd/en/documents/instinct-business-docs/product-briefs/instinct-mi210-brochure.pdf).
- The MI210 has no monitor output. Use the motherboard's BMC VGA/IPMI console for installation and administration.
- Multiple GPUs require checking physical spacing and airflow. VRAM across cards is usable together only when the inference runtime supports the appropriate model split.
- The owned M.2 SSD uses a motherboard M.2 socket. A second SSD can be added later; confirm exact drive dimensions and heatsink clearance.
- The motherboard provides two Gigabit Ethernet ports plus a separate management/IPMI port. Use a normal LAN port for the server's main network connection.

### Cooler and case clearance

Previously recommended specific cooler: **Dynatron A35**, an active SP3 cooler with its own fan. Its [manufacturer datasheet](https://www.inter-tech.de/files/images/cooler/88885512/A35-Specs-Dynatron.pdf) specifies **120 × 82 × 110mm**, with support for up to **280W** heat dissipation. The EPYC 7543P's nominal TDP is 225W; actual temperatures still need testing after assembly.

The RM4A's published cooler-height limits are **137mm with the expansion-card retainer** and **148mm without it**; see the [case specification reference](https://www.computeralliance.com.au/silverstone-rm4a-4u-rackmount-server-chassis). A 110mm A35 fits within those height limits. Confirm socket mounting, RAM clearance and exact chassis revision before ordering. Do not assume that a generic cooler fits merely because its listing says `4U`.

An A35 seller delivering to Vietnam at a verified landed price has **not** been established. Keep the 1,000,000 VND cooler allowance provisional.

### Power and airflow

- Keep the 2000W PSU for expansion. Its rating is capacity, not constant power consumption.
- Use only modular cables intended for that exact PSU model.
- AMD specifies one **EPS12V 8-pin** input for the 300W MI210. Ordinary PCIe 8-pin and EPS12V 8-pin wiring are not interchangeable; use only a cable verified for this PSU and card.
- Account for the motherboard's CPU power connections before allocating cables to the GPU. Do not assume a spare cable is available.
- Required airflow: **three P12 Max front intakes → sealed MI210 duct → two P8 Max rear exhausts**. The passive heatsink must receive direct front-to-back airflow; ordinary open-case circulation is insufficient.
- Check each motherboard fan header's current limit before daisy-chaining PST fans. Start with separate headers where practical.
- Before adding GPUs, recheck connectors, chassis spacing, temperatures, fan current and PSU capacity at the actual mains input voltage.

## Assembly extras and cables

These are the product pages and prices from the preceding accessory check. Stock labels are website claims from that check, not a guarantee of branch pickup or current availability. Shipping is additional unless the seller states otherwise.

| Item | Link / listed price | Buy when / status |
|---|---|---|
| Phillips screwdrivers | [Stanley six-piece set](https://itcvietnam.vn/bo-to-vit-6-cay-stanley-tst66672-p16196869.html), about 380,000 VND | Case and motherboard assembly; page listed stock. Check the SSD screw separately: it may need a smaller precision Phillips bit. |
| Torque screwdriver | [ALIYIQI AYQ-3, 0.5–3Nm](https://imall.vn/to-vit-dat-luc-0-53n-m-0-05n-m-aliyiqi-ayq-3) | CPU socket; needs a compatible **T20 bit**. Price and stock unconfirmed. No standalone T20-bit purchase was verified. |
| Thermal paste | [Arctic MX-4, 4g](https://gearvn.com/products/keo-tan-nhiet-arctic-mx4-4g), 150,000 VND | Only if the chosen cooler lacks suitable supplied/pre-applied paste. Stock unconfirmed. |
| USB installer drive | [Kingston Exodia 32GB](https://hoanghapc.vn/usb-kingston-32gb-datatraveler-exodia-dtx-32gb-usb-3-2), 190,000 VND | OS installation; page listed stock. Reuse an existing suitable USB drive if available. |
| VGA cable | Buy only if using a local monitor rather than IPMI | Connect the H12SSL-I's BMC VGA output; the MI210 itself has no display connector. |
| Ethernet cable | [UGREEN Cat6 RJ45, 2m](https://ugreenvn.vn/cap-mang-cat6-ugreen/cap-mang-duc-san-cat6-utp-26awg-tron-dai-2m-ugreen-20160.html), 50,000 VND before VAT | Server-to-router connection; page listed stock. Choose length for the actual distance. |
| SP3 CPU carrier | Ask CPU seller to include it | Required for socket installation; check before buying a replacement. No qualified standalone purchase verified. |
| Standoffs, screws, M.2 screw and I/O shield | Ask case/motherboard sellers to include the correct parts | The board's listed I/O shield is **MCP-260-00042-0N**. Used-board bundles may omit it. |
| MI210 EPS12V cable | Ask the GPU and PSU sellers to confirm the exact cable required | No qualified standalone replacement purchase is verified. Never substitute a PCIe 8-pin cable merely because it physically fits. |
| MI210 air duct | Required; fabricate or obtain after measuring the installed card and chassis | It must seal the front intake airflow through the passive GPU heatsink without obstructing adjacent cards or cables. |
| Cable ties / Velcro straps | Optional; local hardware or electronics shop | Cable management; no specific stocked purchase verified. |
| Wired ESD wrist strap | Optional assembly aid | No stocked purchase verified. The previously checked Pro'sKit 608-611B listing was sold out; do not treat it as buy-ready. |
| M.2 heatsink | Conditional | Check whether the owned SSD already has one and whether it fits; no duplicate purchase by default. |

**Display connection:** the MI210 has no display connector. Use the H12SSL-I's rear VGA port or IPMI remote console; no DisplayPort cable is needed for the GPU.

**Ethernet:** a network cable from a normal motherboard LAN port to the router or network switch. Cat6 is sufficient for the board's Gigabit LAN.

## Assembly and first-boot checklist

1. Inventory delivered parts, original PSU cables, MI210 EPS12V cable, CPU carrier, I/O shield and case hardware. Record serial numbers and warranty terms.
2. Work on a stable, non-conductive surface with power disconnected. Inspect the SP3 socket before installing the CPU.
3. Follow the board manual for carrier insertion and socket screw order. It specifies a **T20 driver and 14.0 lbf-in, approximately 1.58Nm**, for the socket screws. The cooler has its own mounting instructions; do not transfer socket torque to cooler screws.
4. Install all eight matching DIMMs in the prescribed order, install the SSD, then fit the cooler with the required thermal interface material.
5. Fit only the case standoffs that match the motherboard mounting holes, then install the board, PSU, GPU and case fans. Secure the GPU before moving the chassis.
6. Connect the board's main and CPU power inputs, the correctly wired MI210 EPS12V supply, front-panel controls and fans. Fit the sealed GPU air duct, then check routing and clearance before closing the lid.
7. First boot: verify the BIOS detects the EPYC CPU, **512GB RAM**, all eight memory channels, SSD and fans. Allow memory training to finish; investigate reported errors before installing software.
8. Install a supported 64-bit Linux distribution, AMD ROCm and the chosen ROCm-capable model runtime. The MI210 is not a CUDA device; confirm every required Kildall backend on ROCm before migration.
9. Validate GPU detection and **64GB HBM2e**, ECC status, memory stability, SSD health and CPU/GPU temperatures under sustained load. Abort the load test if GPU temperature rises abnormally or airflow fails.
10. Copy Kildall data with verification and keep the original device/backup intact until the new server is checked. Benchmark the new runtime before changing production model or routing settings.

## Assessment and outstanding items

**Current assessment: 7.5/10 as a hardware plan.** CPU, motherboard, RAM, case dimensions and PCIe generation are compatible with one MI210, but the GPU purchase and passive-cooling solution are not yet qualified.

Before paying for remaining parts:

- Confirm that the MI210 seller ships to Vietnam and obtain the landed checkout total, serial number, photos and a passing test report. The current listing has no returns.
- Validate the sealed air duct and server-grade fan configuration before sustained MI210 use.
- Confirm the exact cooler, mounting hardware, clearance and Vietnam landed cost.
- Confirm used-CPU compatibility/vendor-lock status, board BIOS and complete accessories.
- Requote the case and other components. No cheaper alternative has been newly verified for this document.
- For every overseas purchase, include shipping, tax and forwarding in the total before deciding it fits the budget.
- Treat **130,190,000 VND as the superseded PDF estimate only**. The updated MI210 + 512GB RAM buy-ready expectation is approximately **208,000,000–217,000,000 VND**, excluding the owned SSD, assembly extras and OS costs.

Source policy: the original PDF and planning files remain unchanged. This document records the chosen build, historical purchase references and unresolved checks; it does not certify current stock or authorize purchases.
