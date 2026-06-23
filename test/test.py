import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles
import random

@cocotb.test()
async def test_fifo(dut):
    dut._log.info("--- Iniciando pruebas de la FIFO en Cocotb ---")

    clock = Clock(dut.clk, 50, unit="ns")
    cocotb.start_soon(clock.start())

    # 0. Inicialización de señales
    dut.ena.value = 1
    dut.ui_in.value = 0      
    dut.uio_in.value = 0     
    dut.rst_n.value = 0      

    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1      
    await ClockCycles(dut.clk, 2)

    uio_out_val = dut.uio_out.value.to_unsigned()
    empty_flag = (uio_out_val >> 3) & 1
    full_flag  = (uio_out_val >> 2) & 1
    
    assert empty_flag == 1, "Error: La bandera 'empty' debería ser 1 tras el reset."
    assert full_flag == 0, "Error: La bandera 'full' NO debería ser 1 tras el reset."

    DEPTH = 16
    written_data = []

    # 1. Prueba de ESCRITURA hasta llenar la memoria
    dut._log.info("TEST 1: Escribiendo datos en la FIFO...")
    dut.uio_in.value = 1  

    for i in range(DEPTH):
        data = random.randint(0, 255)
        dut.ui_in.value = data
        written_data.append(data)
        await RisingEdge(dut.clk)
        
    # Intentar escribir con FIFO llena
    dut.ui_in.value = 0xFF
    await RisingEdge(dut.clk)
    
    # Apagar escritura
    dut.uio_in.value = 0
    await ClockCycles(dut.clk, 2) 
    
    full_flag = (dut.uio_out.value.to_unsigned() >> 2) & 1
    assert full_flag == 1, "Error: La FIFO debería estar LLENA (full=1)."

    # 2. Prueba de LECTURA hasta vaciar la memoria
    dut._log.info("TEST 2: Leyendo datos de la FIFO...")
    dut.uio_in.value = 2  # Activar rd_en

    # Como la memoria suele tener un ciclo de latencia de lectura,
    # esperamos un ciclo en blanco antes de empezar a comprobar el bus de salida
    await RisingEdge(dut.clk) 

    for expected_data in written_data:
        # Esperamos el ciclo para que el dato actual se propague
        await RisingEdge(dut.clk) 
        read_data = dut.uo_out.value.to_unsigned()
        assert read_data == expected_data, f"Error de datos: esperado {expected_data}, obtenido {read_data}"

    # Apagar lectura y esperar que se asienten las señales
    dut.uio_in.value = 0
    await ClockCycles(dut.clk, 2)

    empty_flag = (dut.uio_out.value.to_unsigned() >> 3) & 1
    assert empty_flag == 1, "Error: La FIFO debería estar VACÍA (empty=1)."

    # 3. Prueba de Escritura y Lectura simultánea
    dut._log.info("TEST 3: Escritura y Lectura simultánea...")
    dut.uio_in.value = 1; dut.ui_in.value = 0xAA
    await RisingEdge(dut.clk)

    dut.uio_in.value = 3  
    secuencia_in = [0xBB, 0xCC, 0xDD, 0xEE, 0xFF]
    
    for val in secuencia_in:
        dut.ui_in.value = val
        await RisingEdge(dut.clk)

    dut.uio_in.value = 0
    await ClockCycles(dut.clk, 2)

    dut._log.info("--- Pruebas finalizadas exitosamente ---")