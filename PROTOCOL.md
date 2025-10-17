# EZCOO Protocol Documentation

Collected from https://docs.pikvm.org/ezcoo/

**Tested Devices:** EZCOO EZ-SW41HA-KVMU3L and EZ-SW41HA-KVMU3P with firmware version 2.03

## V1 Protocol

**Source:** https://docs.pikvm.org/ezcoo/ezcoo1.docx (A copy can be found in the /docs directory)

### Overview

The EZCOO switch can be controlled and upgraded via the Micro-USB port. Connect a Micro-USB cable from the USB port on the front panel to your Windows PC (Laptop/Desktop). The driver will install automatically when the matrix is connected - please wait for a minute.

If you can't find the device, please find the driver and install manually:
https://www.easycoolav.com/art/tech-support-a0040.html

### Control Interface

**Serial Parameters:**
- Baud Rate: 57600bps
- Data: 8bit
- Parity: None
- Stop: 1bit

**Software:** Use UartAssist.exe with the correct parameters. Download from:
https://www.easycoolav.com/art/tech-support-a0040.html

### API Commands

> **Note:** Press "Enter" key after each command

| Command | Function |
|---------|----------|
| `H` | Get system help (command list) |
| `SET AUTO OFF` | Turn off auto switch function |
| `SET AUTO ON` | Turn on auto switch function (Default) |
| `SET RST` | Reset the switch to factory defaults |
| `SET OUT1 VS IN y` | Set output x to input y (X=1, y=1-4) |
| `SET CAS EN` | Set Cascade mode enable (Turn off HDCP) |
| `SET CAS DIS` | Set Cascade mode Disable (Turn on HDCP) |
| `SET IN x EDID y` | Set Input x EDID {x=[0~4] (0=ALL), y=[0~32]} |

#### EDID List

| ID | Description |
|----|-------------|
| 0 | 1080P_2CH (PCM) |
| 1 | 1080P_6CH |
| 2 | 1080P_8CH |
| 3 | 1080P_3D_2CH(PCM) |
| 4 | 1080P_3D_6CH |
| 5 | 1080P_3D_8CH |
| 6 | 4K30Hz_3D_2CH (PCM) |
| 7 | 4K30HZ_3D_6CH |
| 8 | 4K30HZ_3D_8CH |
| 9 | 4K60Hz(Y420)_3D_2CH(PCM) |
| 10 | 4K60Hz(Y420)_3D_6CH |
| 11 | 4K60Hz(Y420)_3D_8CH |
| 12 | 4K60HZ_3D_2CH |
| 13 | 4K60HZ_3D_6CH |
| 14 | 4K60HZ_3D_8CH |
| 15 | 1080P_2CH(PCM)_HDR |
| 16 | 1080P_6CH_HDR |
| 17 | 1080P_8CH_HDR |
| 18 | 1080P_3D_2CH(PCM)_HDR |
| 19 | 1080P_3D_6CH_HDR |
| 20 | 1080P_3D_8CH_HDR |
| 21 | 4K30Hz_3D_2CH(PCM)_HDR |
| 22 | 4K30Hz_3D_6CH_HDR |
| 23 | 4K30Hz_3D_8CH_HDR |
| 24 | 4K60Hz(Y420)_3D_2CH_HDR |
| 25 | 4K60Hz(Y420)_3D_6CH_HDR |
| 26 | 4K60Hz(Y420)_3D_8CH_HDR |
| 27 | 4K60Hz_3D_2CH(PCM)_HDR |
| 28 | 4K60Hz_3D_6CH_HDR |
| 29 | 4K60Hz_3D_8CH_HDR |
| 30 | USER1_EDID |
| 31 | USER2_EDID |
| 32 | USER3_EDID(BY_PASS) |

### HDCP Control via Front Panel Button

#### Turn on HDCP (default)
1. Press and hold down the switch button on the front panel
2. Power on the switch while keeping the button held
3. Keep holding the button for about 5 seconds
4. All LEDs will intermittently flicker - this indicates HDCP is available

#### Turn off HDCP
1. Press and hold down the switch button on the front panel
2. Power on the switch while keeping the button held
3. Keep holding the button for about 5 seconds
4. All LEDs will cycle in order - this indicates HDCP has been removed

