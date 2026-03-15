include makefile.common
include mmccextr/mmccextr.mak

prefix=/usr
exec_prefix=${prefix}
libdir=${exec_prefix}/lib
bindir=${exec_prefix}/bin

FFMPEG_CFLAGS=-I/usr/include/x86_64-linux-gnu
FFMPEG_LIBS=-lavcodec -lavutil -lrt

ENABLE_DEBUG=no
NO_EC_DEF=

BUILDINFO_ARCH_NAME=$(shell $(GCC) -dumpmachine)
BUILDINFO_BUILD_DATE=$(shell date)

top_srcdir ?= .
INCF=-I$(top_srcdir)/

ifeq ($(ENABLE_DEBUG),no)
STRIP_FLAGS=--strip-all --strip-debug --strip-unneeded --discard-all
endif

LIBABI_OBJ   := $(patsubst %,tmp/%.o,$(LIBABI_SRC))
LIBFFABI_OBJ := $(patsubst %,tmp/%.o,$(LIBFFABI_SRC))
MMCCX_SRC    := $(patsubst %,mmccextr/%,$(MMCCEXTR_SRC))

# ── Targets ───────────────────────────────────────────────────────────────── #

.PHONY: all clean install rebuild

all: out/libdriveio.so.0 out/libmakemkv.so.1 out/libmmbd.so.0 out/mmccextr out/mmgplsrv out/makemkv.bin.full

clean:
	-rm -rf out tmp

install: out/libdriveio.so.0 out/libmakemkv.so.1 out/libmmbd.so.0 out/mmccextr out/mmgplsrv out/makemkv.bin.full
	$(INSTALL) -D -m 644 out/libdriveio.so.0  $(DESTDIR)$(libdir)/libdriveio.so.0
	$(INSTALL) -D -m 644 out/libmakemkv.so.1  $(DESTDIR)$(libdir)/libmakemkv.so.1
	$(INSTALL) -D -m 644 out/libmmbd.so.0     $(DESTDIR)$(libdir)/libmmbd.so.0
ifeq ($(DESTDIR),)
	ldconfig
endif
	$(INSTALL) -D -m 755 out/mmccextr         $(DESTDIR)$(bindir)/mmccextr
	$(INSTALL) -D -m 755 out/mmgplsrv         $(DESTDIR)$(bindir)/mmgplsrv

# ── Strip step ────────────────────────────────────────────────────────────── #

out/%: out/%.full
	@echo "$@"
	@$(OBJCOPY) $(STRIP_FLAGS) $< $@

# ── libdriveio ────────────────────────────────────────────────────────────── #

out/libdriveio.so.0.full:
	@mkdir -p out
	@echo "$@"
	@echo "$<"
	@$(GXX) $(CXXFLAGS) $(CFLAGS) $(LDFLAGS) -D_REENTRANT -shared -Wl,-z,defs -o$@ \
	$(INCF)$(LIBDRIVEIO_INC) $(LIBDRIVEIO_SRC) \
	-fPIC -Xlinker -dy -Xlinker --version-script=libdriveio/src/libdriveio.vers \
	-Xlinker -soname=libdriveio.so.0 -lc -lstdc++

# ── libmakemkv ────────────────────────────────────────────────────────────── #

tmp/%.c.o: %.c
	@mkdir -p $(dir $@)
	@echo "$@"
	@$(GCC) -c $(CFLAGS) $(NO_EC_DEF) -D_GNU_SOURCE -D_REENTRANT -o$@ \
	$(INCF)$(LIBABI_INC) $(INCF)$(LIBFFABI_INC) \
	-DHAVE_BUILDINFO_H -Itmp $(FFMPEG_CFLAGS) -fPIC $<

