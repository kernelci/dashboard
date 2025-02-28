http 'http://localhost:8000/api/test/maestro%3A678ee7b046f65f378a18d33e'

# HTTP/1.1 200 OK
# Allow: GET, HEAD, OPTIONS
# Cache-Control: max-age=0
# Content-Length: 20004
# Content-Type: application/json
# Cross-Origin-Opener-Policy: same-origin
# Date: Fri, 28 Feb 2025 12:48:28 GMT
# Expires: Fri, 28 Feb 2025 12:48:28 GMT
# Referrer-Policy: same-origin
# Server: WSGIServer/0.2 CPython/3.12.7
# Vary: Accept, Cookie, origin
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY

# {
#     "architecture": "arm64",
#     "build_id": "maestro:678eddbf46f65f378a1850b3",
#     "compiler": "gcc-12",
#     "config_name": "defconfig",
#     "environment_compatible": [
#         "libretech,aml-a311d-cc",
#         "amlogic,a311d",
#         "amlogic,g12b"
#     ],
#     "environment_misc": {
#         "platform": "meson-g12b-a311d-libretech-cc"
#     },
#     "git_commit_hash": "d73a4602e973e9e922f00c537a4643907a547ade",
#     "git_commit_tags": [],
#     "git_repository_branch": "main",
#     "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/netdev/net-next.git",
#     "id": "maestro:678ee7b046f65f378a18d33e",
#     "log_excerpt": "BL33 decompress pass\nERROR:   Error initializing runtime service opteed_fast\nU-Boot 2024.01-rc4+ (Dec 14 2023 - 01:31:33 -0500) Libre Computer AML-A311D-CC\nModel: Libre Computer AML-A311D-CC Alta\nSoC:   Amlogic Meson G12B (A311D) Revision 29:b (10:2)\nDRAM:  2 GiB (effective 3.8 GiB)\nCore:  408 devices, 31 uclasses, devicetree: separate\nWDT:   Not starting watchdog@f0d0\nMMC:   mmc@ffe05000: 1, mmc@ffe07000: 0\nLoading Environment from FAT... Card did not respond to voltage select! : -110\n** Bad device specification mmc 0 **\nCard did not respond to voltage select! : -110\n** Bad device specification mmc 0 **\nCouldn't find partition mmc 0\nCard did not respond to voltage select! : -110\n** Bad device specification mmc 0 **\nCouldn't find partition mmc 0\nError: could not access storage.\nG12B:BL:6e7c85:2a3b91;FEAT:E0F83180:402000;POC:B;RCY:0;SPINOR:0;0.\nbl2_stage_init 0x01\nbl2_stage_init 0x81\nhw id: 0x0000 - pwm id 0x01\nbl2_stage_init 0xc1\nbl2_stage_init 0x02\nL0:00000000\nL1:20000703\nL2:00008067\nL3:14000000\nB2:00402000\nB1:e0f83180\nTE: 58159\nBL2 Built : 15:22:05, Aug 28 2019. g12b g1bf2b53 - luan.yuan@droid15-sz\nBoard ID = 1\nSet A53 clk to 24M\nSet A73 clk to 24M\nSet clk81 to 24M\nA53 clk: 1200 MHz\nA73 clk: 1200 MHz\nCLK81: 166.6M\nsmccc: 00012ab4\nDDR driver_vesion: LPDDR4_PHY_V_0_1_18 build time: Aug 28 2019 15:22:01\nboard id: 1\nLoad FIP HDR from SPI, src: 0x00010000, des: 0xfffd0000, size: 0x00004000, part: 0\nfw parse done\nLoad ddrfw from SPI, src: 0x00030000, des: 0xfffd0000, size: 0x0000c000, part: 0\nLoad ddrfw from SPI, src: 0x00014000, des: 0xfffd0000, size: 0x00004000, part: 0\nPIEI prepare done\nfastboot data load\nfastboot data verify\nverify result: 266\nCfg max: 1, cur: 1. Board id: 255. Force loop cfg\nLPDDR4 probe\nddr clk to 1584MHz\nLoad ddrfw from SPI, src: 0x00018000, des: 0xfffd0000, size: 0x0000c000, part: 0\ndmc_version 0001\nCheck phy result\nINFO : End of CA training\nINFO : End of initialization\nINFO : Training has run successfully!\nCheck phy result\nINFO : End of initialization\nINFO : End of read enable training\nINFO : End of fine write leveling\nINFO : End of Write leveling coarse delay\nINFO : Training has run successfully!\nCheck phy result\nINFO : End of initialization\nINFO : End of read dq deskew training\nINFO : End of MPR read delay center optimization\nINFO : End of write delay center optimization\nINFO : End of read delay center optimization\nINFO : End of max read latency training\nINFO : Training has run successfully!\n1D training succeed\nLoad ddrfw from SPI, src: 0x00024000, des: 0xfffd0000, size: 0x0000c000, part: 0\nCheck phy result\nINFO : End of initialization\nINFO : End of 2D read delay Voltage center optimization\nINFO : End of 2D read delay Voltage center optimization\nINFO : End of 2D write delay Voltage center optimization\nINFO : End of 2D write delay Voltage center optimization\nINFO : Training has run successfully!\nchannel==0\nRxClkDly_Margin_A0==88 ps 9\nTxDqDly_Margin_A0==98 ps 10\nRxClkDly_Margin_A1==88 ps 9\nTxDqDly_Margin_A1==98 ps 10\nTrainedVREFDQ_A0==74\nTrainedVREFDQ_A1==74\nVrefDac_Margin_A0==24\nDeviceVref_Margin_A0==40\nVrefDac_Margin_A1==25\nDeviceVref_Margin_A1==40\nchannel==1\nRxClkDly_Margin_A0==98 ps 10\nTxDqDly_Margin_A0==88 ps 9\nRxClkDly_Margin_A1==98 ps 10\nTxDqDly_Margin_A1==88 ps 9\nTrainedVREFDQ_A0==75\nTrainedVREFDQ_A1==77\nVrefDac_Margin_A0==23\nDeviceVref_Margin_A0==38\nVrefDac_Margin_A1==24\nDeviceVref_Margin_A1==37\ndwc_ddrphy_apb_wr((0<<20)|(2<<16)|(0<<12)|(0xb0):0004\nsoc_vref_reg_value 0x 00000019 0000001a 00000017 00000019 00000018 00000019 00000018 00000018 00000018 00000016 00000018 00000015 00000017 00000019 00000017 00000019 00000018 00000019 00000019 00000018 00000016 00000018 00000018 00000019 00000018 00000017 00000019 00000019 0000001a 00000017 00000019 00000017 dram_vref_reg_value 0x 00000060\n2D training succeed\naml_ddr_fw_vesion: LPDDR4_PHY_V_0_1_18 build time: Aug 28 2019 13:54:19\nauto size-- 65535DDR cs0 size: 2048MB\nDDR cs1 size: 2048MB\nDMC_DDR_CTRL: 00e00024DDR size: 3928MB\ncs0 DataBus test pass\ncs1 DataBus test pass\ncs0 AddrBus test pass\ncs1 AddrBus test pass\n100bdlr_step_size ps== 420\nresult report\nboot times 0Enable ddr reg access\nLoad FIP HDR from SPI, src: 0x00010000, des: 0x01700000, size: 0x00004000, part: 0\nLoad BL3X from SPI, src: 0x0003c000, des: 0x0172c000, size: 0x000c0000, part: 0\n0.0;M3 CHK:0;cm4_sp_mode 0\nMVN_1=0x00000000\nMVN_2=0x00000000\n[Image: g12b_v1.1.3390-6ac5299 2019-09-26 14:10:05 luan.yuan@droid15-sz]\nOPS=0x10\nring efuse init\nchipver efuse init\n29 0b 10 00 01 05 19 00 00 17 38 33 33 42 42 50\n[0.018960 Inits done]\nsecure task start!\nhigh task start!\nlow task start!\nrun into bl31\nNOTICE:  BL31: v1.3(release):4fc40b1\nNOTICE:  BL31: Built : 15:58:17, May 22 2019\nNOTICE:  BL31: G12A normal boot!\nNOTICE:  BL31: BL33 decompress pass\nERROR:   Error initializing runtime service opteed_fast\nU-Boot 2024.01-rc4+ (Dec 14 2023 - 01:31:33 -0500) Libre Computer AML-A311D-CC\nModel: Libre Computer AML-A311D-CC Alta\nSoC:   Amlogic Meson G12B (A311D) Revision 29:b (10:2)\nDRAM:  2 GiB (effective 3.8 GiB)\nCore:  408 devices, 31 uclasses, devicetree: separate\nWDT:   Not starting watchdog@f0d0\nMMC:   mmc@ffe05000: 1, mmc@ffe07000: 0\nLoading Environment from FAT... Card did not respond to voltage select! : -110\n** Bad device specification mmc 0 **\nCard did not respond to voltage select! : -110\n** Bad device specification mmc 0 **\nCouldn't find partition mmc 0\nCard did not respond to voltage select! : -110\n** Bad device specification mmc 0 **\nCouldn't find partition mmc 0\nError: could not access storage.\nNet:   eth0: ethernet@ff3f0000\nstarting USB...\nBus usb@ff500000: Register 3000140 NbrPorts 3\nStarting the controller\nUSB XHCI 1.10\nscanning bus usb@ff500000 for devices... G12B:BL:6e7c85:2a3b91;FEAT:E0F83180:402000;POC:B;RCY:0;SPINOR:0;0.\nbl2_stage_init 0x01\nbl2_stage_init 0x81\nhw id: 0x0000 - pwm id 0x01\nbl2_stage_init 0xc1\nbl2_stage_init 0x02\nL0:00000000\nL1:20000703\nL2:00008067\nL3:14000000\nB2:00402000\nB1:e0f83180\nTE: 58167\nBL2 Built : 15:22:05, Aug 28 2019. g12b g1bf2b53 - luan.yuan@droid15-sz\nBoard ID = 1\nSet A53 clk to 24M\nSet A73 clk to 24M\nSet clk81 to 24M\nA53 clk: 1200 MHz\nA73 clk: 1200 MHz\nCLK81: 166.6M\nsmccc: 00012abd\nDDR driver_vesion: LPDDR4_PHY_V_0_1_18 build time: Aug 28 2019 15:22:01\nboard id: 1\nLoad FIP HDR from SPI, src: 0x00010000, des: 0xfffd0000, size: 0x00004000, part: 0\nfw parse done\nLoad ddrfw from SPI, src: 0x00030000, des: 0xfffd0000, size: 0x0000c000, part: 0\nLoad ddrfw from SPI, src: 0x00014000, des: 0xfffd0000, size: 0x00004000, part: 0\nPIEI prepare done\nfastboot data load\nfastboot data verify\nverify result: 266\nCfg max: 1, cur: 1. Board id: 255. Force loop cfg\nLPDDR4 probe\nddr clk to 1584MHz\nLoad ddrfw from SPI, src: 0x00018000, des: 0xfffd0000, size: 0x0000c000, part: 0\ndmc_version 0001\nCheck phy result\nINFO : End of CA training\nINFO : End of initialization\nINFO : Training has run successfully!\nCheck phy result\nINFO : End of initialization\nINFO : End of read enable training\nINFO : End of fine write leveling\nINFO : End of Write leveling coarse delay\nINFO : Training has run successfully!\nCheck phy result\nINFO : End of initialization\nINFO : End of read dq deskew training\nINFO : End of MPR read delay center optimization\nINFO : End of write delay center optimization\nINFO : End of read delay center optimization\nINFO : End of max read latency training\nINFO : Training has run successfully!\n1D training succeed\nLoad ddrfw from SPI, src: 0x00024000, des: 0xfffd0000, size: 0x0000c000, part: 0\nCheck phy result\nINFO : End of initialization\nINFO : End of 2D read delay Voltage center optimization\nINFO : End of 2D read delay Voltage center optimization\nINFO : End of 2D write delay Voltage center optimization\nINFO : End of 2D write delay Voltage center optimization\nINFO : Training has run successfully!\nchannel==0\nRxClkDly_Margin_A0==88 ps 9\nTxDqDly_Margin_A0==98 ps 10\nRxClkDly_Margin_A1==88 ps 9\nTxDqDly_Margin_A1==98 ps 10\nTrainedVREFDQ_A0==74\nTrainedVREFDQ_A1==75\nVrefDac_Margin_A0==24\nDeviceVref_Margin_A0==40\nVrefDac_Margin_A1==25\nDeviceVref_Margin_A1==39\nchannel==1\nRxClkDly_Margin_A0==98 ps 10\nTxDqDly_Margin_A0==98 ps 10\nRxClkDly_Margin_A1==88 ps 9\nTxDqDly_Margin_A1==88 ps 9\nTrainedVREFDQ_A0==77\nTrainedVREFDQ_A1==77\nVrefDac_Margin_A0==22\nDeviceVref_Margin_A0==37\nVrefDac_Margin_A1==24\nDeviceVref_Margin_A1==37\ndwc_ddrphy_apb_wr((0<<20)|(2<<16)|(0<<12)|(0xb0):0004\nsoc_vref_reg_value 0x 00000019 0000001a 00000017 00000019 00000018 00000019 00000018 00000018 00000018 00000016 00000018 00000015 00000017 00000019 00000017 00000019 00000018 0000001a 00000019 00000018 00000016 00000018 00000018 00000019 00000018 00000018 00000019 00000019 0000001a 00000017 00000018 00000017 dram_vref_reg_value 0x 00000060\n2D training succeed\naml_ddr_fw_vesion: LPDDR4_PHY_V_0_1_18 build time: Aug 28 2019 13:54:19\nauto size-- 65535DDR cs0 size: 2048MB\nDDR cs1 size: 2048MB\nDMC_DDR_CTRL: 00e00024DDR size: 3928MB\ncs0 DataBus test pass\ncs1 DataBus test pass\ncs0 AddrBus test pass\ncs1 AddrBus test pass\n100bdlr_step_size ps== 420\nresult report\nboot times 0Enable ddr reg access\nLoad FIP HDR from SPI, src: 0x00010000, des: 0x01700000, size: 0x00004000, part: 0\nLoad BL3X from SPI, src: 0x0003c000, des: 0x0172c000, size: 0x000c0000, part: 0\n0.0;M3 CHK:0;cm4_sp_mode 0\nMVN_1=0x00000000\nMVN_2=0x00000000\n[Image: g12b_v1.1.3390-6ac5299 2019-09-26 14:10:05 luan.yuan@droid15-sz]\nOPS=0x10\nring efuse init\nchipver efuse init\n29 0b 10 00 01 05 19 00 00 17 38 33 33 42 42 50\n[0.018961 Inits done]\nsecure task start!\nhigh task start!\nlow task start!\nrun into bl31\nNOTICE:  BL31: v1.3(release):4fc40b1\nNOTICE:  BL31: Built : 15:58:17, May 22 2019\nNOTICE:  BL31: G12A normal boot!\nNOTICE:  BL31: BL33 decompress pass\nERROR:   Error initializing runtime service opteed_fast\nU-Boot 2024.01-rc4+ (Dec 14 2023 - 01:31:33 -0500) Libre Computer AML-A311D-CC\nModel: Libre Computer AML-A311D-CC Alta\nSoC:   Amlogic Meson G12B (A311D) Revision 29:b (10:2)\nDRAM:  2 GiB (effective 3.8 GiB)\nCore:  408 devices, 31 uclasses, devicetree: separate\nWDT:   Not starting watchdog@f0d0\nMMC:   mmc@ffe05000: 1, mmc@ffe07000: 0\nLoading Environment from FAT... Card did not respond to voltage select! : -110\n** Bad device specification mmc 0 **\nCard did not respond to voltage select! : -110\n** Bad device specification mmc 0 **\nCouldn't find partition mmc 0\nCard did not respond to voltage select! : -110\n** Bad device specification mmc 0 **\nCouldn't find partition mmc 0\nError: could not access storage.\nNet:   eth0: ethernet@ff3f0000\nstarting USB...\nBus usb@ff500000: Register 3000140 NbrPorts 3\nStarting the controller\nUSB XHCI 1.10\nscanning bus usb@ff500000 for devices... G12B:BL:6e7c85:2a3b91;FEAT:E0F83180:402000;POC:B;RCY:0;SPINOR:0;0.�!,K��х��}���с0x01\nbl2_stage_init 0x81\nhw id: 0x0000 - pwm id 0x01\nbl2_stage_init 0xc1\nbl2_stage_init 0x02\nL0:00000000\nL1:20000703\nL2:00008067\nL3:14000000\nB2:00402000\nB1:e0f83180\nTE: 58150\nBL2 Built : 15:22:05, Aug 28 2019. g12b g1bf2b53 - luan.yuan@droid15-sz\nBoard ID = 1\nSet A53 clk to 24M\nSet A73 clk to 24M\nSet clk81 to 24M\nA53 clk: 1200 MHz\nA73 clk: 1200 MHz\nCLK81: 166.6M\nsmccc: 00012aac\nDDR driver_vesion: LPDDR4_PHY_V_0_1_18 build time: Aug 28 2019 15:22:01\nboard id: 1\nLoad FIP HDR from SPI, src: 0x00010000, des: 0xfffd0000, size: 0x00004000, part: 0\nfw parse done\nLoad ddrfw from SPI, src: 0x00030000, des: 0xfffd0000, size: 0x0000c000, part: 0\nLoad ddrfw from SPI, src: 0x00014000, des: 0xfffd0000, size: 0x00004000, part: 0\nPIEI prepare done\nfastboot data load\nfastboot data verify\nverify result: 266\nCfg max: 1, cur: 1. Board id: 255. Force loop cfg\nLPDDR4 probe\nddr clk to 1584MHz\nLoad ddrfw from SPI, src: 0x00018000, des: 0xfffd0000, size: 0x0000c000, part: 0\ndmc_version 0001\nCheck phy result\nINFO : End of CA training\nINFO : End of initialization\nINFO : Training has run successfully!\nCheck phy result\nINFO : End of initialization\nINFO : End of read enable training\nINFO : End of fine write leveling\nINFO : End of Write leveling coarse delay\nINFO : Training has run successfully!\nCheck phy result\nINFO : End of initialization\nINFO : End of read dq deskew training\nINFO : End of MPR read delay center optimization\nINFO : End of write delay center optimization\nINFO : End of read delay center optimization\nINFO : End of max read latency training\nINFO : Training has run successfully!\n1D training succeed\nLoad ddrfw from SPI, src: 0x00024000, des: 0xfffd0000, size: 0x0000c000, part: 0\nCheck phy result\nINFO : End of initialization\nINFO : End of 2D read delay Voltage center optimization\nINFO : End of 2D read delay Voltage center optimization\nINFO : End of 2D write delay Voltage center optimization\nINFO : End of 2D write delay Voltage center optimization\nINFO : Training has run successfully!\nchannel==0\nRxClkDly_Margin_A0==88 ps 9\nTxDqDly_Margin_A0==98 ps 10\nRxClkDly_Margin_A1==88 ps 9\nTxDqDly_Margin_A1==98 ps 10\nTrainedVREFDQ_A0==74\nTrainedVREFDQ_A1==74\nVrefDac_Margin_A0==25\nDeviceVref_Margin_A0==40\nVrefDac_Margin_A1==25\nDeviceVref_Margin_A1==40\nchannel==1\nRxClkDly_Margin_A0==98 ps 10\nTxDqDly_Margin_A0==98 ps 10\nRxClkDly_Margin_A1==98 ps 10\nTxDqDly_Margin_A1==88 ps 9\nTrainedVREFDQ_A0==77\nTrainedVREFDQ_A1==77\nVrefDac_Margin_A0==23\nDeviceVref_Margin_A0==37\nVrefDac_Margin_A1==22\nDeviceVref_Margin_A1==37\ndwc_ddrphy_apb_wr((0<<20)|(2<<16)|(0<<12)|(0xb0):0004\nsoc_vref_reg_value 0x 00000019 0000001a 00000017 00000019 00000018 00000019 00000018 00000017 00000017 00000016 00000017 00000015 00000018 00000019 00000017 00000019 00000018 00000019 0000001a 00000018 00000016 00000018 00000018 00000019 00000018 00000018 00000019 00000019 0000001a 00000016 00000018 00000017 dram_vref_reg_value 0x 00000060\n2D training succeed\naml_ddr_fw_vesion: LPDDR4_PHY_V_0_1_18 build time: Aug 28 2019 13:54:19\nauto size-- 65535DDR cs0 size: 2048MB\nDDR cs1 size: 2048MB\nDMC_DDR_CTRL: 00e00024DDR size: 3928MB\ncs0 DataBus test pass\ncs1 DataBus test pass\ncs0 AddrBus test pass\ncs1 AddrBus test pass\n100bdlr_step_size ps== 420\nresult report\nboot times 0Enable ddr reg access\nLoad FIP HDR from SPI, src: 0x00010000, des: 0x01700000, size: 0x00004000, part: 0\nLoad BL3X from SPI, src: 0x0003c000, des: 0x0172c000, size: 0x000c0000, part: 0\n0.0;M3 CHK:0;cm4_sp_mode 0\nMVN_1=0x00000000\nMVN_2=0x00000000\n[Image: g12b_v1.1.3390-6ac5299 2019-09-26 14:10:05 luan.yuan@droid15-sz]\nOPS=0x10\nring efuse init\nchipver efuse init\n29 0b 10 00 01 05 19 00 00 17 38 33 33 42 42 50\n[0.018961 Inits done]\nsecure task start!\nhigh task start!\nlow task start!\nrun into bl31\nNOTICE:  BL31: v1.3(release):4fc40b1\nNOTICE:  BL31: Built : 15:58:17, May 22 2019\nNOTICE:  BL31: G12A normal boot!\nNOTICE:  BL31: BL33 decompress pass\nERROR:   Error initializing runtime service opteed_fast\nU-Boot 2024.01-rc4+ (Dec 14 2023 - 01:31:33 -0500) Libre Computer AML-A311D-CC\nModel: Libre Computer AML-A311D-CC Alta\nSoC:   Amlogic Meson G12B (A311D) Revision 29:b (10:2)\nDRAM:  2 GiB (effective 3.8 GiB)\nCore:  408 devices, 31 uclasses, devicetree: separate\nWDT:   Not starting watchdog@f0d0\nMMC:   mmc@ffe05000: 1, mmc@ffe07000: 0\nLoading Environment from FAT... Card did not respond to voltage select! : -110\n** Bad device specification mmc 0 **\nCard did not respond to voltage select! : -110\n** Bad device specification mmc 0 **\nCouldn't find partition mmc 0\nCard did not respond to voltage select! : -110\n** Bad device specification mmc 0 **\nCouldn't find partition mmc 0\nError: could not access storage.\nNet:   eth0: ethernet@ff3f0000\nstarting USB...\nBus usb@ff500000: Register 3000140 NbrPorts 3\nStarting the controller\nUSB XHCI 1.10\nscanning bus usb@ff500000 for devices... 3 USB Device(s) found\nscanning usb for storage devices... 0 Storage Device(s) found\nHit any key to stop autoboot:  1\n??? 0\n=> setenv autoload no\nsetenv autoload no\n=> setenv initrd_high 0xffffffff\nsetenv initrd_high 0xffffffff\n=> setenv fdt_high 0xffffffff\nsetenv fdt_high 0xffffffff\n=> dhcp\ndhcp\nSpeed: 1000, full duplex\nBOOTP broadcast 1\nDHCP client bound to address 192.168.7.181 (238 ms)\n=> setenv serverip 192.168.6.2\nsetenv serverip 192.168.6.2\n=> tftpboot 0x01080000 1072814/tftp-deploy-gc_l3wwh/kernel/uImage\ntftpboot 0x01080000 1072814/tftp-deploy-gc_l3wwh/kernel/uImage\nSpeed: 1000, full duplex\nUsing ethernet@ff3f0000 device\nTFTP from server 192.168.6.2; our IP address is 192.168.7.181\nFilename '1072814/tftp-deploy-gc_l3wwh/kernel/uImage'.\nLoad address: 0x1080000\nLoading: *?T T T T T T T T T T\nRetry count exceeded; starting again\n=>\n",
#     "log_url": "https://kciapistagingstorage1.file.core.windows.net/production/baseline-arm64-broonie-678ee7b046f65f378a18d33e/log.txt.gz?sv=2022-11-02&ss=f&srt=sco&sp=r&se=2026-10-18T13:36:18Z&st=2024-10-17T05:36:18Z&spr=https&sig=xFxYOOh5uXJWeN9I3YKAUvpGGQivo89HKZbD78gcxvc%3D",
#     "misc": {
#         "arch": "arm64",
#         "compiler": "gcc-12",
#         "error_code": "Infrastructure",
#         "error_msg": "matched a bootloader error message: 'Retry count exceeded' (4)",
#         "kernel_type": "image",
#         "runtime": "lava-broonie"
#     },
#     "output_files": [
#         {
#             "name": "callback_data",
#             "url": "https://kciapistagingstorage1.file.core.windows.net/production/baseline-arm64-broonie-678ee7b046f65f378a18d33e/lava_callback.json.gz?sv=2022-11-02&ss=f&srt=sco&sp=r&se=2026-10-18T13:36:18Z&st=2024-10-17T05:36:18Z&spr=https&sig=xFxYOOh5uXJWeN9I3YKAUvpGGQivo89HKZbD78gcxvc%3D"
#         }
#     ],
#     "path": "boot",
#     "regression_type": "unstable",
#     "start_time": "2025-01-21T00:17:52.855000Z",
#     "status": "MISS",
#     "status_history": [
#         {
#             "field_timestamp": "2025-01-21T00:24:05.705873Z",
#             "git_commit_hash": "d73a4602e973e9e922f00c537a4643907a547ade",
#             "id": "maestro:678ee7b046f65f378a18d33e",
#             "status": "MISS"
#         },
#         {
#             "field_timestamp": "2025-01-20T15:22:05.948330Z",
#             "git_commit_hash": "64ff63aeefb03139ae27454bd4208244579ae88e",
#             "id": "maestro:678e592546f65f378a15d3c1",
#             "status": "PASS"
#         },
#         {
#             "field_timestamp": "2025-01-20T13:10:01.093219Z",
#             "git_commit_hash": "5fe71fda89745fc3cd95f70d06e9162b595c3702",
#             "id": "maestro:678e4a0946f65f378a158459",
#             "status": "PASS"
#         },
#         {
#             "field_timestamp": "2025-01-20T11:26:01.225745Z",
#             "git_commit_hash": "45bd1c5ba7580f612e46f3c6cb430c64adfd0294",
#             "id": "maestro:678e30f546f65f378a151e05",
#             "status": "FAIL"
#         },
#         {
#             "field_timestamp": "2025-01-19T03:10:05.623899Z",
#             "git_commit_hash": "59372af69d4d71e6487614f1b35712cf241eadb4",
#             "id": "maestro:678c6b447adb323264c66a80",
#             "status": "PASS"
#         },
#         {
#             "field_timestamp": "2025-01-18T05:40:01.280900Z",
#             "git_commit_hash": "41c5d104f338b21b98aee5a207336c281325583f",
#             "id": "maestro:678b3dd77adb323264c529af",
#             "status": "PASS"
#         },
#         {
#             "field_timestamp": "2025-01-18T04:36:00.846297Z",
#             "git_commit_hash": "3df22e75102785bac1768f7eeabbc45c01a6e7f4",
#             "id": "maestro:678b2de47adb323264c4e58f",
#             "status": "FAIL"
#         },
#         {
#             "field_timestamp": "2025-01-17T05:49:01.279497Z",
#             "git_commit_hash": "7d2eba0f83a59d360ed1e77ed2778101a6e3c4a1",
#             "id": "maestro:6789eea37adb323264c10476",
#             "status": "PASS"
#         },
#         {
#             "field_timestamp": "2025-01-17T03:09:01.100522Z",
#             "git_commit_hash": "3030e3d57ba8d0f59bd8162b3b1f3f7ee273f280",
#             "id": "maestro:6789c9027adb323264c0333f",
#             "status": "PASS"
#         },
#         {
#             "field_timestamp": "2025-01-16T21:42:01.164556Z",
#             "git_commit_hash": "2ee738e90e80850582cbe10f34c6447965c1d87b",
#             "id": "maestro:67897c4f7adb323264bef0b4",
#             "status": "PASS"
#         }
#     ],
#     "tree_name": "net-next"
# }
