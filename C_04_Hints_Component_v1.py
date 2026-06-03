from tkinter import *
from functools import partial  # To prevent unwanted windows


class StartQuiz:
    """
    Simplified start interface for testing the Hints component.
    Launches Play with hardcoded test data (no real quiz logic needed here).
    """

    def __init__(self):
        """
        Gets number of questions from user
        """

        self.start_frame = Frame(padx=10, pady=10)
        self.start_frame.grid()

        # Create play button (simplified — just for testing Hints)
        self.play_button = Button(self.start_frame, font=("Arial", 16, "bold"),
                                  fg="#FFFFFF", bg="#0057D8", text="Play", width=10,
                                  command=self.check_questions)
        self.play_button.grid(row=0, column=1, padx=20, pady=20)

    def check_questions(self):
        """
        Launches Play class with hardcoded test question for hint testing.
        """
        Play(1)
        root.withdraw()


class Play:
    """
    Simplified game interface for testing the Hints system.
    Uses hardcoded question data so hints can be developed independently.
    """

    def __init__(self, how_many):

        self.play_box = Toplevel()
        self.play_box.title("Football Nickname Quiz")

        self.game_frame = Frame(self.play_box)
        self.game_frame.grid(padx=10, pady=10)

        # Hint state variables
        self.hints_used = 0
        self.hint1_used = False
        self.hint2_used = False

        # --- Hardcoded test question data ---
        self.current_club = "Arsenal"
        self.current_answer = "Gunners"
        self.current_hint_team = ("A North London club founded in 1886, known for "
                                  "playing at the Emirates Stadium.")
        self.current_hint_nick = ("Their nickname relates to the club's origins — "
                                  "workers from a weapons factory.")

        body_font = ("Arial", 12)

        # Heading label
        self.heading_label = Label(self.game_frame,
                                   text="Question 1 of 1",
                                   font=("Arial", 16, "bold"))
        self.heading_label.grid(row=0, pady=10, padx=10)

        # Score label
        self.score_label = Label(self.game_frame,
                                 text="Score: 0",
                                 font=body_font, bg="#FFF2CC")
        self.score_label.grid(row=1, pady=10, padx=10)

        # Instruction label
        Label(self.game_frame,
              text="Guess the nickname of the football club below. Good luck. ⚽",
              font=body_font, bg="#D5E8D4",
              wraplength=300, justify="left", padx=10).grid(row=2, pady=10, padx=10)

        # Club name display
        self.club_label = Label(self.game_frame,
                                text=self.current_club,
                                font=("Arial", 14, "bold"),
                                bg="#FFFFFF", relief="solid", width=25)
        self.club_label.grid(row=3, pady=10, padx=10)

        # Hint display label — shows prompt before any hint is clicked
        self.hint_label = Label(self.game_frame,
                                text="Use the hints below if you're stuck! 💡",
                                font=body_font, bg="#FFF2CC",
                                wraplength=300, justify="left")
        self.hint_label.grid(row=4, pady=5, padx=10)

        # Hints frame
        self.hints_frame = Frame(self.game_frame)
        self.hints_frame.grid(row=5, pady=5)

        # Hint buttons: [text | command | col]
        hint_button_list = [
            ["Hint 1", self.show_hint_1, 0],
            ["Hint 2", self.show_hint_2, 1],
        ]

        hint_ref_list = []
        for item in hint_button_list:
            btn = Button(self.hints_frame, text=item[0], bg="#FF8000",
                         command=item[1], font=("Arial", 16, "bold"),
                         fg="#FFFFFF", width=10)
            btn.grid(row=0, column=item[2], padx=5, pady=5)
            hint_ref_list.append(btn)

        self.hint1_button = hint_ref_list[0]
        self.hint2_button = hint_ref_list[1]

        # End game button
        self.end_game_button = Button(self.game_frame, text="End Game",
                                      font=("Arial", 16, "bold"),
                                      fg="#FFFFFF", bg="#990000", width=21,
                                      command=self.close_play)
        self.end_game_button.grid(row=6, pady=10)

    def show_hint_1(self):
        """
        Reveals Hint 1: a clue about the football club's location / history.
        Costs 1 point. Button is disabled after use so it can't be clicked twice.
        Replaces the default prompt text with the hint content.
        """
        if not self.hint1_used:
            self.hint1_used = True
            self.hints_used += 1
            self.hint1_button.config(state=DISABLED, text="Hint 1 ✓")
            self.hint_label.config(
                text="💡 Club Hint: {}".format(self.current_hint_team))

    def show_hint_2(self):
        """
        Reveals Hint 2: a clue about the meaning of the nickname.
        Costs 1 point. Button is disabled after use so it can't be clicked twice.
        Appends to existing hint text if Hint 1 was also used.
        """
        if not self.hint2_used:
            self.hint2_used = True
            self.hints_used += 1
            self.hint2_button.config(state=DISABLED, text="Hint 2 ✓")
            current_text = self.hint_label.cget("text")
            # If Hint 1 is already showing, append on a new line
            if "Club Hint" in current_text:
                self.hint_label.config(
                    text="{}\n🔍 Nickname Hint: {}".format(
                        current_text, self.current_hint_nick))
            else:
                self.hint_label.config(
                    text="🔍 Nickname Hint: {}".format(self.current_hint_nick))

    def close_play(self):
        """
        Closes the play window and returns to the start screen.
        """
        root.deiconify()
        self.play_box.destroy()


# main routine
if __name__ == "__main__":
    root = Tk()
    root.title("Football Nickname Quiz")
    StartQuiz()
    root.mainloop()