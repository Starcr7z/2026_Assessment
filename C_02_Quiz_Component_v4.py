from tkinter import *
from functools import partial  # To prevent unwanted windows
import pandas as pd
import random


def get_questions():
    """
    Retrieves football club data from Excel file.
    Returns a list of lists: [club, nickname, hint_team, hint_nick]
    """
    df = pd.read_excel("football.xlsx")
    questions = []
    for _, row in df.iterrows():
        questions.append([
            row["Football Team"],
            row["Football Nickname"],
            row["Hint for Football Team"],
            row["Hint for Nickname"]
        ])
    return questions


class StartQuiz:
    """
    Initial Game interface (asks users how many questions they
    would like to answer in the football nickname quiz).
    Unchanged from v2 — this version adds hints to the Play class.
    """

    def __init__(self):
        """
        Gets number of questions from user
        """

        self.start_frame = Frame(padx=10, pady=10)
        self.start_frame.grid()

        intro_string = ("Each question shows a football club and 4 nickname options. "
                        "Pick the correct answer to score points. "
                        "You can use up to 2 hints per question — each hint "
                        "costs 1 point from your potential score.\n\n"
                        "Correct, no hints used = 3 points\n"
                        "Correct, 1 hint used = 2 points\n"
                        "Correct, 2 hints used = 1 point\n"
                        "Wrong answer (no hints used) = 0 points\n"
                        "Wrong answer (any hints used) = -1 points")

        choose_string = "How many questions do you want to answer?"

        start_labels_list = [
            ["Football Nickname Quiz ⚽", ("Arial", 16, "bold"), None],
            [intro_string, ("Arial", 12), None],
            [choose_string, ("Arial", 12, "bold"), "#009900"]
        ]

        start_label_ref = []
        for count, item in enumerate(start_labels_list):
            make_label = Label(self.start_frame, text=item[0], font=item[1],
                               fg=item[2],
                               wraplength=350, justify="left", pady=10, padx=20)
            make_label.grid(row=count)
            start_label_ref.append(make_label)

        self.choose_label = start_label_ref[2]

        self.entry_area_frame = Frame(self.start_frame)
        self.entry_area_frame.grid(row=3)

        self.num_questions_entry = Entry(self.entry_area_frame, font=("Arial", 20, "bold"),
                                         width=10)
        self.num_questions_entry.grid(row=0, column=0, padx=10, pady=10)

        self.play_button = Button(self.entry_area_frame, font=("Arial", 16, "bold"),
                                  fg="#FFFFFF", bg="#0057D8", text="Play", width=10,
                                  command=self.check_questions)
        self.play_button.grid(row=0, column=1)

        self.exit_button = Button(self.start_frame, font=("Arial", 12, "bold"),
                                  fg="#FFFFFF", bg="#990000", text="Exit", width=10,
                                  command=self.start_frame.quit)
        self.exit_button.grid(row=4, pady=10)

    def check_questions(self):
        """
        Validates number of questions entered (whole number, 1 to MAX_QUESTIONS).
        Launches Play class with loaded questions if valid.
        """

        MAX_QUESTIONS = 100

        questions_wanted = self.num_questions_entry.get()

        self.choose_label.config(fg="#009900", font=("Arial", 12, "bold"),
                                 text="How many questions do you want to answer?")
        self.num_questions_entry.config(bg="#FFFFFF")

        error = "Oops - Please choose a whole number between 1 and {}.".format(MAX_QUESTIONS)
        has_errors = "no"

        try:
            questions_wanted = int(questions_wanted)
            if 1 <= questions_wanted <= MAX_QUESTIONS:
                all_questions = get_questions()
                Play(questions_wanted, all_questions)
                root.withdraw()
            else:
                has_errors = "yes"

        except ValueError:
            has_errors = "yes"

        if has_errors == "yes":
            self.choose_label.config(text=error, fg="#990000",
                                     font=("Arial", 10, "bold"))
            self.num_questions_entry.config(bg="#F4CCCC")
            self.num_questions_entry.delete(0, END)


