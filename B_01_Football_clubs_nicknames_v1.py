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


class StartGame:
    """
    Initial Game interface (asks users how many questions they
    would like to answer in the football nickname quiz).
    First full assembled version — all components integrated.
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
        Loads questions from Excel and launches Play class if valid.
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
                self.num_questions_entry.delete(0, END)
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
    Full assembled version: questions, scoring, hints 1 & 2,
    stats button, end game, and play again functionality.
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
        self.hint1_used = False
        self.hint2_used = False
        self.current_answer = ""
        self.answer_buttons_ref = []

        # Running stats lists
        self.all_scores_list = []
        self.all_hints_list = []
        self.all_correct_list = []
        self.questions_correct = IntVar()
        self.questions_correct.set(0)

        # Shuffle and trim to requested number
        self.question_list = random.sample(all_questions, how_many)
        self.all_questions = all_questions  # Keep full pool for wrong answer options

        body_font = ("Arial", 12)

        # Labels: [text | font | bg | row]
        play_labels_list = [
            ["Question 1 of {}".format(how_many), ("Arial", 16, "bold"), None, 0],
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

        # Club name display
        self.club_label = Label(self.game_frame, text="",
                                font=("Arial", 14, "bold"),
                                bg="#FFFFFF", relief="solid", width=25)
        self.club_label.grid(row=3, pady=10, padx=10)

        # Hint display label — shows prompt before any hint is used
        self.hint_label = Label(self.game_frame, text="Use the hints below if you're stuck! 💡",
                                font=body_font, bg="#FFF2CC",
                                wraplength=300, justify="left")
        self.hint_label.grid(row=4, pady=5, padx=10)

        # 2x2 answer buttons
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
            [self.hints_stats_frame, "Stats", "#333333", self.to_stats, 10, 0, 2],
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
        self.end_game_button = control_ref_list[4]

        # Disable next and stats at start
        self.next_button.config(state=DISABLED)
        self.stats_button.config(state=DISABLED)

        # Load first question
        self.new_question()

    def new_question(self):
        """
        Sets up a fresh question — loads club name, builds 4 answer options,
        resets all buttons and hint display.
        """
        self.hints_used = 0
        self.hint1_used = False
        self.hint2_used = False

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
        Reveals Hint 1: clue about the football club.
        Costs 1 potential point. Button disabled after use.
        """
        if not self.hint1_used:
            self.hint1_used = True
            self.hints_used += 1
            self.hint1_button.config(state=DISABLED, text="Hint 1 ✓")
            self.hint_label.config(
                text="💡 Club Hint: {}".format(self.current_hint_team))

    def show_hint_2(self):
        """
        Reveals Hint 2: clue about the nickname meaning.
        Costs 1 potential point. Button disabled after use.
        Appends to Hint 1 text if both hints are used.
        """
        if not self.hint2_used:
            self.hint2_used = True
            self.hints_used += 1
            self.hint2_button.config(state=DISABLED, text="Hint 2 ✓")
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
        Calculates score based on hints used, records result for stats.
        """
        chosen = self.current_options[button_index]

        for btn in self.answer_buttons_ref:
            btn.config(state=DISABLED)
        self.hint1_button.config(state=DISABLED)
        self.hint2_button.config(state=DISABLED)

        if chosen == self.current_answer:
            points = 3 - self.hints_used
            self.score += points
            self.all_scores_list.append(points)
            self.all_correct_list.append(True)
            correct_so_far = self.questions_correct.get()
            self.questions_correct.set(correct_so_far + 1)
            self.answer_buttons_ref[button_index].config(bg="#D5E8D4")
            self.results_label.config(
                text="✅ Correct! {} was right. +{} point/s".format(chosen, points),
                bg="#D5E8D4")
        else:
            if self.hints_used > 0:
                self.score -= 1
                self.all_scores_list.append(-1)
                penalty_text = " -1 point penalty for using hints."
            else:
                self.all_scores_list.append(0)
                penalty_text = ""
            self.all_correct_list.append(False)
            self.answer_buttons_ref[button_index].config(bg="#F4CCCC")
            self.results_label.config(
                text="❌ Wrong! The answer was {}.{}".format(
                    self.current_answer, penalty_text),
                bg="#F4CCCC")

        self.all_hints_list.append(self.hints_used)
        self.score_label.config(text="Score: {}".format(self.score))
        self.next_button.config(state=NORMAL)
        self.stats_button.config(state=NORMAL)

    def next_question(self):
        """
        Advances to next question. At end of game, shows final score,
        disables all controls and changes End Game to Play Again.
        """
        self.question_number += 1

        if self.question_number >= self.total_questions:
            # Game over — show summary
            questions_correct = self.questions_correct.get()
            self.heading_label.config(text="Game Over!")
            self.results_label.config(
                text="Quiz complete! Score: {} / {}   Correct: {} / {}".format(
                    self.score, self.total_questions * 3,
                    questions_correct, self.total_questions),
                bg="#FFF2CC")
            self.next_button.config(state=DISABLED, text="Game Over")
            for btn in self.answer_buttons_ref:
                btn.config(state=DISABLED, text="")
            self.hint1_button.config(state=DISABLED)
            self.hint2_button.config(state=DISABLED)
            self.club_label.config(text="")
            self.hint_label.config(text="")
            # Change End Game to Play Again
            self.end_game_button.config(text="Play Again", bg="#006600")
            self.stats_button.config(bg="#990000")
        else:
            self.new_question()

    def to_stats(self):
        """
        Bundles all stats data and passes to Stats class.
        """
        questions_correct = self.questions_correct.get()
        stats_bundle = [questions_correct, self.all_scores_list,
                        self.all_hints_list, self.all_correct_list]
        Stats(self, stats_bundle)

    def close_play(self):
        """
        Closes play window and returns to start screen (or Play Again).
        Clears entry box so user can start fresh.
        """
        root.deiconify()
        self.play_box.destroy()


class Stats:
    """
    Displays statistics popup for the Football Nickname Quiz.
    Shows: correct answers, total score vs max possible, hints used,
    best question score, and average score per question.
    Disables hint and end game buttons while open to prevent crashes.
    """

    def __init__(self, partner, all_stats_info):

        # Disable buttons to prevent navigating away while stats is open
        partner.hint1_button.config(state=DISABLED)
        partner.hint2_button.config(state=DISABLED)
        partner.end_game_button.config(state=DISABLED)
        partner.stats_button.config(state=DISABLED)

        # Extract data from bundle
        questions_correct = all_stats_info[0]
        all_scores = all_stats_info[1]
        all_hints = all_stats_info[2]

        sorted_scores = sorted(all_scores)

        background = "#DAE8FC"

        self.stats_box = Toplevel()
        self.stats_box.title("Statistics")

        # If users press cross at top, close stats and re-enable buttons
        self.stats_box.protocol('WM_DELETE_WINDOW',
                                partial(self.close_stats, partner))

        self.stats_frame = Frame(self.stats_box, width=350)
        self.stats_frame.grid()

        # --- Calculate stats ---
        questions_played = len(all_scores)
        total_score = sum(all_scores)
        max_possible = questions_played * 3
        best_score = sorted_scores[-1]
        average_score = total_score / questions_played
        total_hints = sum(all_hints)
        success_rate = questions_correct / questions_played * 100

        # --- Build label strings ---
        success_string = (f"Correct Answers: {questions_correct} / {questions_played}"
                          f" ({success_rate:.0f}%)")
        total_score_string = f"Total Score: {total_score} / {max_possible}"
        hints_string = f"Total Hints Used: {total_hints}"
        best_score_string = f"Best Score (single question): {best_score}"
        average_score_string = f"Average Score Per Question: {average_score:.1f}"

        # Comment based on performance
        comment_alignment = "W"

        if total_score == max_possible:
            comment_string = "🏆 Amazing! Perfect score — no hints needed!"
            comment_colour = "#D5E8D4"
        elif questions_correct == 0:
            comment_string = "💡 No correct answers yet — try using the hints!"
            comment_colour = "#F8CECC"
            best_score_string = "Best Score: n/a"
        else:
            comment_string = ""
            comment_colour = "#F0F0F0"
            comment_alignment = ""

        heading_font = ("Arial", 16, "bold")
        normal_font = ("Arial", 14)
        comment_font = ("Arial", 13)

        # Label list: [text | font | sticky]
        all_stats_strings = [
            ["Statistics", heading_font, ""],
            [success_string, normal_font, "W"],
            [total_score_string, normal_font, "W"],
            [hints_string, normal_font, "W"],
            [comment_string, comment_font, comment_alignment],
            ["\nQuestion Stats", heading_font, ""],
            [best_score_string, normal_font, "W"],
            [average_score_string, normal_font, "W"]
        ]

        stats_label_ref_list = []
        for count, item in enumerate(all_stats_strings):
            self.stats_label = Label(self.stats_frame, text=item[0],
                                     font=item[1], wraplength=300,
                                     anchor="w", justify="left",
                                     padx=30, pady=5)
            self.stats_label.grid(row=count, sticky=item[2], padx=10)
            stats_label_ref_list.append(self.stats_label)

        # Colour the comment label based on performance
        stats_comment_label = stats_label_ref_list[4]
        stats_comment_label.config(bg=comment_colour)

        self.dismiss_button = Button(self.stats_frame,
                                     font=("Arial", 16, "bold"),
                                     text="Dismiss", bg="#333333",
                                     fg="#FFFFFF", width=20,
                                     command=partial(self.close_stats, partner))
        self.dismiss_button.grid(row=8, padx=10, pady=10)

    def close_stats(self, partner):
        """
        Closes stats window and re-enables buttons in Play.
        """
        partner.hint1_button.config(state=NORMAL)
        partner.hint2_button.config(state=NORMAL)
        partner.end_game_button.config(state=NORMAL)
        partner.stats_button.config(state=NORMAL)
        self.stats_box.destroy()


# main routine
if __name__ == "__main__":
    root = Tk()
    root.title("Football Nickname Quiz")
    StartGame()
    root.mainloop()