out/libmakemkv.so.1.full: tmp/gen_buildinfo.h $(LIBABI_OBJ) $(LIBFFABI_OBJ)
	@mkdir -p out
	@echo "$@"
	@$(GXX) $(CXXFLAGS) $(CFLAGS) $(LDFLAGS) $(NO_EC_DEF) -D_GNU_SOURCE -D_REENTRANT -shared -Wl,-z,defs -o$@ \
	$(INCF)$(LIBEBML_INC) $(LIBEBML_DEF) \
	$(INCF)$(LIBMATROSKA_INC) $(INCF)$(LIBMAKEMKV_INC) \
	$(INCF)$(SSTRING_INC) $(INCF)$(MAKEMKVGUI_INC) \
	$(INCF)$(LIBABI_INC) $(INCF)$(LIBFFABI_INC) \
	$(LIBEBML_SRC) $(LIBMATROSKA_SRC) $(LIBMAKEMKV_SRC) \
	$(SSTRING_SRC) $(LIBABI_SRC_LINUX) \
	$(LIBABI_OBJ) $(LIBFFABI_OBJ) \
	-DHAVE_BUILDINFO_H -Itmp \
	-fPIC -Xlinker -dy -Xlinker --version-script=libmakemkv/src/libmakemkv.vers \
	-Xlinker -soname=libmakemkv.so.1 -lc -lstdc++ -lcrypto -lz -lexpat $(FFMPEG_LIBS) -lm -lrt

# ── libmmbd ───────────────────────────────────────────────────────────────── #

out/libmmbd.so.0.full:
	@mkdir -p out
	@echo "$@"
	@$(GXX) $(CXXFLAGS) $(CFLAGS) $(LDFLAGS) -D_REENTRANT -shared -Wl,-z,defs -o$@ \
	$(INCF)$(MAKEMKVGUI_INC) $(INCF)$(LIBMMBD_INC) \
	$(INCF)$(LIBDRIVEIO_INC) $(INCF)$(LIBMAKEMKV_INC) \
	$(INCF)$(SSTRING_INC) $(INCF)$(LIBABI_INC) \
	$(LIBMMBD_SRC) $(LIBMMBD_SRC_LINUX) $(SSTRING_SRC) \
	$(LIBDRIVEIO_SRC_PUB) \
	-fPIC -Xlinker -dy -Xlinker --version-script=libmmbd/src/libmmbd.vers \
	-Xlinker -soname=libmmbd.so.0 -lc -lstdc++ -lrt -lpthread -lcrypto -ldl

# ── mmccextr ──────────────────────────────────────────────────────────────── #

out/mmccextr.full: $(MMCCX_SRC) tmp/gen_buildinfo.h
	@mkdir -p out
	@echo "$@"
	@$(GCC) $(CFLAGS) $(LDFLAGS) $(MMCCEXTR_DEF) -DHAVE_BUILDINFO_H -Itmp -D_GNU_SOURCE \
	-o$@ $(MMCCX_SRC) -lc \
	-ffunction-sections -Wl,--gc-sections -Wl,-z,defs

# ── mmgplsrv ──────────────────────────────────────────────────────────────── #

out/mmgplsrv.full: $(MMGPL_SRC)
	@mkdir -p out
	@echo "$@"
	@$(GCC) $(CFLAGS) $(LDFLAGS) \
	$(INCF)$(MMGPL_INC) $(INCF)$(DVDNAV_INC) $(INCF)$(DVDREAD_INC) \
	$(INCF)$(MAKEMKVGUI_INC) $(INCF)$(LIBMAKEMKV_INC) \
	$(INCF)$(LIBDRIVEIO_INC) $(INCF)$(LIBABI_INC) \
	$(MMGPL_DEF) -D_GNU_SOURCE -Dstl=std \
	-o$@ $(MMGPL_SRC) $(MMGPL_SRC_LINUX) -lc -lstdc++ \
	-ffunction-sections -Wl,--gc-sections -Wl,-z,defs

# ── MakeMKV binary ──────────────────────────────────────────────────────────────── #

out/makemkv.bin.full: out/libmakemkv.so.1 out/libmmbd.so.0 out/libdriveio.so.0
	@mkdir -p out
	@echo "$@"
	@cp bin/makemkvcon out/

# ── Build info header ─────────────────────────────────────────────────────── #

tmp/gen_buildinfo.h:
	@mkdir -p tmp
	@echo "$@"
	@echo "/* This file is auto-generated. Do not edit. */" > $@
	@echo "#define BUILDINFO_ARCH_NAME \"$(BUILDINFO_ARCH_NAME)\"" >> $@
	@echo "#define BUILDINFO_BUILD_DATE \"$(BUILDINFO_BUILD_DATE)\"" >> $@
