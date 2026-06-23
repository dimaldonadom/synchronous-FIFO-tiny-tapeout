import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles
import random

@cocotb.test()
async def test_fifo(dut):
    dut._log.info("--- Iniciando pruebas de la FIFO en Cocotb ---")

    # Configurar el reloj a 50 ns (20 MHz) para coincidir con tu config.json
    clock = Clock(dut.clk, 50, units="ns")
    cocotb.start_soon(clock.start())

    # 0. Inicialización de señales
    dut.ena.value = 1
    dut.ui_in.value = 0      # d_in
    dut.uio_in.value = 0     # bit 0: wr_en, bit 1: rd_en
    dut.rst_n.value = 0      # Reset activo en bajo (0)

    # Esperar un par de ciclos y soltar el reset
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1      # Soltar reset
    await ClockCycles(dut.clk, 2)

    # Comprobación del Reset
    assert dut.uio_out[3].value == 1, "Error: La bandera 'empty' debería ser 1 tras el reset."
    assert dut.uio_out[2].value == 0, "Error: La bandera 'full' NO debería ser 1 tras el reset."

    # Variables para autoverificación
    DEPTH = 8
    written_data = []

    # 1. Prueba de ESCRITURA hasta llenar la memoria
    dut._log.info("TEST 1: Escribiendo datos en la FIFO...")
    dut.uio_in[0].value = 1  # wr_en = 1
    dut.uio_in[1].value = 0  # rd_en = 0

    for i in range(DEPTH):
        data = random.randint(0, 255) # Dato aleatorio de 8 bits
        dut.ui_in.value = data
        written_data.append(data)
        await RisingEdge(dut.clk)
        
    # Intentar escribir con FIFO llena (Corner case exigido por la guía)
    dut.ui_in.value = 0xFF
    await RisingEdge(dut.clk)
    
    dut.uio_in[0].value = 0  # wr_en = 0
    await ClockCycles(dut.clk, 1)
    
    # Comprobar que está llena
    assert dut.uio_out[2].value == 1, "Error: La FIFO debería estar LLENA (full=1)."

    # 2. Prueba de LECTURA hasta vaciar la memoria
    dut._log.info("TEST 2: Leyendo datos de la FIFO...")
    dut.uio_in[1].value = 1  # rd_en = 1

    for expected_data in written_data:
        await RisingEdge(dut.clk)
        # Nota: si tu FIFO requiere un ciclo para actualizar d_out, podrías necesitar leer un ciclo después.
        read_data = dut.uo_out.value.integer
        assert read_data == expected_data, f"Error de datos: esperado {expected_data}, obtenido {read_data}"

    # Intentar leer con FIFO vacía (Corner case)
    await RisingEdge(dut.clk)
    dut.uio_in[1].value = 0  # rd_en = 0
    await ClockCycles(dut.clk, 1)

    # Comprobar que está vacía
    assert dut.uio_out[3].value == 1, "Error: La FIFO debería estar VACÍA (empty=1)."

    # 3. Prueba de Escritura y Lectura simultánea
    dut._log.info("TEST 3: Escritura y Lectura simultánea...")
    # Metemos un dato inicial
    dut.uio_in[0].value = 1; dut.uio_in[1].value = 0; dut.ui_in.value = 0xAA
    await RisingEdge(dut.clk)

    # Leer y escribir a la vez
    dut.uio_in[0].value = 1; dut.uio_in[1].value = 1  # wr_en=1, rd_en=1
    secuencia_in = [0xBB, 0xCC, 0xDD, 0xEE, 0xFF]
    
    for val in secuencia_in:
        dut.ui_in.value = val
        await RisingEdge(dut.clk)
        # Aquí puedes autoverificar si los datos salen correctamente de manera concurrente

    dut.uio_in[0].value = 0; dut.uio_in[1].value = 0
    await ClockCycles(dut.clk, 2)

    dut._log.info("--- Pruebas finalizadas exitosamente ---")