> **Tip:** For more commands, send "H" to get the command list.

### Firmware Upgrade

**Serial Parameters:**
- Baud Rate: 57600bps
- Data: 8bit
- Parity: None
- Stop: 1bit

**Upgrade Process:**

1. **Prepare for ISP Mode:**
   - Open UartAssist.exe with correct parameters
   - Send command: `ISP 32 1` + Enter
   - Click Send button
   - You will see "JUMP TO ISP MODE..."
   - Click Close
   - All LEDs on the switch will turn off

   > ⚠️ **WARNING:** DO NOT remove any connections during this process

2. **Flash Firmware:**
   - Open FlyMcu.exe
   - Follow this order:
     1. Search the port
     2. Select 57600 bps
     3. Load the .hex file
     4. Start ISP (update)

## V2 Protocol (F/W 1.20)

### Overview

All commands start with a prefix system address `zz` if using addresses [01-99]. For single device operation, use address 00.

### System Commands

| Command | Function | Parameters |
|---------|----------|------------|
| `EZH` | Help | - |
| `EZSTA` | Show Global System Status | - |
| `EZS RST` | Reset to Factory Defaults | - |
| `EZS ADDR xx` | Set System Address | xx=[00~99] (00=Single) |
| `EZS CAS EN/DIS` | Set Cascade Mode Enable/Disable | EN or DIS |
| `EZS OUTx VS INy` | Set Output x To Input y | x=[0~2] (0=ALL), y=[1~4] |
| `EZS IR SYS xx.yy` | Set IR Custom Code | xx=[00-FFH], yy=[00-FFH] |
| `EZS IR OUTx INy CODE zz` | Set IR Data Code | x=[1~2], y=[1~4], zz=[00-FFH] |
| `EZG ADDR` | Get System Address | - |
| `EZG STA` | Get System Status | - |
| `EZG CAS` | Get Cascade Mode Status | - |
| `EZG OUTx VS` | Get Output x Video Route | x=[0~2] (0=ALL) |
| `EZG IR SYS` | Get IR Custom Code | - |
| `EZG IR OUTx INy CODE` | Get IR Data Code | x=[1~2], y=[1~4] |
| `EZS OUTx VIDEOy` | Set Output VIDEO Mode | x=[1~2], y=[1~2] (1=BYPASS, 2=4K->2K) |

### Input Setup Commands

> **Note:** Input number (x) = HDMI(x), x=1

| Command | Function | Parameters |
|---------|----------|------------|
| `EZS INx EDID y` | Set Input x EDID | x=[0~4] (0=ALL), y=[0~15] |
| `EZG INx EDID` | Get Input x EDID Index | x=[0~4] (0=ALL) |

#### V2 EDID List

| ID | Description |
|----|-------------|
| 0 | EDID_BYPASS |
| 1 | 1080P_2CH_HDR |
| 2 | 1080P_6CH_HDR |
| 3 | 1080P_8CH_HDR |
| 4 | 1080P_3D_2CH_HDR |
| 5 | 1080P_3D_6CH_HDR |
| 6 | 1080P_3D_8CH_HDR |
| 7 | 4K30HZ_3D_2CH_HDR |
| 8 | 4K30HZ_3D_6CH_HDR |
| 9 | 4K30HZ_3D_8CH_HDR |
| 10 | 4K60HzY420_3D_2CH_HDR |
| 11 | 4K60HzY420_3D_6CH_HDR |
| 12 | 4K60HzY420_3D_8CH_HDR |
| 13 | 4K60HZ_3D_2CH_HDR |
| 14 | 4K60HZ_3D_6CH_HDR |
| 15 | 4K60HZ_3D_8CH_HDR |
| 16 | H4K_DOLBY_VISION_ATMOS |

### Original V2 Help Output

