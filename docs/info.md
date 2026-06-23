# Projet Ecole 2026
**Synchronous FIFO Submission to TinyTapeout**

## Requirements
* **Icarus Verilog**
* **GTKWave**
* **OpenLane 2**
* **TinyTapeout**
* **Docker**
* **Git**



## Week 1: Instalation and configuration
This week involves the installation of the **OpenLane 2** tool. For this, the following [instalation guide](https://openlane2.readthedocs.io/en/latest/getting_started/common/docker_installation/index.html) was used.


### 1. Verificación de Docker
First, we verify that the service is running correctly:

```bash
docker run hello-world
```

> **[ ! ] Important:&nbsp;**  Some OpenLane libraries do not work with Python 3.13; it is recommended to create a virtual environment with version 3.12.


### 2. Virtual Environment Creation
The standard virtual environment is created as follows:

```bash
python3.10 -m venv PE_env
source PE_env/bin/activate
```

> **[ i ] Note:&nbsp;** The professor suggests using `uv` for the virtual environment:
>```bash
>mkdir ~/ttsetup
>uv venv --python 3.12 ~/ttsetup/venv
>```

### 3. Clone the Project
Next, we clone the TinyTapeout test project and its support tools:

```bash
git clone [https://github.com/TinyTapeout/ttsky25b-factory-test](https://github.com/TinyTapeout/ttsky25b-factory-test) factory-test
cd factory-test
git clone [https://github.com/TinyTapeout/tt-support-tools](https://github.com/TinyTapeout/tt-support-tools) tt
```

### 4. Environment Variables and Dependencies
We export the necessary environment variables:

```bash
export PDK_ROOT=~/ttsetup/pdk
export PDK=sky130A
export LIBRELANE_TAG=3.0.0rc1
```

The requirements are installed:

```bash
pip install -r test/requirements.txt
pip install -r tt/requirements.txt
pip install librelane==$LIBRELANE_TAG 
```

### 5. Validation and GDS Generation
Finally, we validate everything by generating the GDS file:

```bash
./tt/tt_tool.py --create-user-config
./tt/tt_tool.py --harden
klayout runs/wokwi/final/gds/tt_um_factory_test.gds
```

## Week 2-3: RTL Design and Functional Verification

### Overview

The `fifo` module has 2 parameters, 5 inputs, and 3 outputs. Its interface is described below:

#### Parameters:

* **`WIDTH`:** Data bus size.
* **`DEPTH`:** Number of data elements to store. This number must be a power of 2 (explained later).

#### Inputs:

* **`clk`:** Module operation clock.
* **`rst`:** Active-high asynchronous reset.
* **`wr_en`:** Write enable signal. Enables writing data into the memory for the next clock cycle.
* **`rd_en`:** Read enable signal. Enables reading data for the immediate cycle.
* **`d_in`:** Input data of parameterized size `WIDTH`.

#### Outputs:

* **`d_out`:** Output data of parameterized size `WIDTH`.
* **`full`:** Status signal (flag) that goes active-high when the FIFO is completely full, indicating that no more data can be written.
* **`empty`:** Status signal (flag) that goes active-high when the FIFO is empty, indicating that no data is available to be read.

```
                    ┌──────────────────┐
            clk ───►│                  │
            rst ───►│                  │
                    │                  ├───► full
          wr_en ───►│       FIFO       ├───► empty
          rd_en ───►│                  │
    d_in[W-1:0] ───►│                  │
                    │                  ├───► d_out[W-1:0]
                    └──────────────────┘
```

### Features

The module utilizes two internal pointers, `wr_ptr` and `rd_ptr`, which increment by 1 upon writing and reading, respectively.

The `full` and `empty` flags are driven by combinational logic, ensuring instantaneous state updates. The code describing this logic is as follows:

```verilog
always @(*) begin
    full = (wr_ptr_q[AW-1:0]==rd_ptr_q[AW-1:0]) && (wr_ptr_q[AW]!=rd_ptr_q[AW]);
    empty = wr_ptr_q == rd_ptr_q;
end
```

#### Empty:

The memory is considered empty when both pointers are exactly equal:
```
      0   1   2   3   4   5   6   7
    ┌───┬───┬───┬───┬───┬───┬───┬───┐
    │   │   │   │   │   │   │   │   │
    └───┴───┴───┴───┴───┴───┴───┴───┘
      ^
      |
  wr_ptr_q
  rd_ptr_q
```

#### Full:
The memory is considered full when all bits of the write pointer, except for the most significant bit (MSB), match the corresponding bits of the read pointer. Since the write pointer has already completed one full wrap-around, its MSB differs from that of the read pointer.

```
      0   1   2   3   4   5   6   7
    ┌───┬───┬───┬───┬───┬───┬───┬───┐
    │ D │ D │ D │ D │ D │ D │ D │ D │
    └───┴───┴───┴───┴───┴───┴───┴───┘
              ^
              |
          rd_ptr_q
          wr_ptr_q 
```



