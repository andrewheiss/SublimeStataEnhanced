import os
import sublime_plugin
import sublime
import re

settingsfile = "Stata Enhanced.sublime-settings"

def strip_inline_comments(text):
	# This is really brute force and hackish. Ideally we could use ST scopes to
	# only remove comments instead of trying to parse everything with regex
	# (since there will inevitably be edge cases that should/shouldn't be
	# removed). ST kind of has that functionality: 
	# 	self.view.find_by_selector('comment')
	# But this is a good stopgap for now.
	clean = text

	# Take care of line continuation
	clean = re.sub("/{3,}\\n", "", clean)

	# Remove /* ... */ comments (handles multiple lines) + // comments
	#
	# Bonus! Handles these cases correctly:
	#  * "This is a /* string */"
	#  * "This is // also a string"
	#  * "URLs work too. http://www.example.com"
	#
	# Code adapted from http://stackoverflow.com/a/18381470/120898
	def remove_comments(string):
		pattern = r"(\".*?(?<!\\)\"|\'.*?(?<!\\)\')|(/\*.*?\*/|//[^\r\n]*$)"
		# pattern = r"(\".*?\"|\'.*?\')|(/\*.*?\*/|//[^\r\n]*$)"  # Original
		# First group captures quoted strings (double or single)
		# Second group captures comments (//single-line or /* multi-line */)
		regex = re.compile(pattern, re.MULTILINE|re.DOTALL)
		def _replacer(match):
			# If the 2nd group (capturing comments) is not None,
			# it means we have captured a non-quoted (real) comment string.
			if match.group(2) is not None:
				return ""  # So we will return empty to remove the comment
			else:  # Otherwise, we will return the 1st group
				return match.group(1)  # Captured quoted-string
		return regex.sub(_replacer, string)

	clean = remove_comments(clean)

	# Escape $s, since AppleScript parses them as variables
	# clean = re.sub("\\$", "\\$", clean)

	return(clean)


class text_2_stata13Command(sublime_plugin.TextCommand):
	""" Run selection or current line *directly* in Stata (for Stata 13) """

	def run(self, edit):
		settings = sublime.load_settings(settingsfile)

		# Get the selection; if nothing is selected, get the current line
		all_text = ""
		sels = self.view.sel()
		for sel in sels:
			all_text = all_text + self.view.substr(sel)
		if len(all_text) == 0:
			all_text = self.view.substr(self.view.line(sel)) 
		all_text = all_text + "\n"

		# Get rid of inline comments
		all_text = strip_inline_comments(all_text)

		# Send the command to Stata with AppleScript
		cmd = """osascript<< END
		 tell application "{0}"
			# activate
			DoCommandAsync "{1}" with addToReview
		 end tell
		 END""".format(settings.get('stata_name'), 
		 	all_text.replace('"', '\\"').replace('`', '\\`').
		 	replace('$', "\\$").strip()) 
		print(cmd)
		os.system(cmd)


class text_2_stataCommand(sublime_plugin.TextCommand):
	""" Run selection or current line in Stata through a temporary file (for Stata < 13) """
	def run(self, edit):
		settings = sublime.load_settings(settingsfile)
		
		# Get the selection; if nothing is selected, get the current line
		all_text = ""
		sels = self.view.sel()
		for sel in sels:
			all_text = all_text + self.view.substr(sel)
		if len(all_text) == 0:
			all_text = self.view.substr(self.view.line(sel)) 
		all_text = all_text + "\n"

		# Get rid of inline comments
		all_text = strip_inline_comments(all_text)

		# Get the path to the current rile
		filename = self.view.file_name()
		filepath = os.path.dirname(filename)

		# Write the selection to a temporary file in the current directory
		dofile_path = os.path.join(filepath, 'sublime2stata.do')
		this_file = open(dofile_path,'w')
		this_file.write(all_text)
		this_file.close()

		# Open the temporary do file in Stata
		if sublime.platform() == "osx":
			# Get ST version for returning focus to ST
			if int(sublime.version()) > 3000:
				st_name = "Sublime Text"
			else:
				st_name = "Sublime Text 2"

			cmd = """osascript -e 'tell application "Finder" to open POSIX file "{0}"' -e 'tell application "{1}" to activate' &""".format(dofile_path, st_name)
			os.system(cmd)
		elif sublime.platform() == "windows":
			vbs_cmd = """CreateObject("WScript.Shell").Run \"\""{0}\"" \""{1}\"\"", 4, false """.format(settings.get('stata_name'), dofile_path)

			vbs_path = os.path.join(filepath, 'open_in_stata.vbs')
			vbs_file = open(vbs_path, 'w')
			vbs_file.write(vbs_cmd)
			vbs_file.close()

			cmd = "cscript.exe {0}".format("\""+vbs_path+"\"")
			os.system(cmd)
			os.remove(vbs_path)