```
===============================================================================================================================
=********************************************************Systems HELP*********************************************************=
=-----------------------------------------------------------------------------------------------------------------------------=
=                        System Address = 00           F/W Version : 1.20                                                     =
=   Azz                           :  All Commands start by Prefix System Address zz, if [01-99]                               =
=-----------------------------------------------------------------------------------------------------------------------------=
=   EZH                           : Help                                                                                      =
=   EZSTA                         : Show Global System Status                                                                 =
=   EZS RST                       : Reset to Factory Defaults                                                                 =
=   EZS ADDR xx                   : Set System Address to xx {xx=[00~99](00=Single)}                                          =
=   EZS CAS EN/DIS                : Set Cascade Mode Enable/Disable                                                           =
=   EZS OUTx VS INy               : Set Output x To Input y{x=[0~2](0=ALL), y=[1~4]}                                          =
=   EZS IR SYS xx.yy              : Set IR Custom Code{xx=[00-FFH],yy=[00-FFH]}                                               =
=   EZS IR OUTx INy CODE zz       : Set IR Data Code{x=[1~2],y=[1~4],zz=[00-FFH]}                                             =
=   EZG ADDR                      : Get System Address                                                                        =
=   EZG STA                       : Get System System Status                                                                  =
=   EZG CAS                       : Get Cascade Mode Status                                                                   =
=   EZG OUTx VS                   : Get Output x Video Route{x=[0~2](0=ALL)}                                                  =
=   EZG IR SYS                    : Get IR Custom Code                                                                        =
=   EZG IR OUTx INy CODE          : Get IR Data Code{x=[1~2],y=[1~4]}                                                         =
=   EZS OUTx VIDEOy               : Set Output VIDEO Mode                                                                     =
=                                   {x=[1~2], y=[1~2](1=BYPASS,2=4K->2K)}                                                     =
=-----------------------------------------------------------------------------------------------------------------------------=
=Input Setup Commands:(Note:input number(x)=HDMI(x),x=1)                                                                      =
=   EZS INx EDID y                : Set Input x EDID{x=[0~4](0=ALL), y=[0~15]}                                                =
=                                   0:EDID_BYPASS         1:1080P_2CH_HDR          2:1080P_6CH_HDR        3:1080P_8CH_HDR     =
=                                   4:1080P_3D_2CH_HDR    5:1080P_3D_6CH_HDR   6:1080P_3D_8CH_HDR                             =
=                                   7:4K30HZ_3D_2CH_HDR  8:4K30HZ_3D_6CH_HDR  9:4K30HZ_3D_8CH_HDR                             =
=                                   10:4K60HzY420_3D_2CH_HDR  11:4K60HzY420_3D_6CH_HDR  12:4K60HzY420_3D_8CH_HDR              =
=                                   13:4K60HZ_3D_2CH_HDR  14:4K60HZ_3D_6CH_HDR  15:4K60HZ_3D_8CH_HDR                          =
=                                   16:H4K_DOLBY_VISION_ATMOS                                                                 =
=   EZG INx EDID                  : Get Input x EDID  Index{x=[0~4](0=ALL)}                                                   =
=-----------------------------------------------------------------------------------------------------------------------------=
=*****************************************************************************************************************************=
===============================================================================================================================
```

## V2 Protocol (F/W 2.03)

**Connection Settings:**
- Baudrate: 115200
- Line ending: LF (\n)
- Timeout: 1.0s

### System Control Commands

| Command | Function | Parameters |
|---------|----------|------------|
| `EZH` | Help | - |
| `EZSTA` | Show Global System Status | - |
| `EZS RST` | Reset to Factory Defaults | - |
| `EZS RBT` | Set System to Reboot | - |
| `EZS ADDR xx` | Set System Address | xx=[00~99] (00=Single) |
| `EZS AUTO ON/OFF` | Set Auto Switch Mode On/Off | ON or OFF |
| `EZG ADDR` | Get System Address | - |
| `EZG STA` | Get System Status | - |
| `EZG INx SIG STA` | Get Input x Signal Status | x=[0~4] (0=ALL) |
| `EZG AUTO MODE` | Get Auto Switch Mode Status | - |

### Output Setup Commands

> **Note:** Output number (x) = HDMI(x), x=1

