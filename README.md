# ZigsMon aka: GeriMon
Human monitor for the elderly. Work for ECU Midwifery and Nursing Dept. Was to enable older Austrailians to stay at home and out of care / institutions for longer wilst still being monitored by Nursing / Care staff. System records daily movement and activity to be referenced by qualified staff before weekly visits.  
COVID ended my employment with Edith Cowan University. Obviously working closely with the elderly in a pandemic is not a good idea.
Anyway, I put a lot of work into this and I don't expect them to employ me again to continue the work so here is the code. It's a bit all over the shop (functional code, classes, files of function not a proper structure), this is because it was a learning experience and I wanted to have classes from the start but I had to work out how it worked first then the pandemic struck. Pretty easy to change anyway.
Requires a Digi Zigbee Gateway (Industrial version) supports HA and IAS devices. 
Idea is all data is uploaded to a database. If I can find the DB script I used I will upload it also.
![image](https://user-images.githubusercontent.com/43127610/131336161-2ea93296-558a-4e84-9159-7226f08cb7af.png)  

All exta libraries must go into a zip file on the device (ie Multiprocessing). Runs python 2, so code is the old way and will not work on version 3.  
I have used the code functions and to create a home automation example, just a motion sensor turning on a zigbee plug. So if thats your thing have a look.  
