import bluetooth
import bluetooth._bluetooth as bluez
import struct
import sys

def device_inquiry_with_rssi(sock):
    # Set inquiry parameters
    duration = 8  # ~10.24 seconds; 1.28 * 8
    max_responses = 255
    cmd_pkt = struct.pack("BBBBB", 0x33, 0x8b, 0x9e, duration, max_responses)
    bluez.hci_send_cmd(sock, bluez.OGF_LINK_CTL, bluez.OCF_INQUIRY, cmd_pkt)

    # Process inquiry results
    results = []
    done = False
    while not done:
        pkt = sock.recv(255)
        ptype, event, plen = struct.unpack("BBB", pkt[:3])
        if event == bluez.EVT_INQUIRY_RESULT_WITH_RSSI:
            pkt = pkt[3:]
            nrsp = bluetooth.get_byte(pkt[0])
            for i in range(nrsp):
                addr = bluez.ba2str(pkt[1+6*i:1+6*i+6])
                rssi = bluetooth.byte_to_signed_int(bluetooth.get_byte(pkt[1 + 13 * nrsp + i]))
                results.append((addr, rssi))
                print(f"Discovered: {addr}, RSSI: {rssi}")
        elif event == bluez.EVT_INQUIRY_COMPLETE:
            done = True

    return results

def main():
    # Open Bluetooth device
    dev_id = 0
    try:
        sock = bluez.hci_open_dev(dev_id)
    except:
        print("Error accessing Bluetooth device.")
        sys.exit(1)

    # Start device inquiry
    print("Scanning for devices...")
    device_inquiry_with_rssi(sock)
    print("Scan complete.")

if __name__ == "__main__":
    main()