| Command | Function | Parameters |
|---------|----------|------------|
| `EZS OUTx VS INy` | Set Output x To Input y | x=[0~1] (0=ALL), y=[1~4] |
| `EZS OUTx STREAM ON/OFF` | Set Output x Stream ON/OFF | x=[0~1] (0=ALL) |
| `EZG OUTx VS` | Get Output x Video Route | x=[0~1] (0=ALL) |
| `EZG OUTx STREAM` | Get Output x Stream ON/OFF Status | x=[0~1] (0=ALL) |

### Input Setup Commands

| Command | Function | Parameters |
|---------|----------|------------|
| `EZS INx EDID y` | Set Input x EDID | x=[0] (0=ALL), y=[0~29] |
| `EZS INx EDID CY OUTy` | Copy Output y EDID To Input x (USER1 BUF) | x=[0] (0=ALL), y=[1] |
| `EZG INx EDID` | Get Input x EDID Index | x=[0] (0=ALL) |

#### Verified EDID List (30 entries: 0-29)

| ID | Description |
|----|-------------|
| 0 | 1080P_2CH |
| 1 | 1080P_6CH |
| 2 | 1080P_8CH |
| 3 | 1080P_3D_2CH |
| 4 | 1080P_3D_6CH |
| 5 | 1080P_3D_8CH |
| 6 | 4K30HZ_3D_2CH |
| 7 | 4K30HZ_3D_6CH |
| 8 | 4K30HZ_3D_8CH |
| 9 | 4K60HzY420_3D_2CH |
| 10 | 4K60HzY420_3D_6CH |
| 11 | 4K60HzY420_3D_8CH |
| 12 | 4K60HZ_3D_2CH |
| 13 | 4K60HZ_3D_6CH |
| 14 | 4K60HZ_3D_8CH |
| 15 | 1080P_2CH_HDR |
| 16 | 1080P_6CH_HDR |
| 17 | 1080P_8CH_HDR |
| 18 | 1080P_3D_2CH_HDR |
| 19 | 1080P_3D_6CH_HDR |
| 20 | 1080P_3D_8CH_HDR |
| 21 | 4K30HZ_3D_2CH_HDR |
| 22 | 4K30HZ_3D_6CH_HDR |
| 23 | 4K30HZ_3D_8CH_HDR |
| 24 | 4K60HzY420_3D_2CH_HDR |
| 25 | 4K60HzY420_3D_6CH_HDR |
| 26 | 4K60HzY420_3D_8CH_HDR |
| 27 | 4K60HZ_3D_2CH_HDR |
| 28 | 4K60HZ_3D_6CH_HDR |
| 29 | 4K60HZ_3D_8CH_HDR |

### IR Code Setup Commands

| Command | Function | Parameters |
|---------|----------|------------|
| `EZS IR SYS xx.yy` | Set IR Custom Code | xx=[00-FFH], yy=[00-FFH] |
| `EZS IR OUTx UD CODE yy.zz` | Set IR OUTx Up/Down Code | x=[1], yy=[00-FFH], zz=[00-FFH] |
| `EZS IR OUTx INy CODE zz` | Set IR OUTx INy Code | x=[1], y=[1~4], zz=[00-FFH] |
| `EZS IR POW xx` | Set IR Power Code | xx=[00-FFH] |
| `EZG IR SYS` | Get IR Custom Code | - |
| `EZG IR OUTx UD CODE` | Get IR OUTx Up/Down Code | x=[1] |
| `EZG IR OUTx INy CODE` | Get IR OUTx INy Code | x=[1], y=[1~4] |
| `EZG IR POW` | Get IR Power Code | - |

### Actual Device Help Output (F/W 2.03)