class Play:
    """
    Interface for playing the Football Nickname Quiz.
    v4: Hint display area now shows a prompt before any hint is used.
    Hint 1 and Hint 2 buttons reveal clues about the club and nickname.
    Each hint used reduces potential score by 1.
    Hint buttons are locked after use and disabled after answering.
    """

    def __init__(self, how_many, all_questions):
        self.play_box = Toplevel()
        self.play_box.title("Football Nickname Quiz")

        # If users press the 'x', end the entire game
        self.play_box.protocol('WM_DELETE_WINDOW', root.destroy)

        self.game_frame = Frame(self.play_box)
        self.game_frame.grid(padx=10, pady=10)

        # Game state variables
        self.total_questions = how_many
        self.question_number = 0
        self.score = 0
        self.hints_used = 0
        self.current_answer = ""
        self.answer_buttons_ref = []

        # Shuffle and trim to requested number
        self.question_list = random.sample(all_questions, how_many)
        self.all_questions = all_questions  # Keep full pool for wrong answer options

        body_font = ("Arial", 12)

        # Labels: [text | font | bg | row]
        play_labels_list = [
            ["Question 0 of {}".format(how_many), ("Arial", 16, "bold"), None, 0],
            ["Score: 0", body_font, "#FFF2CC", 1],
            ["Guess the nickname of the football club below. Good luck. ⚽", body_font, "#D5E8D4", 2],
            ["", body_font, None, 5]
        ]

        play_labels_ref = []
        for item in play_labels_list:
            make_label = Label(self.game_frame, text=item[0], font=item[1],
                               bg=item[2], wraplength=300, justify="left", padx=10)
            make_label.grid(row=item[3], pady=10, padx=10)
            play_labels_ref.append(make_label)

        self.heading_label = play_labels_ref[0]
        self.score_label = play_labels_ref[1]
        self.results_label = play_labels_ref[3]

        # Club name display label
        self.club_label = Label(self.game_frame, text="",
                                font=("Arial", 14, "bold"),
                                bg="#FFFFFF", relief="solid", width=25)
        self.club_label.grid(row=3, pady=10, padx=10)

        # Hint text label — shows prompt before any hint is used
        self.hint_label = Label(self.game_frame, text="Use the hints below if you're stuck! 💡",
                                font=body_font, bg="#FFF2CC",
                                wraplength=300, justify="left")
        self.hint_label.grid(row=4, pady=5, padx=10)

        # 2x2 answer buttons frame
        self.answer_frame = Frame(self.game_frame)
        self.answer_frame.grid(row=6)

        for i in range(4):
            btn = Button(self.answer_frame, font=("Arial", 12),
                         text="", width=15, bg="#FFFFFF",
                         command=partial(self.check_answer, i))
            btn.grid(row=i // 2, column=i % 2, padx=5, pady=5)
            self.answer_buttons_ref.append(btn)

        # Hints / Stats frame
        self.hints_stats_frame = Frame(self.game_frame)
        self.hints_stats_frame.grid(row=8)

        # Control buttons: [frame | text | bg | command | width | row | col]
        control_button_list = [
            [self.game_frame, "Next Question", "#0057D8", self.next_question, 21, 7, None],
            [self.hints_stats_frame, "Hint 1", "#FF8000", self.show_hint_1, 10, 0, 0],
            [self.hints_stats_frame, "Hint 2", "#FF8000", self.show_hint_2, 10, 0, 1],
            [self.hints_stats_frame, "Stats", "#333333", "", 10, 0, 2],
            [self.game_frame, "End Game", "#990000", self.close_play, 21, 9, None]
        ]

        control_ref_list = []
        for item in control_button_list:
            btn = Button(item[0], text=item[1], bg=item[2],
                         command=item[3], font=("Arial", 16, "bold"),
                         fg="#FFFFFF", width=item[4])
            btn.grid(row=item[5], column=item[6], padx=5, pady=5)
            control_ref_list.append(btn)

        self.next_button = control_ref_list[0]
        self.hint1_button = control_ref_list[1]
        self.hint2_button = control_ref_list[2]
        self.stats_button = control_ref_list[3]

        # Disable next and stats at start
        self.next_button.config(state=DISABLED)
        self.stats_button.config(state=DISABLED)

        # Load first question
        self.new_question()

    def new_question(self):
        """
        Sets up a fresh question. Clears hints, resets buttons,
        loads club name and 4 shuffled nickname options.
        """
        self.hints_used = 0
        self.hint1_used = False
        self.hint2_used = False

        # Reset hint display to default prompt for new question
        self.hint_label.config(text="Use the hints below if you're stuck! 💡")
        self.results_label.config(text="", bg=self.game_frame.cget("bg"))
        self.next_button.config(state=DISABLED)
        self.hint1_button.config(state=NORMAL, text="Hint 1")
        self.hint2_button.config(state=NORMAL, text="Hint 2")

        for btn in self.answer_buttons_ref:
            btn.config(state=NORMAL, bg="#FFFFFF")

        # Get current question data
        current = self.question_list[self.question_number]
        self.current_club = current[0]
        self.current_answer = current[1]
        self.current_hint_team = current[2]
        self.current_hint_nick = current[3]

        self.heading_label.config(
            text="Question {} of {}".format(self.question_number + 1, self.total_questions))
        self.club_label.config(text=self.current_club)

        # Build 4 options: 1 correct + 3 random wrong
        wrong_options = [q[1] for q in self.all_questions if q[1] != self.current_answer]
        wrong_choices = random.sample(wrong_options, 3)
        options = wrong_choices + [self.current_answer]
        random.shuffle(options)
        self.current_options = options

        for i, btn in enumerate(self.answer_buttons_ref):
            btn.config(text=options[i])

    def show_hint_1(self):
        """
        Reveals Hint 1: a clue about the football club's location / history.
        Costs 1 point. Button is then disabled so it can't be used twice.
        If Hint 2 was already used, appends rather than replacing it.
        """
        if not self.hint1_used:
            self.hint1_used = True
            self.hints_used += 1
            self.hint1_button.config(state=DISABLED, text="Hint 1 ✓")
            current_text = self.hint_label.cget("text")
            # If Hint 2 is already showing, prepend Hint 1 above it
            if "Nickname Hint" in current_text:
                self.hint_label.config(
                    text="💡 Club Hint: {}\n{}".format(
                        self.current_hint_team, current_text))
            else:
                self.hint_label.config(
                    text="💡 Club Hint: {}".format(self.current_hint_team))

    def show_hint_2(self):
        """
        Reveals Hint 2: a clue about the meaning of the nickname.
        Costs 1 point. Button is then disabled so it can't be used twice.
        """
        if not self.hint2_used:
            self.hint2_used = True
            self.hints_used += 1
            self.hint2_button.config(state=DISABLED, text="Hint 2 ✓")
            # Append to existing hint text if Hint 1 was also used
            current_text = self.hint_label.cget("text")
            # Only append if Hint 1 is already showing (not the default prompt)
            if "Club Hint" in current_text:
                self.hint_label.config(
                    text="{}\n🔍 Nickname Hint: {}".format(
                        current_text, self.current_hint_nick))
            else:
                self.hint_label.config(
                    text="🔍 Nickname Hint: {}".format(self.current_hint_nick))

    def check_answer(self, button_index):
        """
        Called when an answer button is clicked.
        Checks if correct, calculates score based on hints used, shows result.
        """
        chosen = self.current_options[button_index]

        # Disable all answer and hint buttons after selection
        for btn in self.answer_buttons_ref:
            btn.config(state=DISABLED)
        self.hint1_button.config(state=DISABLED)
        self.hint2_button.config(state=DISABLED)

        if chosen == self.current_answer:
            # 3 points minus 1 per hint used
            points = 3 - self.hints_used
            self.score += points
            self.answer_buttons_ref[button_index].config(bg="#D5E8D4")
            self.results_label.config(
                text="✅ Correct! {} was right. +{} point/s".format(chosen, points),
                bg="#D5E8D4")
        else:
            # Penalty if hints were used
            if self.hints_used > 0:
                self.score -= 1
                penalty_text = " -1 point penalty for using hints."
            else:
                penalty_text = ""
            self.answer_buttons_ref[button_index].config(bg="#F4CCCC")
            self.results_label.config(
                text="❌ Wrong! The answer was {}.{}".format(
                    self.current_answer, penalty_text),
                bg="#F4CCCC")

        self.score_label.config(text="Score: {}".format(self.score))
        self.next_button.config(state=NORMAL)
        self.stats_button.config(state=NORMAL)

    def next_question(self):
        """
        Moves to next question, or shows game over if all questions done.
        """
        self.question_number += 1

        if self.question_number >= self.total_questions:
            self.heading_label.config(text="Game Over!")
            self.results_label.config(
                text="Quiz complete! Final score: {} / {}".format(
                    self.score, self.total_questions * 3),
                bg="#FFF2CC")
            self.next_button.config(state=DISABLED, text="Game Over")
            for btn in self.answer_buttons_ref:
                btn.config(state=DISABLED, text="")
            self.hint1_button.config(state=DISABLED)
            self.hint2_button.config(state=DISABLED)
            self.club_label.config(text="")
            self.hint_label.config(text="")
        else:
            self.new_question()

    def close_play(self):
        """
        Closes play window and returns to start screen.
        """
        root.deiconify()
        self.play_box.destroy()


# main routine
if __name__ == "__main__":
    root = Tk()
    root.title("Football Nickname Quiz")
    StartQuiz()
    root.mainloop()