from typing import Union
import socket
import struct


def intToVarInt(value: int) -> bytes:
    if (value < 0):
        value += 1 << 32
    
    buffer = b""
    for i in range(10):
        byte = value & 0x7F
        value >>= 7
        buffer += struct.pack(">B", byte | (0x80 if value > 0 else 0))
        if value == 0:
            break
    return buffer


def unpackVarInt(sock):
    data = 0
    for i in range(5):
        ordinal = sock.recv(1)

        if len(ordinal) == 0:
            break

        byte = ord(ordinal)
        data |= (byte & 0x7F) << 7*i

        if not byte & 0x80:
            break

    return data


def makePacket(
    packetId: int,
    data: bytes = bytearray()
) -> bytes:
    packetIdAsVarInt = intToVarInt(packetId)
    packetSize = intToVarInt(len(packetIdAsVarInt + data))
    return packetSize + packetIdAsVarInt + data


def pingServer(
    ip: str = "127.0.0.1", 
    port: int = 25565,
    timeout: int = 5
) -> dict[str, Union[str, int]]:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Connecting the the server
        sock.settimeout(timeout)
        sock.connect((ip, port))

        # Making and sending the handshake packet
        encoded_ip = ip.encode("UTF-8")
        handshakePacket = makePacket(
            packetId=0x00,
            data=(
                intToVarInt(-1) + \
                intToVarInt(len(encoded_ip)) + \
                encoded_ip + \
                port.to_bytes(2, "big", signed=False) + \
                intToVarInt(1)))
        sock.send(handshakePacket)

        # Making and sending the request packet
        requestPacket = makePacket(packetId=0x00)
        sock.send(requestPacket)

        # Getting the packet length & id
        packet_length = unpackVarInt(sock)
        packet_id = unpackVarInt(sock)

        # Skippin a var int becaues of some bullshit
        if packet_id > packet_length:
            unpackVarInt(sock)

        # Getting the packet contents
        data = b''
        extra_length = unpackVarInt(sock)
        while len(data) < extra_length:
            data += sock.recv(extra_length)
        data = data.decode("utf-8")

        return {
            "packet_length": packet_length,
            "packet_id": packet_id,
            "results": data
        }