# Sublime Stata Enhanced

* Version 2.0.2
* Date: June 29, 2014

This package basic support for Stata (11–13, Windows and OS X) and comes with:

* Language definition for `.do` and `.ado` files 
* Commands for sending individual lines or selections to Stata (available via the command palette and with keyboard shortcuts):
	* (*Stata 13, OS X only*) Send current line or selection to Stata: `super+enter`
	* (*Stata 11, 12; OS X only*) Send current line or selection to Stata: `super+alt+enter`
	* (*Stata 11–13; Windows only*) Send current line or selection to Stata: `ctrl+enter`
* (*OS X only*) A build system for Stata files

**NB**: If you use Stata < 13 on OS X, you'll probably want to reconfigure those keyboard shortcuts in `Default (OSX).sublime-keymap` so that `super+enter` runs `stata-send-command-move-next-line.sublime-macro` instead of `stata-send-command-move-next-line13.sublime-macro`.


## Background

This is a modified version of [Steve Harris's Stata package](https://github.com/docsteveharris/stata). Because of scripting limitations in Stata < 12, his version relied on creating temporary `.do` files to pass commands to Stata. Stata 13 added fancy new AppleScript commands (specifically `DoCommand` and `DoCommandAsync`) that allow for scripted commands and eliminate the need for temporary files. Because of that, this package is far simpler than other Sublime Text packages.

For compatability with previous versions of Stata, however, I have included commands that create temporary files, as in the original Stata package. As such, this package works with Stata 11 and above on both OS X and Windows.


## Installation

There are two ways to install this package:

1. Search for "Stata Enhanced" on [Package Control](https://sublime.wbond.net/)
2. Copy the entire plugin folder to `~/Library/Application Support/Sublime Text 2/Packages` or `~/Library/Application Support/Sublime Text 3/Packages`


## Configuration options

### OS X

* (**All versions of Stata**) Set the name of your Stata installation in `Stata Enhanced (OS X).sublime-settings` (default is `StataSE`)
* (**Stata 11 and 12 only**) This package sends selected code to a temporary file and then opens that file in Stata via Finder. In order for it to work correctly on your system, you must ensure two things are true:
	1. `.do` files must be set to open in Stata by default in Finder (right click on a `.do` file > "Get Info" > "Open with" > "Change all…" > Select Stata. 
	2. `.do` files opened in Stata need to be run, not edited. Change this in Preferences > Do-file Editor > Advanced > Edit do-files opened from the Finder in Do-file Editor (uncheck this)

### Windows

* (**All versions of Stata**) Set the full path of your Stata installation (with slashes reversed) in `Stata Enhanced (Windows).sublime-settings` (default is `"C:/Program Files (x86)/Stata13/StataSE-64.exe"`)
* This package sends selected code to a temporary file and then opens that file in Stata via Finder. In order for it to work correctly on your system, you must ensure that `.do` files opened in Stata are run, not edited. Change this in Do-file Editor > Edit > Preferences > Advanced > Edit do-files opened from Windows instead of executing them (uncheck this)


## Roadmap and wish list

* Stata 13 for Windows [has support for Automation APIs](http://www.stata.com/automation/). It would be cool to use those instead of temporary files (like how the OS X version of the plugin uses temporary files for Stata 11–12, but the API for 13).
* There is a setting for the Stata version, but it doesn't do anything yet. It would be nice to have run the appropriate command without having almost-duplicate `stata-send-command-move-next-line.sublime-macro` and `stata-send-command-move-next-line13.sublime-macro` files. However, I don't see a way to use setting variables in macro files. 
* (*Temporarily taken care of for now by opening the file through Finder instead of Stata on OS X*).  
In the build file, the `osascript ...` command works, but gives the following error: `error "No result was returned from some part of this expression." number -2763`. The plugin currently fixes that by wrapping the command in `try` and `end try` commands. It would be nice to not have to do that, though.
