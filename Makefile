obj-m += cpuinfo_spoof.o

# Match the previously used DDK build style. The DDK KDIR supplies
# fs/proc/internal.h for php110_layout.h; no private header upload is needed.
ccflags-y += -Werror=incompatible-pointer-types
ccflags-y += -g -gdwarf-4 -fno-eliminate-unused-debug-types
ccflags-y += -I$(srctree)/fs/proc

KDIR ?= /lib/modules/$(shell uname -r)/build
MDIR := $(realpath $(dir $(abspath $(lastword $(MAKEFILE_LIST)))))/

all:
	$(MAKE) -C $(KDIR) M=$(MDIR) modules

clean:
	$(MAKE) -C $(KDIR) M=$(MDIR) clean
