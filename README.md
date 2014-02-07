# Sublime Stata Enhanced

* Version 1.1.3
* Date: February 6, 2014

This package basic support for Stata (11–13!) and comes with:

* (*All versions of Stata*) Language definition for `.do` and `.ado` files 
* (*All versions of Stata, OS X only*) A build system for Stata files
* Commands for sending individual lines or selections to Stata (available via the command palette and with keyboard shortcuts):
	* (*Stata 13, OS X only*) Send current line or selection to Stata: `super+enter`
	* (*Stata 11, 12; OS X only*) Send current line or selection to Stata: `super+alt+enter`

If you use Stata < 13, you'll probably want to reconfigure those keyboard shortcuts in `Default (OSX).sublime-keymap` so that `super+enter` runs `stata-send-command-move-next-line.sublime-macro` instead of `stata-send-command-move-next-line13.sublime-macro`.


## Background

This is a modified version of [Steve Harris's Stata package](https://github.com/docsteveharris/stata). Because of scripting limitations in Stata < 12, his version relied on creating temporary `.do` files to pass commands to Stata. Stata 13 added fancy new AppleScript commands (specifically `DoCommand` and `DoCommandAsync`) that allow for scripted commands and eliminate the need for temporary files. Because of that, this package is far simpler than other Sublime Text packages.

For compatability with previous versions of Stata, however, I have included commands that create temporary files, as in the original Stata package. As such, this package works with Stata 11 and above.


## Installation

There are two ways to install this package:

1. Search for "Stata Enhanced" on [Package Control](https://sublime.wbond.net/)
2. Copy the entire plugin folder to `~/Library/Application Support/Sublime Text 2/Packages` or `~/Library/Application Support/Sublime Text 3/Packages`


## Configuration options

* Set the name of your Stata installation in `Stata Enhanced.sublime-settings` (default is StataSE)


## Known issues

* (**Stata 13 only**) Stata *really* hates running comments in the command window. Inline comments like `*`, `\\`, and `\* ... \*` will often result in errors when running lines individually. This is a limitation with Stata. Comments are allowed in `.do` files, but not really in the command window (see [this](http://www.stata.com/statalist/archive/2010-12/msg00372.html)). So skip commented lines if you run lines individually.


## Roadmap and wish list

* This only works on OS X since all commands rely on `osascript`. Adding Windows support would be cool (Stata 13 on Windows [has support for automation APIs](http://www.stata.com/automation/)).
* There is a setting for the Stata version, but it doesn't do anything yet. It would be nice to have run the appropriate command without having almost-duplicate `stata-send-command-move-next-line.sublime-macro` and `stata-send-command-move-next-line13.sublime-macro` files. However, I don't see a way to use setting variables in macro files. 
* (*Temporarily taken care of for now by opening the file through Finder instead of Stata*).  
In the build file, the `osascript ...` command works, but gives the following error: `error "No result was returned from some part of this expression." number -2763`. The plugin currently fixes that by wrapping the command in `try` and `end try` commands. It would be nice to not have to do that, though.