```
===============================================================================================================================
=********************************************************Systems HELP*********************************************************=
=-----------------------------------------------------------------------------------------------------------------------------=
=                        System Address = 00           F/W Version : 2.03                                                     =
=   Azz                           :  All Commands start by Prefix System Address zz, if [01-99]                               =
=-----------------------------------------------------------------------------------------------------------------------------=
=System Control Setup Commands:                                                                                               =
=   EZH                           : Help                                                                                      =
=   EZSTA                         : Show Global System Status                                                                 =
=   EZS RST                       : Reset to Factory Defaults                                                                 =
=   EZS RBT                       : Set Systerm to Reboot                                                                     =
=   EZS ADDR xx                   : Set System Address to xx {xx=[00~99](00=Single)}                                          =
=   EZS AUTO ON/OFF               : Set Auto Switch Mode On/Off                                                               =
=   EZG ADDR                      : Get System Address                                                                        =
=   EZG STA                       : Get System System Status                                                                  =
=   EZG INx SIG STA               : Get Input x Signal Status{x=[0~4](0=ALL)}                                                 =
=   EZG AUTO MODE                 : Get Auto Switch Mode Status                                                               =
=-----------------------------------------------------------------------------------------------------------------------------=
=Output Setup Command : (Note:output number(x)=HDMI(x),x=1)                                                                   =
=   EZS OUTx VS INy               : Set Output x To Input y {x=[0~1](0=ALL), y=[1~4]}                                         =
=   EZS OUTx STREAM ON/OFF        : Set Output x Stream ON/OFF{x=[0~1](0=ALL)}                                                =
=   EZG OUTx VS                   : Get Output x Video Route{x=[0~1](0=ALL)}                                                  =
=   EZG OUTx STREAM               : Get Output x Stream ON/OFF Status{x=[0~1](0=ALL)}                                         =
=-----------------------------------------------------------------------------------------------------------------------------=
=Input Setup Commands:                                                                                                        =
=   EZS INx EDID y                : Set Input x EDID{x=[0](0=ALL), y=[0~29]}                                                  =
=                                   0:1080P_2CH          1:1080P_6CH          2:1080P_8CH          3:1080P_3D_2CH             =
=                                   4:1080P_3D_6CH       5:1080P_3D_8CH       6:4K30HZ_3D_2CH      7:4K30HZ_3D_6CH            =
=                                   8:4K30HZ_3D_8CH      9:4K60HzY420_3D_2CH  10:4K60HzY420_3D_6CH 11:4K60HzY420_3D_8CH       =
=                                   12:4K60HZ_3D_2CH     13:4K60HZ_3D_6CH     14:4K60HZ_3D_8CH     15:1080P_2CH_HDR           =
=                                   16:1080P_6CH_HDR     17:1080P_8CH_HDR     18:1080P_3D_2CH_HDR  19:1080P_3D_6CH_HDR        =
=                                   20:1080P_3D_8CH_HDR  21:4K30HZ_3D_2CH_HDR 22:4K30HZ_3D_6CH_HDR 23:4K30HZ_3D_8CH_HDR       =
=                                   24:4K60HzY420_3D_2CH_HDR      25:4K60HzY420_3D_6CH_HDR      26:4K60HzY420_3D_8CH_HDR      =
=                                   27:4K60HZ_3D_2CH_HDR          28:4K60HZ_3D_6CH_HDR          29:4K60HZ_3D_8CH_HDR          =
=   EZS INx EDID CY OUTy          : Copy Output y EDID To Input x(USER1 BUF){x=[0](0=ALL), y=[1]}                             =
=   EZG INx EDID                  : Get Input x EDID  Index{x=[0](0=ALL)}                                                     =
=-----------------------------------------------------------------------------------------------------------------------------=
=IR Code Setup Command:                                                                                                       =
=   EZS IR SYS xx.yy              : Set IR Custom Code{xx=[00-FFH],yy=[00-FFH]}                                               =
=   EZS IR OUTx UD CODE yy.zz     : Set IR OUTx Up/Down Code{x=[1],yy=[00-FFH],zz=[00-FFH]}                                   =
=   EZS IR OUTx INy CODE zz       : Set IR OUTx INy Code{x=[1],y=[1~4],zz=[00-FFH]}                                           =
=   EZS IR POW xx                 : Set IR Power Code{xx=[00-FFH]}                                                            =
=   EZG IR SYS                    : Get IR Custom Code                                                                        =
=   EZG IR OUTx UD CODE           : Get IR OUTx Up/Down Code{x=[1]}                                                           =
=   EZG IR OUTx INy CODE          : Get IR OUTx INy Code{x=[1],y=[1~4]}                                                       =
=   EZG IR POW                    : Get IR Power Code                                                                         =
=-----------------------------------------------------------------------------------------------------------------------------=
=*****************************************************************************************************************************=
===============================================================================================================================
```