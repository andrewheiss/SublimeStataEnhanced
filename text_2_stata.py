import os
import sublime_plugin
import sublime
import subprocess

settingsfile = "Stata 13.sublime-settings"

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

		# Send the command to Stata with AppleScript
		cmd = """osascript<< END
		 tell application "{0}"
			# activate
			DoCommandAsync "{1}" with addToReview
		 end tell
		 END""".format(settings.get('stata_name'), all_text.replace('"', '\\"').replace('`', '\\`').strip()) 
		print(cmd)
		os.system(cmd)


class text_2_stataCommand(sublime_plugin.TextCommand):
	""" Run selection or current line in Stata through a temporary file (for Stata < 13) """
	def run(self, edit):
		# Get the selection; if nothing is selected, get the current line
		all_text = ""
		sels = self.view.sel()
		for sel in sels:
			all_text = all_text + self.view.substr(sel)
		if len(all_text) == 0:
			all_text = self.view.substr(self.view.line(sel)) 
		all_text = all_text + "\n"

		# Get the path to the current rile
		filename = self.view.file_name()
		filepath = os.path.dirname(filename)

		# Write the selection to a temporary file in the current directory
		dofile_path = os.path.join(filepath, 'sublime2stata.do')
		this_file = open(dofile_path,'w')
		this_file.write(all_text)
		this_file.close()

		# Open the temporary do file in Stata
		cmd = """osascript -e 'tell application "Finder" to open POSIX file "{0}"' &""".format(dofile_path)
		os.system(cmd)
