# Backannotated timing simulation for tinytapeout

## Requirements

* The tinytapeout `GDS.zip` artifact
* A Centos 7 or AlmaLinux 8 machine or VM on an x86\_64-based system. Other
  distributions have not been tested, and CVC requires an x86\_64-based machine
  to successfully compile.
* Tachyon's OSS-CVC (see below)
* cocotb (see below)

## Steps

### Compiling OSS-CVC

1. Read the license and, if you agree, download CVC from
   [Tachyon's website](http://www.tachyon-da.com/).
2. If you haven't already, install development tools on your machine by runnning
   `yum group install -y "Development Tools"` as root.
3. Unpack the CVC archive and change into the source directory: 
   `tar -xvf open_src_cvc_700c_tar.bz2; cd open-src-cvc.700c/src/`
4. Build `hexasm`: `make -f makefile.cvc64 hexasm.o`
5. Copy the compiled `hexasm` binary somewhere in your path.
6. Build the rest of CVC: `make -f makefile.cvc64`
7. Copy the compiled `cvc64` binary somewhere in your path.
8. Test your installation:
```
cd ../tests_and_examples/install.test/
      ./inst_test.sh cvc64
      ./inst_test_interp.sh cvc64
```

### Installing cocotb

1. Install python3 and pip, if you haven't already:
   Run `yum install -y python3 python3-pip` as root
2. Install cocotb: Run `pip3 install cocotb` as a regular user.

### Performing the backannotated simulation

1. In `tb.v`, edit the line starting with `$sdf_annotate` to point to the SDF
   file corresponding to the corner you want to test at.
2. From `GDS.zip`, copy the powered gate-level netlist from
   `runs/wokwi/results/final/verilog/gl/tt_um_cam.v` to `gate_level_netlist.v`
   in this directory.
3. Run `SIM=cvc GATES=yes SDF=yes make > sim.log`. Once finished, review
   `sim.log`.

## Further reading

* [Timing closure for Open-Source Designs: A technical
  report](https://docs.google.com/document/d/13J1AY1zhzxur8vaFs3rRW9ZWX113rSDs63LezOOoXZ8/edit) : This is where I learned the procedure to launch CVC from.
* [How we fixed Caravel - An interview with Andy
  Wright](https://www.youtube.com/watch?v=F377UouYr7Y)

## Legal

Please read the warranty disclaimer in [LICENSE](../LICENSE)
