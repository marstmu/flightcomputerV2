from machine import Pin, SPI
import time

# Define SPI pins
spi = SPI(0, baudrate=5000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
# cs = Pin(17, Pin.OUT)  # Chip select (CS) pin
# reset = Pin(14, Pin.OUT)  # Reset pin
# dio0 = Pin(26, Pin.IN)  # DIO0 interrupt pin (for received packets)

# RFM95 registers
RFM95_REG_OP_MODE = 0x01
RFM95_REG_FRF_MSB = 0x06
RFM95_REG_FRF_MID = 0x07
RFM95_REG_FRF_LSB = 0x08
RFM95_REG_PA_CONFIG = 0x09
RFM95_REG_FIFO_ADDR_PTR = 0x0D
RFM95_REG_FIFO = 0x00
RFM95_REG_PAYLOAD_LENGTH = 0x22
RFM95_REG_IRQ_FLAGS = 0x12
RFM95_REG_FIFO_RX_CURRENT_ADDR = 0x10
RFM95_REG_RX_NB_BYTES = 0x13

# Constants for RFM95
RFM95_MODE_SLEEP = 0x00
RFM95_MODE_STDBY = 0x01
RFM95_MODE_TX = 0x03
RFM95_MODE_RXCONTINUOUS = 0x05

# Frequency for LoRa (915 MHz in this case)
RF_FREQUENCY = 915000000

# Helper functions
def reset_rfm95():
    reset.value(0)
    time.sleep(0.01)
    reset.value(1)
    time.sleep(0.01)

def write_register(register, value):
    cs.value(0)
    spi.write(bytearray([register | 0x80]))  # MSB = 1 for write operation
    spi.write(bytearray([value]))
    cs.value(1)

def read_register(register):
    cs.value(0)
    spi.write(bytearray([register & 0x7F]))  # MSB = 0 for read operation
    result = spi.read(1)
    cs.value(1)
    return result[0]

def set_mode(mode):
    write_register(RFM95_REG_OP_MODE, mode)

def set_frequency(frequency):
    frf = int((frequency << 19) / 32000000)
    write_register(RFM95_REG_FRF_MSB, (frf >> 16) & 0xFF)
    write_register(RFM95_REG_FRF_MID, (frf >> 8) & 0xFF)
    write_register(RFM95_REG_FRF_LSB, frf & 0xFF)

def set_tx_power(level):
    write_register(RFM95_REG_PA_CONFIG, 0x80 | (level & 0x0F))  # PA_BOOST, power level

def receive_packet():
    set_mode(RFM95_MODE_RXCONTINUOUS)  # Set to receive mode
    
    while dio0.value() == 0:  # Wait for a packet (DIO0 goes high when a packet is received)
        time.sleep(0.1)
    
    # Packet received
    irq_flags = read_register(RFM95_REG_IRQ_FLAGS)
    write_register(RFM95_REG_IRQ_FLAGS, irq_flags)  # Clear IRQ flags

    # Get current RX address
    fifo_addr = read_register(RFM95_REG_FIFO_RX_CURRENT_ADDR)
    write_register(RFM95_REG_FIFO_ADDR_PTR, fifo_addr)

    # Get the packet length
    packet_length = read_register(RFM95_REG_RX_NB_BYTES)

    # Read packet from FIFO
    packet = []
    for i in range(packet_length):
        packet.append(read_register(RFM95_REG_FIFO))
    
    return bytes(packet)

def send_packet(data):
    set_mode(RFM95_MODE_STDBY)
    
    # Write to FIFO
    write_register(RFM95_REG_FIFO_ADDR_PTR, 0x00)  # Set FIFO address to base
    for byte in data:
        write_register(RFM95_REG_FIFO, byte)
    
    # Set payload length
    write_register(RFM95_REG_PAYLOAD_LENGTH, len(data))
    
    # Set to transmit mode
    set_mode(RFM95_MODE_TX)
    
    # Wait for TX done (DIO0 goes high)
    while dio0.value() == 0:
        time.sleep(0.1)
    
    # TX done, return to standby mode
    set_mode(RFM95_MODE_STDBY)

# Initialize the RFM95
def init_rfm95():
    reset_rfm95()

    # Set LoRa mode
    write_register(RFM95_REG_OP_MODE, 0x80)

    # Set frequency
    set_frequency(RF_FREQUENCY)

    # Set TX power to 17 dBm
    set_tx_power(17)

# Main loop for testing
def main():
    init_rfm95()

    while True:
        # Receive data
        print("Waiting for packet...")
        packet = receive_packet()
        print("Received packet:", packet)

        # After receiving, send a response packet
        send_packet(b'ACK')
        print("Sent ACK")

        time.sleep(1)

# Run the main function
main()
