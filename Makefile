SOURCE = REEL
VERSION = $(shell cat doc/version)
INSTALL=/usr/bin/install -c

GTK_INSTALL =
QT_INSTALL =

.PHONY: all clean install rebuild _build _build/doc _build/data _build/ui _build/src

all: _build

clean:
	@rm -rvf _build

install:
	$(INSTALL) -D -m 644 out/libdriveio.so.0  $(DESTDIR)$(LIBDIR)/libdriveio.so.0
	$(INSTALL) -D -m 644 out/libmakemkv.so.1  $(DESTDIR)$(LIBDIR)/libmakemkv.so.1
	$(INSTALL) -D -m 644 out/libmmbd.so.0     $(DESTDIR)$(LIBDIR)/libmmbd.so.0

ifeq ($(DESTDIR),)
	ldconfig
endif

	$(INSTALL) -D -m 755 out/mmccextr         $(DESTDIR)$(BINDIR)/mmccextr
	$(INSTALL) -D -m 755 out/mmgplsrv         $(DESTDIR)$(BINDIR)/mmgplsrv
	$(INSTALL) -D -m 755 out/makemkvcon       $(DESTDIR)$(BINDIR)/makemkvcon
	$(INSTALL) -D -m 755 src/reel             $(DESTDIR)$(BINDIR)/reel

ifeq ($(GTK_INSTALL),yes)
	$(INSTALL) -D -m 755 src/core/*.py  $(DESTDIR)$(LIBDIR)/reel/core/
	$(INSTALL) -D -m 755 src/ui/*.py   $(DESTDIR)$(LIBDIR)/reel/ui/
	$(INSTALL) -D -m 755 src/main.py  $(DESTDIR)$(LIBDIR)/reel/
endif

	$(INSTALL) -D -m 644 data/comMLSTidbits.Reel.desktop $(DESTDIR)$(LAUNCHERDIR)/
	$(INSTALL) -D -m 644 data/icons/scalable/comMLSTidbits.Reel.svg $(DESTDIR)$(ICONDIR)/

	$(INSTALL) -D -m 644 data/ui/* $(DESTDIR)$(PREFIX)/share/reel/ui/

_build: _build/doc _build/data _build/ui _build/src

_build/doc:
	@mkdir -p _build/doc
	@for f in doc/version doc/copyright CODE_OF_CONDUCT.md COPYING README.md CONTRIBUTING.md; do \
		if [ -f "$$f" ]; then \
			echo "\e[32mCP \e[0m $$f"; \
			cp "$$f" _build/doc/; \
		fi; \
	done

_build/data:
	@mkdir -p _build/data
	@for f in data/com.MLSTidbits.Reel.desktop data/icons/scalable/com.MLSTidbits.Reel.svg; do \
		if [ -f "$$f" ]; then \
			echo "\e[32mCP \e[0m $$f"; \
			cp "$$f" _build/data/; \
		fi; \
	done

_build/ui:
	@mkdir -p _build/ui
	@for f in data/ui/*; do \
		if [ -f "$$f" ]; then \
			echo "\e[32mCP \e[0m $$f"; \
			cp "$$f" _build/ui/; \
		fi; \
	done

_build/src:
	@mkdir -p _build
	@for f in src/gtk/main.py src/gtk src/qt src/reel; do \
		if [ -f "$$f" ] || [ -d "$$f" ]; then \
			echo "\e[32mCP \e[0m $$f"; \
			cp -fr "$$f" _build/; \
		fi; \
	done
