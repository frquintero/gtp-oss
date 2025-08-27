"""Terminal input handler for managing multiline input and special key handling."""
import sys
from typing import Optional, List
from .input_history import InputHistory


class TerminalInputHandler:
    """Handles terminal input with multiline support and special key handling."""

    def __init__(self, cli_instance):
        """Initialize with reference to parent CLI instance."""
        self.cli = cli_instance
        self._current_buffer = []
        self.input_history = InputHistory(max_entries=100)

    def get_multiline_input(self, prefill_text: str = "") -> Optional[str]:
        """Get input using raw mode where:
        - Enter (Return) sends the prompt to the LLM
        - Ctrl+J inserts a newline into the message
        - Ctrl+C quits the application (raises KeyboardInterrupt)

        This uses low-level terminal control so blank lines are allowed in the
        message via Ctrl+J and a single Enter submits immediately.
        """

        # State tracking for Ctrl+C behavior
        ctrl_c_pressed_once = False
        # State tracking for ESC double-press reset behavior
        esc_reset_pending = False
        # State tracking for ESC sequence detection
        pending_esc = False

        # Show any prefill content and initialize buffer
        buffer: list[str] = []
        if prefill_text:
            # Print prefill lines for context
            for line in prefill_text.split('\n'):
                self.cli.console.print(f">> {line}")
            # Initialize buffer with prefill_text characters (including newlines)
            buffer = list(prefill_text)

        # Store buffer reference for cursor positioning
        self._current_buffer = buffer

        try:
            import termios
            import tty

            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)

            try:
                tty.setraw(fd)
                sys.stdout.write(">> ")
                sys.stdout.flush()

                # Print help message below the prompt
                self._print_help_message()

                while True:
                    ch = sys.stdin.read(1)
                    if not ch:
                        continue

                    # Handle pending ESC state first
                    if pending_esc:
                        pending_esc = False
                        if ch == '[':
                            # This is an escape sequence - read the final character
                            final_ch = sys.stdin.read(1)
                            if final_ch == 'A':  # Up arrow
                                history_entry = self.input_history.get_previous(''.join(buffer))
                                if history_entry is not None:
                                    buffer = self._replace_buffer_with_history(buffer, history_entry)
                                # Cancel ESC hint if visible
                                if esc_reset_pending:
                                    esc_reset_pending = self._reset_esc_state_and_restore_help()
                                    self._current_buffer = buffer
                                continue
                            elif final_ch == 'B':  # Down arrow
                                history_entry = self.input_history.get_next()
                                if history_entry is not None:
                                    buffer = self._replace_buffer_with_history(buffer, history_entry)
                                else:
                                    # At end of history - clear buffer
                                    buffer = self._replace_buffer_with_history(buffer, "")
                                # Cancel ESC hint if visible
                                if esc_reset_pending:
                                    esc_reset_pending = self._reset_esc_state_and_restore_help()
                                    self._current_buffer = buffer
                                continue
                            else:
                                # Other sequences - ignore
                                if esc_reset_pending:
                                    esc_reset_pending = self._reset_esc_state_and_restore_help()
                                    self._current_buffer = buffer
                                continue
                        else:
                            # ESC followed by non-bracket
                            # If it's another ESC, treat as double-ESC reset; otherwise, fall through.
                            if ch == "\x1b":
                                current_text = ''.join(buffer)
                                has_content = bool(current_text.strip())
                                if has_content and esc_reset_pending:
                                    buffer = self._clear_current_input_and_redraw(buffer)
                                    esc_reset_pending = False
                                    continue
                            # For any other non-ESC char, do nothing here; normal handling below will run

                    # Ctrl+C -> two-step quit mechanism
                    if ch == "\x03":
                        if ctrl_c_pressed_once:
                            # Second Ctrl+C -> prepare clean exit
                            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                            # Clear the help line below, then move back up to the prompt line start
                            sys.stdout.write("\n\033[2K\033[1A\r")
                            sys.stdout.flush()
                            raise KeyboardInterrupt
                        else:
                            # First Ctrl+C -> show quit confirmation message
                            ctrl_c_pressed_once = True
                            # Clear help message line and replace with quit confirmation
                            sys.stdout.write("\n\033[1G\033[2K")  # Move down, go to left margin, clear line
                            sys.stdout.write("\033[91mCtrl+C again to quit\033[0m")  # Red color for attention
                            # Move back up and position cursor after current text using relative positioning
                            cursor_column = len(">> " + ''.join(buffer)) + 1
                            sys.stdout.write(f"\033[1A\033[{cursor_column}G")
                            sys.stdout.flush()
                        continue

                    # Reset Ctrl+C state if any other key is pressed
                    if ctrl_c_pressed_once:
                        ctrl_c_pressed_once = self._reset_ctrl_c_state_and_restore_help()
                        # Update current buffer reference for cursor positioning
                        self._current_buffer = buffer

                    # Reset ESC reset state if a non-ESC key is pressed
                    if esc_reset_pending and ch != "\x1b":
                        esc_reset_pending = self._reset_esc_state_and_restore_help()
                        # Update current buffer reference for cursor positioning
                        self._current_buffer = buffer

                    # "/" -> open command palette (only if it's the first character)
                    if ch == "/" and not buffer:
                        # Restore terminal first
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                        try:
                            # Clear current line and open command palette
                            sys.stdout.write("\r\033[K")  # Clear current line
                            sys.stdout.flush()

                            # Open command palette
                            result = self.cli._open_command_palette()
                            if result == "exit":
                                return None  # Signal to exit

                            # Restore terminal for continued input
                            tty.setraw(fd)
                            sys.stdout.write(">> " + ''.join(buffer))
                            sys.stdout.flush()
                            # Restore help message
                            self._print_help_message()
                        except Exception as e:
                            # Restore terminal and continue
                            tty.setraw(fd)
                            sys.stdout.write(">> " + ''.join(buffer))
                            sys.stdout.flush()
                            # Restore help message
                            self._print_help_message()
                        continue

                    # Enter/Return (carriage return) -> submit or reposition if empty
                    # Note: many terminals send '\r' (13) for Enter; treat that as submit.
                    if ch == "\r" or ord(ch) == 13:
                        # Check if buffer is empty (no content to send)
                        if not buffer or not ''.join(buffer).strip():
                            # Empty line - just reposition cursor to after ">>"
                            # Clear current line and rewrite the prompt
                            sys.stdout.write("\r\033[K>> ")
                            sys.stdout.flush()
                            # Clear buffer if it had whitespace
                            buffer = []
                            continue
                        else:
                            # Has content - submit normally
                            sys.stdout.write("\n")
                            sys.stdout.flush()
                            break

                    # Ctrl+J (line feed, ASCII 10) -> insert newline only when current line has text
                    if ch == "\x0a":
                        # Only allow newline if the current line (after last \n) has content
                        current_text = ''.join(buffer)
                        last_line_text = current_text.split('\n')[-1]
                        if len(last_line_text) > 0:
                            buffer.append('\n')
                            # Update current buffer reference
                            self._current_buffer = buffer
                            # First, clear the help message that's currently below the cursor
                            sys.stdout.write("\n\033[2K")  # Move down and clear the help message line
                            sys.stdout.write("\033[1A")   # Move back up to the original line
                            # Now move to new line and print clean prompt at left margin
                            sys.stdout.write("\r\n>> ")
                            # Move down and print help message on the line below using relative positioning
                            sys.stdout.write("\n\033[1G\033[2K")  # New line, go to left margin, clear line
                            sys.stdout.write("\033[90m(\033[36mEnter\033[90m = send, \033[36mCtrl+J\033[90m = newline, \033[36mCtrl+C\033[90m = quit, \033[36m/\033[90m = command)\033[0m")
                            # Move back up one line and position cursor after ">> "
                            sys.stdout.write("\033[1A\033[4G")  # Move up and go to column 4 (after ">> ")
                            sys.stdout.flush()
                        # If current line is empty, ignore Ctrl+J
                        continue

                    # Backspace handling (prevent deleting the '>> ' prompt)
                    if ch in ("\x7f", "\x08"):
                        if not buffer:
                            continue
                        current_text = ''.join(buffer)
                        last_line = current_text.split('\n')[-1]
                        if buffer[-1] == '\n' or len(last_line) == 0:
                            # At start of a line: if last char is a newline, remove the empty line safely
                            if buffer[-1] == '\n':
                                # Remove newline from buffer
                                buffer.pop()
                                self._current_buffer = buffer
                                # Clear help line and current empty prompt line, then move to previous line end
                                sys.stdout.write("\n\033[2K")  # clear help below
                                sys.stdout.write("\033[1A")     # back to current line
                                sys.stdout.write("\r\033[2K")   # clear current line (the '>> ')
                                sys.stdout.write("\033[1A")     # move to previous line
                                # Move cursor to end of previous line content
                                prev_text = ''.join(buffer)
                                prev_last_len = len(prev_text.split('\n')[-1])
                                sys.stdout.write(f"\033[{4 + prev_last_len}G")
                                # Reprint help below previous line and restore cursor
                                self._print_help_message()
                            # If not a newline, and at column 0 for this line, do nothing (protect '>> ')
                            continue
                        else:
                            # Normal character deletion within the line
                            buffer.pop()
                            self._current_buffer = buffer
                            sys.stdout.write("\b \b")
                            sys.stdout.flush()
                        continue

                    # Handle ESC: set pending state and show hint immediately (plain ESC)
                    if ch == "\x1b":
                        # Assume plain ESC until proven sequence; show/cycle hint now
                        current_text = ''.join(buffer)
                        has_content = bool(current_text.strip())
                        if has_content:
                            if esc_reset_pending:
                                buffer = self._clear_current_input_and_redraw(buffer)
                                esc_reset_pending = False
                            else:
                                esc_reset_pending = True
                                self._show_esc_reset_message()
                        # Now mark that an escape sequence might follow (for arrows)
                        pending_esc = True
                        continue

                    # Printable character -> echo and append
                    buffer.append(ch)
                    # Reset history position when user starts typing new content
                    self.input_history.reset_position()
                    # Update current buffer reference
                    self._current_buffer = buffer
                    sys.stdout.write(ch)
                    sys.stdout.flush()

            finally:
                # Ensure terminal state is restored
                try:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                except Exception:
                    pass

        except KeyboardInterrupt:
            # User requested quit via Ctrl+C - clear help and prompt lines
            # Clear help line (below), then move back and clear prompt line
            sys.stdout.write("\n\033[2K\033[1A\r\033[2K")
            sys.stdout.flush()
            # Re-raise so outer run loop can print final message
            raise
        except Exception:
            # Fall back to the simple input() if raw mode fails
            try:
                line = input(">> ")
                if not line:
                    return None
                return line
            except Exception:
                self.cli.console.print("[yellow]Input cancelled.[/yellow]")
                return None

        content = ''.join(buffer)
        if not content.strip():
            self.cli.console.print("[yellow]Empty prompt cancelled.[/yellow]")
            return None

        # Add to history before returning
        self.input_history.add_entry(content)
        return content

    def _print_help_message(self):
        """Print the help message below the current cursor position at left margin."""
        # Move to next line, go to column 1 (left margin), and clear line
        sys.stdout.write("\n\033[1G\033[2K")
        # Print help with colored commands
        sys.stdout.write("\033[90m(\033[36mEnter\033[90m = send, \033[36mCtrl+J\033[90m = newline, \033[36mCtrl+C\033[90m = quit, \033[36m↑↓\033[90m = history, \033[36m/\033[90m = command)\033[0m")
        # Move back up one line and position cursor after ">> " plus any existing buffer content
        buffer_text = ''.join(getattr(self, '_current_buffer', []))
        # Compute position within the current (last) line only
        last_line_len = len(buffer_text.split('\n')[-1])
        cursor_column = 4 + last_line_len  # after ">> "
        sys.stdout.write(f"\033[1A\033[{cursor_column}G")
        sys.stdout.flush()

    def _clear_help_line(self):
        """Clear the help line below the current cursor position."""
        # Move down, clear the line, then move back up
        sys.stdout.write("\n\033[2K\033[1A")
        sys.stdout.flush()

    def _clear_current_input_and_redraw(self, current_buffer: List[str]) -> List[str]:
        """Clear all lines of current input, redraw prompt, and return a fresh buffer."""
        current_text = ''.join(current_buffer)
        lines = current_text.count('\n') + 1
        # Clear help line below, then clear all input lines
        sys.stdout.write("\n\033[2K")  # clear help below
        sys.stdout.write("\033[1A")     # back to current line
        for i in range(lines):
            sys.stdout.write("\r\033[2K")
            if i < lines - 1:
                sys.stdout.write("\033[1A")
        # Reset buffer and redraw prompt + help
        new_buffer: List[str] = []
        self._current_buffer = new_buffer
        sys.stdout.write(">> ")
        sys.stdout.flush()
        self._print_help_message()
        return new_buffer

    def _replace_buffer_with_history(self, current_buffer: List[str], history_entry: str) -> List[str]:
        """Replace current buffer with history entry and update display."""
        # Calculate how many lines current buffer occupies
        current_text = ''.join(current_buffer)
        current_lines = current_text.count('\n') + 1
        
        # Clear help line first
        sys.stdout.write("\n\033[2K")  # Clear help below
        sys.stdout.write("\033[1A")     # Back to current line
        
        # Clear all lines of current input by moving up and clearing each line
        for i in range(current_lines):
            sys.stdout.write("\r\033[2K")  # Go to beginning of line and clear completely
            if i < current_lines - 1:
                sys.stdout.write("\033[1A")  # Move up to previous line
        
        # Now we're at the first line, positioned at column 0
        # Display the prompt and new content
        sys.stdout.write(">> ")
        if history_entry:
            sys.stdout.write(history_entry)
        
        # Create new buffer from history entry
        new_buffer = list(history_entry) if history_entry else []
        self._current_buffer = new_buffer
        
        sys.stdout.flush()
        
        # Restore help message
        self._print_help_message()
        
        return new_buffer

    def _reset_ctrl_c_state_and_restore_help(self):
        """Reset Ctrl+C state and restore original help message."""
        # Clear quit confirmation message and restore help
        sys.stdout.write("\n\033[1G\033[2K")  # Move down, go to left margin, clear line
        sys.stdout.write("\033[90m(\033[36mEnter\033[90m = send, \033[36mCtrl+J\033[90m = newline, \033[36mCtrl+C\033[90m = quit, \033[36m↑↓\033[90m = history, \033[36m/\033[90m = command)\033[0m")
        # Calculate current buffer length to position cursor correctly
        buffer_text = ''.join(getattr(self, '_current_buffer', []))
        cursor_column = len(">> " + buffer_text) + 1
        sys.stdout.write(f"\033[1A\033[{cursor_column}G")  # Move back up and position after current text
        sys.stdout.flush()
        return False  # Return False to reset ctrl_c_pressed_once

    def _show_esc_reset_message(self):
        """Show the red confirmation message for ESC-based reset on the help line."""
        # Clear help message line and replace with confirmation
        sys.stdout.write("\n\033[1G\033[2K")  # Move down, go to left margin, clear line
        sys.stdout.write("\033[91mHit Esc again to start over\033[0m")  # Red color
        # Move back up and position cursor after current text using relative positioning
        buffer_text = ''.join(getattr(self, '_current_buffer', []))
        last_line_len = len(buffer_text.split('\n')[-1])
        cursor_column = 4 + last_line_len
        sys.stdout.write(f"\033[1A\033[{cursor_column}G")
        sys.stdout.flush()

    def _reset_esc_state_and_restore_help(self):
        """Restore the normal help line after an ESC confirmation hint."""
        self._print_help_message()
        return False  # Return False to reset esc_reset_pending
