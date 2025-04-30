# Makefile for Ubuntu: 64-bit Wine prefix, Windows 10+, .NET 4.5

WINEPREFIX ?= $(HOME)/.wine64
WINEARCH ?= win64
CLAUDE_DESKTOP ?= Claude-Setup-x64.exe

all: setup-prefix setup-dotnet run-claude

# Step 1: Cleanly initialize the 64-bit Wine prefix
setup-prefix:
	rm -rf $(WINEPREFIX)
	WINEPREFIX=$(WINEPREFIX) WINEARCH=$(WINEARCH) wineboot -u
	WINEPREFIX=$(WINEPREFIX) winetricks -q win10

# Step 2: Install .NET 4.5 into the 64-bit prefix
setup-dotnet:
	WINEPREFIX=$(WINEPREFIX) winetricks dotnet45

# Step 3: Run the installer
run-claude:
	WINEPREFIX=$(WINEPREFIX) wine $(CLAUDE_DESKTOP) /trustlevel:0x20000

# Step 4: Clean the Wine prefix
clean:
	rm -rf $(WINEPREFIX)
