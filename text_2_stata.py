import os
import sublime_plugin
import sublime

class text_2_stataCommand(sublime_plugin.TextCommand):
	""" Run selection or current line in Stata """

	def run(self, edit):
		#  grab the selection
		#  if nothing selected then send the line
		all_text = ""
		sels = self.view.sel()
		for sel in sels:
			all_text = all_text + self.view.substr(sel)
		if len(all_text) == 0:
			all_text = self.view.substr(self.view.line(sel)) 
		all_text = all_text + "\n"

		#  Run the command with AppleScript
		cmd = """osascript<< END
		 tell application "StataSE"
			# activate
			DoCommandAsync "%s" with addToReview
		 end tell
		 END""" % all_text.replace('"', '\\"').replace('`', '\\`').strip() 
		os.system(cmd)
