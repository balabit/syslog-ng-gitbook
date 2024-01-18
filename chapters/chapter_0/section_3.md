# macOS

[ref:install]: /chapters/chapter_4/section_2
[ref:compile]: /chapters/chapter_4/section_2
[ref:freepascal-launchd]: https://wiki.freepascal.org/macOS_daemons_and_agents
[ref:apple-launchd]: https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html
[ref:homebrew]: http://brew.sh
[gh:ose-official]: <http://www.github.com/balabit/syslog-ng>

## Introduction

The syslog-ng application has been resurrected on macOS by our developer team.
We hope our product can be useful for Mac users who want to increase the security of their
system through reliable logging.

At present we are not supporting macOS syslog-ng on our [official repository][gh:ose-official] on GitHub.
However, you can install pre-built syslog-ng binaries from various sources or can compile yourself following [this guide][ref:compile].

If you want to install syslog-ng on macOS you can use multiple packaga managers e.g. [homebrew][ref:homebrew]

## Homebrew

First, check [this][ref:install] if you have not got Homebrew installed and pre-configured yet.

[Homebrew][ref:homebrew] has now different home directories on ARM and X86 systems, also the location could depend on your macOS version.
We will reference to its home directory as `${HOMEBREW_PREFIX}` in this document, as if you follow the installation instructions above it will be set already correctly independenty of your system.

**Hint**: you can use `export HOMEBREW_PREFIX=$(brew --prefix)` in your scripts or shell environments to get and reference the actual location of your homewbrew installation

## Checking dependencies

The syslog-ng package on macOS in homebrew is organized into a formula called `syslog-ng`.

For checking dependencies of it you can use

```shell
brew deps syslog-ng
```

This will list all the required dependencies are needed to run syslog-ng, and homebrew would install automatically as needed.

## Installation

Using homebrew it is simple, use

```shell
brew install syslog-ng
```

This command line refers to the latest distribution of syslog-ng versions at the
time of writing, and usually updated quickly by the homwbrew crew after a new release.

## Starting syslog-ng

You can start `syslog-ng` many ways in foreground, e.g. in a terminal window

```shell
${HOMEBREW_PREFIX}/sbin/syslog-ng -F
```

this will start it as a foreground process in the terminal and write only minimal information to the console during its run.

To see more details you can specify some debug flags, like

```shell
${HOMEBREW_PREFIX}/sbin/syslog-ng -Fdevt
```

this will give you detailed information of what syslog-ng does.

## Running syslog-ng as daemon

You can start it manually as a backround daemon

```shell
${HOMEBREW_PREFIX}/sbin/syslog-ng
```

however this is not a persistent state, after a system restart syslog-ng will not start automatically by default.

To run it as a daemon that will automatically start at system startup and is kept alive you can use `launchd`

You can find several pages about `launchd` and how to add System or User Launch Daemons, Agents to macOS like [this][ref:freepascal-launchd], the official [Apple Developer page][ref:apple-launchd], or simply `man launchd`, `man launchctl`, and `man launchd.plist`

### Basic example of how to run it as a System Daemon

1. Create the following .plist file

   ```plist
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
   <dict>
      <key>Label</key>
      <string>com.syslog-ng.daemon</string>
      
      <key>RunAtLoad</key>
      <true/>
      <key>KeepAlive</key>
      <true/>
      
      <key>ProgramArguments</key>
      <array>
         <string>/opt/homebrew/sbin/syslog-ng</string>
         <string>-F</string>
      </array>

      <key>StandardOutPath</key>
      <string>/opt/homebrew/var/log/syslog-ng-daemon.stdout.log</string>
      <key>StandardErrorPath</key>
      <string>/opt/homebrew/var/log/syslog-ng-daemon.stderr.log</string>
   </dict>
   </plist>
   ```

2. name it e.g. `com.syslog-ng.daemon.plist`, and move it to `/Library/LaunchDaemons`

3. Set proper rights on the plist file

   ```shell
   sudo chown root:wheel /Library/LaunchDaemons/com.syslog-ng.daemon.plist
   sudo chmod 600 /Library/LaunchDaemons/com.syslog-ng.daemon.plist
   ```

That's all, macOS Launchd will take care of the rest, will start and keepalive the daemon after the next system restart

To start the new daemon immediately without machine restart you can use

```shell
sudo launchctl load -w /Library/LaunchDaemons/com.syslog-ng.daemon.plist
```

To stop it you can use

```shell
sudo launchctl unload -w /Library/LaunchDaemons/com.syslog-ng.daemon.plist
```
