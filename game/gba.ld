ENTRY(_start)
MEMORY {
    ROM (rx) : ORIGIN = 0x08000000, LENGTH = 32M
    RAM (rwx) : ORIGIN = 0x02000000, LENGTH = 256K
}
SECTIONS {
    .text : { KEEP(*(.header)) *(.text.startup) *(.text*) *(.rodata*) . = ALIGN(4); } > ROM
    .data : { __data_start = .; *(.data*) . = ALIGN(4); __data_end = .; } > RAM AT> ROM
    __data_load = LOADADDR(.data);
    .bss (NOLOAD) : { __bss_start = .; *(.bss*) *(COMMON) . = ALIGN(4); __bss_end = .; } > RAM
    /DISCARD/ : { *(.comment) *(.ARM.exidx*) *(.ARM.extab*) }
}
