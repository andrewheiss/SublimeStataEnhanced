import os
import sublime_plugin
import sublime
import re
import subprocess

settingsfile = "Stata Enhanced.sublime-settings"

def strip_inline_comments(text):
    # This is really brute force and hackish. Ideally we could use ST scopes to
    # only remove comments instead of trying to parse everything with regex
    # (since there will inevitably be edge cases that should/shouldn't be
    # removed). ST kind of has that functionality:
    #   self.view.find_by_selector('comment')
    # But this is a good stopgap for now.
    clean = text

    # Take care of line continuation
    clean = re.sub("/{3,}.*\\n", " ", clean)

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
        regex = re.compile(pattern, re.MULTILINE | re.DOTALL)

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

def get_stata_version(stata_name):
    if stata_name != "auto": # get application identifier for user-set Stata
        cmd = ["osascript", "-e", "return id of application \"{}\"".format(stata_name)]
        try:
            stata_app_id = subprocess.check_output(cmd)
        except subprocess.CalledProcessError:
            sublime.error_message("User-defined version of Stata not found.")
            raise Exception("User-defined version of Stata not found.")

        stata_app_id = stata_app_id.decode("utf-8").strip()
        version = int(stata_app_id[-2:])
        return((version, stata_app_id))

    else: # figure out Stata version automatically
        cmd = """osascript<< END
                    try
                        tell me to get application id "com.stata.stata15"
                        set stata to 15
                    end try
                    try
                        tell me to get application id "com.stata.stata14"
                        set stata to 14
                    end try
                    try
                        tell me to get application id "com.stata.stata13"
                        set stata to 13
                    end try
                    try
                        tell me to get application id "com.stata.stata12"
                        set stata to 12
                    end try
                    try
                        tell me to get application id "com.stata.stata11"
                        set stata to 11
                    end try
                    return stata
                END"""
        try:
            version = subprocess.check_output(cmd, shell=True)
        except subprocess.CalledProcessError:
            sublime.error_message("No version of Stata found.")
            raise Exception("No version of Stata found.")

        version = version.decode("utf-8").strip()
        return((int(version), "com.stata.stata{}".format(version)))


class StataRunCompleteCommand(sublime_plugin.WindowCommand):
    """ Runs the complete do file in Stata. """

    def run(self):
        self.window.run_command('save')
        file_name = self.window.active_view().file_name()
        settings = sublime.load_settings(settingsfile)

        # Switch focus to Stata or not after sending a command depending on a setting
        if settings.get('switch_focus_to_stata'):
            switch_focus = "activate"
        else:
            switch_focus = ""

        if sublime.platform() == "osx":
            version, stata_app_id = get_stata_version(settings.get('stata_name'))

        if sublime.platform() == "osx" and version >= 13:
            cmd = """osascript<< END
                 tell application id "{}"
                    {}
                    DoCommandAsync "do \\\"{}\\\"" with addToReview
                 end tell
                 END""".format(stata_app_id, switch_focus, file_name)
            os.system(cmd)
        elif sublime.platform() == "osx" and version <= 12:
            # Get ST version for returning focus to ST
            if int(sublime.version()) > 3000:
                st_name = "Sublime Text"
            else:
                st_name = "Sublime Text 2"

            cmd = """osascript -e 'tell application "Finder" to open POSIX file "{0}"' -e 'tell application "{1}" to activate' &""".format(file_name, st_name)
            os.system(cmd)
        elif sublime.platform() == "windows":
            filepath = os.path.dirname(file_name)
            
            vbs_cmd = """CreateObject("WScript.Shell").Run \"\""{0}\"" \""{1}\"\"", 4, false """.format(settings.get('stata_name'), file_name)

            vbs_path = os.path.join(filepath, 'open_in_stata.vbs')
            vbs_file = open(vbs_path, 'w')
            vbs_file.write(vbs_cmd)
            vbs_file.close()

            cmd = "cscript.exe {0}".format("\"" + vbs_path + "\"")
            os.system(cmd)
            os.remove(vbs_path)

class text_2_stataCommand(sublime_plugin.TextCommand):
    """ Run selection or current line *directly* in Stata"""

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

        # Switch focus to Stata or not after sending a command depending on a setting
        if settings.get('switch_focus_to_stata'):
            switch_focus = "activate"
        else:
            switch_focus = ""
    
        if sublime.platform() == "osx":
            version, stata_app_id = get_stata_version(settings.get('stata_name'))

        if sublime.platform() == "osx" and version >= 13:
            all_text = all_text.replace('\\', '\\\\\\').replace('"', '\\"'). \
                replace('`', '\\`').replace('$', "\\$").strip()

            # Stata only allows 8192 characters.
            if len(all_text)<8192:
                # Send the command to Stata with AppleScript
                cmd = """osascript<< END
                 tell application id "{}"
                    {}
                    DoCommandAsync "{}" with addToReview
                 end tell
                 END""".format(stata_app_id, switch_focus, all_text)
                print(cmd)
                os.system(cmd)
            else:
                if sublime.ok_cancel_dialog("This selection is too long to run.\n\nWould you like to run the whole do file?", "Run complete file"):
                    self.view.window().run_command("stata_run_complete")
        
        elif sublime.platform() == "osx" and version <= 12:
            # Get the path to the current file
            filename = self.view.file_name()
            filepath = os.path.dirname(filename)

            # Write the selection to a temporary file in the current directory
            dofile_path = os.path.join(filepath, 'sublime2stata.do')
            this_file = open(dofile_path, 'w')
            this_file.write(all_text)
            this_file.close()

            # Get ST version for returning focus to ST
            if int(sublime.version()) > 3000:
                st_name = "Sublime Text"
            else:
                st_name = "Sublime Text 2"

            cmd = """osascript -e 'tell application "Finder" to open POSIX file "{0}"' -e 'tell application "{1}" to activate' &""".format(dofile_path, st_name)
            os.system(cmd)
        
        elif sublime.platform() == "windows":
            # Get the path to the current file
            filename = self.view.file_name()
            filepath = os.path.dirname(filename)

            # Write the selection to a temporary file in the current directory
            dofile_path = os.path.join(filepath, 'sublime2stata.do')
            this_file = open(dofile_path, 'w')
            this_file.write(all_text)
            this_file.close()

            vbs_cmd = """CreateObject("WScript.Shell").Run \"\""{0}\"" \""{1}\"\"", 4, false """.format(settings.get('stata_name'), dofile_path)

            vbs_path = os.path.join(filepath, 'open_in_stata.vbs')
            vbs_file = open(vbs_path, 'w')
            vbs_file.write(vbs_cmd)
            vbs_file.close()

            cmd = "cscript.exe {0}".format("\"" + vbs_path + "\"")
            os.system(cmd)
            os.remove(vbs_path)
