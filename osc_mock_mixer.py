#!/usr/bin/env python3.14

# Depends:
# pip install python-osc

from socket import socket, AF_INET, SOCK_DGRAM
from pythonosc.osc_message_builder import OscMessageBuilder
from pythonosc.osc_packet import OscPacket


PORT = 10024

# Simulated mixer state.
# Addresses not listed here default to 0 (muted).
state = {}


def send_value(sock, address, value, destination):
    builder = OscMessageBuilder(address=address)
    builder.add_arg(value)
    msg = builder.build()

    sock.sendto(msg.dgram, destination)


def main():
    with socket(AF_INET, SOCK_DGRAM) as sock:
        sock.bind(("", PORT))

        print("OSC Mock Mixer")
        print(f"Listening on UDP port {PORT}")
        print("Press Ctrl+C to exit.\n")

        while True:
            data, sender = sock.recvfrom(4096)

            packet = OscPacket(data)

            for timed in packet.messages:
                msg = timed.message
                address = msg.address
                params = msg.params

                print(f"Received: {address}", end="")

                if params:
                    print(f"  Value: {params}")
                else:
                    print("  Query")

                # -------------------------
                # Query
                # -------------------------

                if not params:
                    value = state.get(address, 0)

                    print(f"  -> Returning: {value}")

                    send_value(
                        sock,
                        address,
                        value,
                        sender
                    )

                # -------------------------
                # Set value
                # -------------------------

                else:
                    value = params[0]

                    state[address] = value

                    print(f"  -> State changed to: {value}")

                    # Return the new value immediately.
                    send_value(
                        sock,
                        address,
                        value,
                        sender
                    )

                print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nMock mixer stopped.")