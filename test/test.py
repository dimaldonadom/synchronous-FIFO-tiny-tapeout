import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles
import random

@cocotb.test()
async def test_fifo(dut):
    dut._log.info("--- Iniciando pruebas de la FIFO en Cocotb ---")

    # Configurar el reloj a 50 ns. CORREGIDO: unit="ns" en lugar de units="ns"
    clock = Clock(dut.clk, 50, unit="ns")
    cocotb.start_soon(clock.start())

    # 0. Inicialización de señales
    dut.ena.value = 1
    dut.ui_in.value = 0      # d_in = 0
    dut.uio_in.value = 0     # wr_en = 0, rd_en = 0
    dut.rst_n.value = 0      # Reset activo en bajo (0)

    # Esperar un par de ciclos y soltar el reset
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1      # Soltar reset
    await ClockCycles(dut.clk, 2)

    # CORREGIDO: Leer el bus completo y aislar los bits (bit 3 = empty, bit 2 = full)
    uio_out_val = dut.uio_out.value.integer
    empty_flag = (uio_out_val >> 3) & 1
    full_flag  = (uio_out_val >> 2) & 1
    
    assert empty_flag == 1, "Error: La bandera 'empty' debería ser 1 tras el reset."
    assert full_flag == 0, "Error: La bandera 'full' NO debería ser 1 tras el reset."

    # Variables para autoverificación
    DEPTH = 8
    written_data = []

    # 1. Prueba de ESCRITURA hasta llenar la memoria
    dut._log.info("TEST 1: Escribiendo datos en la FIFO...")
    
    # CORREGIDO: Escribir el bus completo uio_in. (Valor 1 = binario 00000001 -> wr_en=1, rd_en=0)
    dut.uio_in.value = 1  

    for i in range(DEPTH):
        data = random.randint(0, 255) # Dato aleatorio de 8 bits
        dut.ui_in.value = data
        written_data.append(data)
        await RisingEdge(dut.clk)
        
    # Intentar escribir con FIFO llena
    dut.ui_in.value = 0xFF
    await RisingEdge(dut.clk)
    
    # Apagar escritura (wr_en=0, rd_en=0 -> valor 0)
    dut.uio_in.value = 0
    await ClockCycles(dut.clk, 1)
    
    # Comprobar que está llena
    full_flag = (dut.uio_out.value.integer >> 2) & 1
    assert full_flag == 1, "Error: La FIFO debería estar LLENA (full=1)."

    # 2. Prueba de LECTURA hasta vaciar la memoria
    dut._log.info("TEST 2: Leyendo datos de la FIFO...")
    
    # CORREGIDO: Encender solo rd_en (Valor 2 = binario 00000010 -> wr_en=0, rd_en=1)
    dut.uio_in.value = 2  

    for expected_data in written_data:
        await RisingEdge(dut.clk)
        read_data = dut.uo_out.value.integer
        assert read_data == expected_data, f"Error de datos: esperado {expected_data}, obtenido {read_data}"

    # Intentar leer con FIFO vacía
    await RisingEdge(dut.clk)
    
    # Apagar lectura
    dut.uio_in.value = 0
    await ClockCycles(dut.clk, 1)

    # Comprobar que está vacía
    empty_flag = (dut.uio_out.value.integer >> 3) & 1
    assert empty_flag == 1, "Error: La FIFO debería estar VACÍA (empty=1)."

    # 3. Prueba de Escritura y Lectura simultánea
    dut._log.info("TEST 3: Escritura y Lectura simultánea...")
    
    # Metemos un dato inicial (wr_en=1, rd_en=0 -> valor 1)
    dut.uio_in.value = 1; dut.ui_in.value = 0xAA
    await RisingEdge(dut.clk)

    # Leer y escribir a la vez (wr_en=1, rd_en=1 -> valor 3 = binario 00000011)
    dut.uio_in.value = 3  
    secuencia_in = [0xBB, 0xCC, 0xDD, 0xEE, 0xFF]
    
    for val in secuencia_in:
        dut.ui_in.value = val
        await RisingEdge(dut.clk)

    # Apagar todo
    dut.uio_in.value = 0
    await ClockCycles(dut.clk, 2)

    dut._log.info("--- Pruebas finalizadas exitosamente ---")