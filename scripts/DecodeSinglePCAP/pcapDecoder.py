#Single PCAP Payload Decoder
import J2735_201603_combined
import signal, sys
from binascii import hexlify, unhexlify


def signal_handler(sig, frame) :
    print('\nExiting')
    sys.exit(0)

def fixID(anyID) :
    begID = anyID.find("b'") + 2
    endID = anyID.find("'", begID)
    badID = anyID[begID:endID]
    newID = badID.replace("\\x", '')

    i = 33
    for x in range(78): # range is # of total unwanted ascii characters (33-47, 58-96, 103-126)
        if chr(i) in newID:
            num = newID.index(chr(i))
            hexed = hexlify(str.encode(newID[num]))
            newID = newID.replace(newID[num], hexed.decode('utf-8'))
            i = i+1
        elif (i == 47)  : i = 58
        elif (i == 96)  : i = 103
        elif (i == 126) : i = 33
        else: i = i+1

    newString = anyID[:begID-2] + newID + anyID[endID+1:]

    return newString

# decode message and convert to string from dictionary
payload = input('Enter your PCAP Payload:\n')
msg = unhexlify(payload.strip(' \n'))
utf = msg.decode('utf-8')
data = utf.strip(' \n')
print('MSG:', data, '\n')
decode = J2735_201603_combined.DSRC.MessageFrame
un_hex = unhexlify(data)
decode.from_uper(un_hex) 
decodedStr = str(decode())

# if no issues with decoding, print
if "b'" not in decodedStr: print(decodedStr, '\n') 

# decoding issues found, fix and update message
else: 
    while("b'" in decodedStr):
        decodedStr = fixID(decodedStr)
        #print('New string: ', decodedStr, '\n')
    print('New string: ', decodedStr, '\n')

signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C to exit')
signal.pause()
