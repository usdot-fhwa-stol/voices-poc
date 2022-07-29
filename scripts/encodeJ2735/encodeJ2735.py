# SAE J2735 Encoder
import J2735
import ast
import signal, sys
from binascii import hexlify

def signal_handler(sig, frame):
    print('\nExiting')
    sys.exit(0)


msgIn = input('Enter your JSON J2735 message:\n')
updatedMsg = msgIn.replace("\'", "\"")
updatedMsg = updatedMsg.strip("\n")
msg = ast.literal_eval(updatedMsg)
msgFrame = J2735.DSRC.MessageFrame
msgFrame.set_val(msg)
msgFrameUper = msgFrame.to_uper()
encodedMsg = hexlify(msgFrameUper)
print("\nEncoded Hex:\n", encodedMsg)


signal.signal(signal.SIGINT, signal_handler)
print('\n<Ctrl+C> to exit')
signal.pause()