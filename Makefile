SOURCE = REEL
VERSION = $(shell cat doc/version)
INSTALL=/usr/bin/install -c

ROOT = /usr
BIN_DIR = $(ROOT)/bin
LIB_DIR = $(ROOT)/lib/reel
LAUNCHER_DIR = $(ROOT)/share/applications
ICON_DIR = $(ROOT)/share/icons/hicolor/scalable/apps
PREFIX = $(ROOT)/share/reel

BUILD_DIR = _build

GTK_INSTALL =
QT_INSTALL =

.PHONY: _build _build/doc _build/data _build/ui _build/src

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

all: _build

clean:
	@rm -rvf _build

install:

	@if test -f "_build" ; then \
		echo "Please run 'make all' first to build the project before installing."exit 1; \
	fi

	@echo "\e[32mIN \e[0m /usr/bin/reel"
	@$(INSTALL) -D -m 755 src/reel             $(DESTDIR)$(BINDIR)/reel

ifeq ($(QT_INSTALL),yes)
	@for f in src/qt/*; do \
		if [ -f "$$f" ]; then \
			echo "\e[32mIN \e[0m $$f"; \
			$(INSTALL) -D -m 755 "$$f" $(DESTDIR)$(LIB_DIR)/reel/qt/; \
		fi; \
	done
endif

ifeq ($(GTK_INSTALL),yes)
	@for f in src/gtk/*; do \
		if [ -f "$$f" ]; then \
			echo "\e[32mIN \e[0m $$f"; \
			$(INSTALL) -D -m 755 "$$f" $(DESTDIR)$(LIB_DIR)/reel/gtk/; \
		fi; \
	done
endif

	@for f in data/ui/*; do \
		if [ -f "$$f" ]; then \
			echo "\e[32mIN \e[0m $$f"; \
			$(INSTALL) -D -m 644 "$$f" $(DESTDIR)$(PREFIX)/ui/; \
		fi; \
	done

	@for f in data/icons/scalable/com.MLSTidbits.Reel.svg; do \
		if [ -f "$$f" ]; then \
			echo "\e[32mIN \e[0m $$f"; \
			$(INSTALL) -D -m 644 "$$f" $(DESTDIR)$(ICON_DIR)/; \
		fi; \
	done

	@for f in data/com.MLSTidbits.Reel.desktop; do \
		if [ -f "$$f" ]; then \
			echo "\e[32mIN \e[0m $$f"; \
			$(INSTALL) -D -m 644 "$$f" $(DESTDIR)$(LAUNCHER_DIR)/; \
		fi; \
	done
