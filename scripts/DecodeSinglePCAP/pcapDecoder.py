#Classic J2735 Payload Decoder - Single Message
import J2735_201603_combined
import signal, sys
from binascii import hexlify, unhexlify

def signal_handler(sig, frame):
    print('\nExiting')
    sys.exit(0)


payload = input('Enter your J2735 Payload:\n')
decode = J2735_201603_combined.DSRC.MessageFrame
decode.from_uper(unhexlify(payload))
decodedStr = str(decode())
print(decodedStr, '\n')

# if no issues with decoding, print
if "b'" not in decodedStr: print(decodedStr, '\n') 

# decoding issues found, fix and update message
else: 
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

    while("b'" in decodedStr):
        decodedStr = fixID(decodedStr)
        #print('New string: ', decodedStr, '\n')
    print('New string: ', decodedStr, '\n')


signal.signal(signal.SIGINT, signal_handler)
print('<Ctrl+C> to exit')
signal.pause()