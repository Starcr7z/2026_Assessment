from tkinter import *
from tkinter import messagebox
from functools import partial
import pandas as pd
import random
import datetime


def get_questions():
    """
    Reads the raw football data from our Excel file.
    Returns a clean list of lists: [club, nickname, hint_team, hint_nick]
    """
    try:
        df = pd.read_excel("football.xlsx")
        # Optimization: We convert the exact columns we need straight into a list of lists.
        # This bypasses pd.iterrows(), which is painfully slow on larger datasets.
        return df[["Football Team", "Football Nickname", "Hint for Football Team", "Hint for Nickname"]].astype(
            str).values.tolist()
    except FileNotFoundError:
        # Don't let the script hard-crash if someone forgot to move the spreadsheet over.
        messagebox.showerror("Error", "Could not find football.xlsx.\n"
                                      "Please make sure it is in the same folder as this program.")
        return []


class Startquiz:
    """
    The landing screen. Handles initial user validation and acts as the gatekeeper
    before loading up the actual quiz interface.
    """

    def __init__(self):
        self.start_frame = Frame(padx=10, pady=10)
        self.start_frame.grid()

        # The rules explanation string that lays out the scoring weights
        intro_string = ("Each question shows a football club and 4 nickname options. "
                        "Pick the correct answer to score points. "
                        "You can use up to 2 hints per question — each hint "
                        "costs 1 point from your potential score.\n\n"
                        "Correct, no hints used = 3 points\n"
                        "Correct, 1 hint used = 2 points\n"
                        "Correct, 2 hints used = 1 point\n"
                        "Wrong answer (no hints used) = 0 points\n"
                        "Wrong answer (any hints used) = -1 points")

        # Keeping UI metadata clean by bundling text, formatting, and colors together
        start_labels_list = [
            ["Football Nickname Quiz ⚽", ("Arial", 16, "bold"), None],
            [intro_string, ("Arial", 12), None],
            ["How many questions do you want to answer?", ("Arial", 12, "bold"), "#009900"]
        ]

        # Dynamically loop and build the labels to save ourselves repetitive Tkinter layout lines
        start_label_ref = []
        for count, item in enumerate(start_labels_list):
            make_label = Label(self.start_frame, text=item[0], font=item[1], fg=item[2],
                               wraplength=350, justify="left", pady=10, padx=20)
            make_label.grid(row=count)
            start_label_ref.append(make_label)

        # Grabbing a direct reference to the last label so we can turn it red if an error happens
        self.choose_label = start_label_ref[2]

        # Horizontal sub-frame keeping the input box right next to the trigger button
        self.entry_area_frame = Frame(self.start_frame)
        self.entry_area_frame.grid(row=3)

        self.num_questions_entry = Entry(self.entry_area_frame, font=("Arial", 20, "bold"), width=10)
        self.num_questions_entry.grid(row=0, column=0, padx=10, pady=10)

        self.play_Button = Button(self.entry_area_frame, font=("Arial", 16, "bold"),
                                  fg="#FFFFFF", bg="#0057D8", text="Play", width=10,
                                  command=self.check_questions)
        self.play_Button.grid(row=0, column=1)

        self.exit_Button = Button(self.start_frame, font=("Arial", 12, "bold"),
                                  fg="#FFFFFF", bg="#990000", text="Exit", width=10,
                                  command=self.start_frame.quit)
        self.exit_Button.grid(row=4, pady=10)

    def check_questions(self):
        """
        Validates the string input from the user entry box.
        Ensures it is a clean integer within limits and checks database depth.
        """
        max_questions = 100
        questions_wanted = self.num_questions_entry.get()

        # Flashing the UI label back to green/default text in case they are retrying after an error
        self.choose_label.config(fg="#009900", font=("Arial", 12, "bold"),
                                 text="How many questions do you want to answer?")
        self.num_questions_entry.config(bg="#FFFFFF")

        error = f"Oops - Please choose a whole number between 1 and {max_questions}."

        try:
            questions_wanted = int(questions_wanted)
            if 1 <= questions_wanted <= max_questions:
                all_questions = get_questions()

                # Safety break: stop execution if data file returned empty to avoid empty sample crashes
                if not all_questions:
                    return

                # Prevent users from requesting more questions than what actually exists in the Excel sheet
                if len(all_questions) < questions_wanted:
                    self.choose_label.config(
                        text=f"Not enough questions in data file. Choose {len(all_questions)} or fewer.",
                        fg="#990000", font=("Arial", 10, "bold"))
                    self.num_questions_entry.config(bg="#F4CCCC")
                    self.num_questions_entry.delete(0, END)
                    return

                # Inputs look valid! Clear out the input field, spin up the game, and minimize the home screen
                self.num_questions_entry.delete(0, END)
                Play(questions_wanted, all_questions)
                root.withdraw()
            else:
                self.choose_label.config(text=error, fg="#990000", font=("Arial", 10, "bold"))
                self.num_questions_entry.config(bg="#F4CCCC")
        except ValueError:
            # Handles text characters, symbols, or completely empty submissions gracefully
            self.choose_label.config(text=error, fg="#990000", font=("Arial", 10, "bold"))
            self.num_questions_entry.config(bg="#F4CCCC")


class Play:
    """
    The engine room of the quiz. Spins up a secondary window, controls the gameplay logic,
    tracks the scoring matrices, and outputs history objects for downstream statistics.
    """

    def __init__(self, how_many, all_questions):
        # Using Toplevel to keep it cleanly separate from our main hidden window
        self.play_box = Toplevel()
        self.play_box.title("Football Nickname Quiz")

        # intercepting the top right 'X' button to kill the whole loop cleanly
        self.play_box.protocol('WM_DELETE_WINDOW', root.destroy)

        self.quiz_frame = Frame(self.play_box)
        self.quiz_frame.grid(padx=10, pady=10)

        # Stateful metrics tracked dynamically throughout the user session
        self.total_questions = how_many
        self.question_number = 0
        self.score = 0
        self.hints_used = 0
        self.hint1_used = False
        self.hint2_used = False
        self.current_answer = ""
        self.answer_Buttons_ref = []

        # Structural lists capturing historical logs for stats computation & export files
        self.all_scores_list = []
        self.all_hints_list = []
        self.all_correct_list = []
        self.history_list = []
        self.questions_correct = IntVar(value=0)

        # Pull a perfectly randomized list slice containing the absolute count requested
        self.question_list = random.sample(all_questions, how_many)
        self.all_questions = all_questions

        body_font = ("Arial", 12)
        play_labels_list = [
            [f"Question 1 of {how_many}", ("Arial", 16, "bold"), None, 0],
            ["Score: 0", body_font, "#FFF2CC", 1],
            ["Guess the nickname of the football club below. Good luck. ⚽", body_font, "#D5E8D4", 2],
            ["", body_font, None, 5]
        ]

        play_labels_ref = []
        for item in play_labels_list:
            make_label = Label(self.quiz_frame, text=item[0], font=item[1],
                               bg=item[2], wraplength=300, justify="left", padx=10)
            make_label.grid(row=item[3], pady=10, padx=10)
            play_labels_ref.append(make_label)

        # Unpacking variable references directly out of our UI build loop array
        self.heading_label, self.score_label, self.instruction_label, self.results_label = play_labels_ref

        # Main club prompt widget box
        self.club_label = Label(self.quiz_frame, text="", font=("Arial", 14, "bold"),
                                bg="#FFFFFF", relief="solid", width=25)
        self.club_label.grid(row=3, pady=10, padx=10)

        # Hint output window layer
        self.hint_label = Label(self.quiz_frame, text="Use the hints below if you're stuck! 💡",
                                font=body_font, bg="#FFF2CC", wraplength=300, justify="left")
        self.hint_label.grid(row=4, pady=5, padx=10)

        self.answer_frame = Frame(self.quiz_frame)
        self.answer_frame.grid(row=6)

        # Generate a neat 2x2 grid system for the four answer choice buttons
        for item in range(4):
            btn = Button(self.answer_frame, font=("Arial", 12), text="", width=15, bg="#FFFFFF",
                         command=partial(self.check_answer, item))
            btn.grid(row=item // 2, column=item % 2, padx=5, pady=5)
            self.answer_Buttons_ref.append(btn)

        self.hints_stats_frame = Frame(self.quiz_frame)
        self.hints_stats_frame.grid(row=8)

        # Central configuration map mapping layouts, target functions, colors, and row/column spots
        control_Button_list = [
            [self.quiz_frame, "Next Question", "#0057D8", self.next_question, 21, 7, None],
            [self.hints_stats_frame, "Club Hint", "#FF8000", self.show_hint_1, 15, 0, 0],
            [self.hints_stats_frame, "Nickname Hint", "#FF8000", self.show_hint_2, 15, 0, 1],
            [self.hints_stats_frame, "Stats", "#333333", self.to_stats, 12, 0, 2],
            [self.quiz_frame, "End quiz", "#990000", self.end_quiz_early, 21, 9, None]
        ]

        control_ref_list = []
        for item in control_Button_list:
            make_control_Button = Button(item[0], text=item[1], bg=item[2], fg="#FFFFFF",
                                         command=item[3], font=("Arial", 10, "bold"), width=item[4])
            make_control_Button.grid(row=item[5], column=item[6], padx=5, pady=5)
            control_ref_list.append(make_control_Button)

        self.next_Button, self.hint1_Button, self.hint2_Button, self.stats_Button, self.end_quiz_Button = control_ref_list

        # Lock down navigation controls out of the gate until an answer actually registers
        self.next_Button.config(state=DISABLED)
        self.stats_Button.config(state=DISABLED)

        # Bootstrap stage one
        self.new_question()

    def new_question(self):
        """
        Resets all layout states and sets up a brand new randomized question block.
        """
        self.hints_used = 0
        self.hint1_used = False
        self.hint2_used = False

        self.hint_label.config(text="Use the hints below if you're stuck! 💡")
        self.results_label.config(text="", bg=self.quiz_frame.cget("bg"))
        self.next_Button.config(state=DISABLED)
        self.hint1_Button.config(state=NORMAL, text="Club Hint")
        self.hint2_Button.config(state=NORMAL, text="Nickname Hint")

        # Bring button appearances completely back to clean baseline defaults
        for item in self.answer_Buttons_ref:
            item.config(state=NORMAL, bg="#FFFFFF")

        # Destructure the raw data list slice for the current iteration
        current = self.question_list[self.question_number]
        self.current_club, self.current_answer, self.current_hint_team, self.current_hint_nick = current

        self.heading_label.config(text=f"Question {self.question_number + 1} of {self.total_questions}")
        self.club_label.config(text=self.current_club)

        # Optimization Fix: Convert logic array to a set() wrapper first. This kills duplicate nickname
        # strings if two data files share a name, shielding random.sample from a duplicate options crash.
        wrong_options = list(set(q[1] for q in self.all_questions if q[1] != self.current_answer))
        wrong_choices = random.sample(wrong_options, min(3, len(wrong_options)))

        # Stitch wrong options alongside the true answer and scramble them
        options = wrong_choices + [self.current_answer]
        random.shuffle(options)
        self.current_options = options

        # Push calculated option strings into button texts
        for count, item in enumerate(self.answer_Buttons_ref):
            item.config(text=options[count])

    def show_hint_1(self):
        """Handles state mutation and text adjustments when the Club Hint is revealed."""
        if not self.hint1_used:
            self.hint1_used = True
            self.hints_used += 1
            self.hint1_Button.config(state=DISABLED, text="Club Hint ✓")
            self.update_hint_label()

    def show_hint_2(self):
        """Handles state mutation and text adjustments when the Nickname Hint is revealed."""
        if not self.hint2_used:
            self.hint2_used = True
            self.hints_used += 1
            self.hint2_Button.config(state=DISABLED, text="Nickname Hint ✓")
            self.update_hint_label()

    def update_hint_label(self):
        """Helper to cleanly format structural layouts depending on combination of hints active."""
        if self.hint1_used and self.hint2_used:
            self.hint_label.config(
                text=f"💡 Club Hint: {self.current_hint_team}\n🔍 Nickname Hint: {self.current_hint_nick}")
        elif self.hint1_used:
            self.hint_label.config(text=f"💡 Club Hint: {self.current_hint_team}")
        else:
            self.hint_label.config(text=f"🔍 Nickname Hint: {self.current_hint_nick}")

    def check_answer(self, Button_index):
        """
        Evaluates accuracy, locks interactivity to halt exploit double-clicking,
        processes scoring weights/penalties, and appends the log bundle.
        """
        chosen = self.current_options[Button_index]

        # Freeze input options instantly so they cannot click multiple answers on a single question
        for item in self.answer_Buttons_ref:
            item.config(state=DISABLED)
        self.hint1_Button.config(state=DISABLED)
        self.hint2_Button.config(state=DISABLED)

        # Find where the winning option settled during the shuffle
        correct_index = self.current_options.index(self.current_answer)

        if chosen == self.current_answer:
            # Score scaling logic based on hints used (3 points max, down to 1 point minimum)
            points = 3 - self.hints_used
            self.score += points
            self.all_scores_list.append(points)
            self.all_correct_list.append(True)
            self.questions_correct.set(self.questions_correct.get() + 1)
            self.answer_Buttons_ref[Button_index].config(bg="#D5E8D4")  # Turn chosen green
            self.results_label.config(text=f"✅ Correct! {chosen} was right. +{points} point/s", bg="#D5E8D4")
            result_word = "Correct"
        else:
            # Apply negative penalty logic if they were completely wrong despite burning hints
            if self.hints_used > 0:
                self.score -= 1
                self.all_scores_list.append(-1)
                penalty_text = " -1 point penalty for using hints."
            else:
                self.all_scores_list.append(0)
                penalty_text = ""
            self.all_correct_list.append(False)
            self.answer_Buttons_ref[Button_index].config(bg="#F4CCCC")  # Flash incorrect choice Red
            self.answer_Buttons_ref[correct_index].config(bg="#D5E8D4")  # Guide eye to correct answer in Green
            self.results_label.config(text=f"❌ Wrong! The answer was {self.current_answer}.{penalty_text}",
                                      bg="#F4CCCC")
            result_word = "Wrong"

        # Pack detailed metadata map for down-stream logging exports
        self.history_list.append({
            "question": self.question_number + 1,
            "club": self.current_club,
            "correct_answer": self.current_answer,
            "chosen": chosen,
            "result": result_word,
            "hints_used": self.hints_used,
            "points": self.all_scores_list[-1]
        })

        self.all_hints_list.append(self.hints_used)
        self.score_label.config(text=f"Score: {self.score}")

        # Check loop condition: if out of questions, jump straight to checkout frame
        if self.question_number + 1 == self.total_questions:
            self.quiz_over(early=False)
        else:
            self.next_Button.config(state=NORMAL)
            self.stats_Button.config(state=NORMAL)

    def next_question(self):
        self.question_number += 1
        self.new_question()

    def end_quiz_early(self):
        # Double-check the button is currently visible and active before forcing termination
        if self.next_Button.winfo_exists() and self.next_Button.winfo_ismapped():
            self.quiz_over(early=True)

    def quiz_over(self, early=False):
        """Clears gameplay screen space out entirely and swaps in the master scoreboard frame."""
        self.answer_frame.grid_remove()
        self.hints_stats_frame.grid_remove()
        self.next_Button.grid_remove()
        self.end_quiz_Button.grid_remove()
        self.results_label.grid_remove()
        self.score_label.grid_remove()
        self.instruction_label.grid_remove()
        self.club_label.grid_remove()
        self.hint_label.grid_remove()

        answered_count = len(self.all_scores_list)

        # Container frame holding layout objects in exact window location of old answer grids
        results_frame = Frame(self.quiz_frame, bg="#f0f0f0", bd=2, relief="groove")
        results_frame.grid(row=6, column=0, pady=10, padx=10)

        # Fallback view layout logic if they literally quit the application immediately
        if answered_count == 0:
            Label(results_frame, text="No questions were answered.", font=("Arial", 12), bg="#f0f0f0").grid(row=0,
                                                                                                            pady=10)
            btn_frame = Frame(results_frame, bg="#f0f0f0")
            btn_frame.grid(row=1, pady=10)
            Button(btn_frame, text="Play Again", bg="#006600", fg="#FFFFFF", font=("Arial", 11, "bold"), width=12,
                   command=self.play_again).grid(row=0, column=0, padx=5)
            Button(btn_frame, text="Exit", bg="#990000", fg="#FFFFFF", font=("Arial", 11, "bold"), width=12,
                   command=self.close_play).grid(row=0, column=1, padx=5)
            self.heading_label.config(text="Quiz Ended Early")
            return

        # Statistical calculations
        correct_answers = self.questions_correct.get()
        total_possible_score = answered_count * 3
        accuracy_percent = (correct_answers / answered_count) * 100
        incorrect_answers = answered_count - correct_answers
        total_hints_used = sum(self.all_hints_list)

        # Render out the scoreboard
        Label(results_frame, text="RESULTS", font=("Arial", 14, "bold"), bg="#f0f0f0").grid(row=0, column=0,
                                                                                            columnspan=2, pady=8)
        Label(results_frame, text=f"Final Score: {self.score} / {total_possible_score}", font=("Arial", 12),
              bg="#f0f0f0").grid(row=1, column=0, sticky="w", padx=10, pady=4)
        Label(results_frame, text=f"Accuracy: {accuracy_percent:.1f}%", font=("Arial", 12), bg="#f0f0f0").grid(row=2,
                                                                                                               column=0,
                                                                                                               sticky="w",
                                                                                                               padx=10,
                                                                                                               pady=4)
        Label(results_frame, text=f"Correct Answers: {correct_answers}", font=("Arial", 12), bg="#f0f0f0").grid(row=3,
                                                                                                                column=0,
                                                                                                                sticky="w",
                                                                                                                padx=10,
                                                                                                                pady=4)
        Label(results_frame, text=f"Incorrect Answers: {incorrect_answers}", font=("Arial", 12), bg="#f0f0f0").grid(
            row=4, column=0, sticky="w", padx=10, pady=4)
        Label(results_frame, text=f"Total Hints Used: {total_hints_used}", font=("Arial", 12), bg="#f0f0f0").grid(row=5,
                                                                                                                  column=0,
                                                                                                                  sticky="w",
                                                                                                                  padx=10,
                                                                                                                  pady=4)

        btn_frame = Frame(results_frame, bg="#f0f0f0")
        btn_frame.grid(row=6, column=0, columnspan=2, pady=10)

        # Re-attached fixed and operational navigation routing commands
        Button(btn_frame, text="Play Again", bg="#006600", fg="#FFFFFF", font=("Arial", 11, "bold"), width=12,
               command=self.play_again).grid(row=0, column=0, padx=5)
        Button(btn_frame, text="Statistics", bg="#333333", fg="#FFFFFF", font=("Arial", 11, "bold"), width=12,
               command=self.to_stats).grid(row=0, column=1, padx=5)

        self.heading_label.config(text="Quiz Ended Early" if early else "Quiz Complete!")

    def play_again(self):
        """Unhides landing root context screen and destroys current pop window lifecycle."""
        root.deiconify()
        self.play_box.destroy()

    def to_stats(self):
        """Gathers runtime states and routes them into standard analytics class popup."""
        stats_bundle = [self.questions_correct.get(), self.all_scores_list, self.all_hints_list, self.all_correct_list]
        Stats(self, stats_bundle)

    def close_play(self):
        """Full systematic exit routine returning program control state to home loop."""
        root.deiconify()
        self.play_box.destroy()


class Stats:
    """
    Independent popup frame managing session analytical outputs, contextual logic evaluation,
    and external log generation methods.
    """

    def __init__(self, partner, all_stats_info):
        # Freeze background buttons so users can't click game states while this dialog overlay is open
        partner.hint1_Button.config(state=DISABLED)
        partner.hint2_Button.config(state=DISABLED)
        if hasattr(partner, 'end_quiz_Button') and partner.end_quiz_Button.winfo_exists():
            partner.end_quiz_Button.config(state=DISABLED)
        partner.stats_Button.config(state=DISABLED)

        # Destructure active tuple stats block variables
        questions_correct, all_scores, all_hints, _ = all_stats_info
        self.partner = partner
        sorted_scores = sorted(all_scores) if all_scores else [0]

        self.stats_box = Toplevel()
        self.stats_box.title("Statistics")

        # Guarantee window close handles system cleanup callbacks cleanly
        self.stats_box.protocol('WM_DELETE_WINDOW', partial(self.close_stats, partner))

        self.stats_frame = Frame(self.stats_box, width=350)
        self.stats_frame.grid()

        # Analytics crunch processing logic
        questions_played = len(all_scores)
        total_score = sum(all_scores)
        max_possible = questions_played * 3
        best_score = sorted_scores[-1] if sorted_scores else 0
        average_score = total_score / questions_played if questions_played > 0 else 0
        total_hints = sum(all_hints)
        success_rate = (questions_correct / questions_played * 100) if questions_played > 0 else 0

        # Formatted display text assignments
        success_string = f"✅ Correct Answers: {questions_correct} / {questions_played}  ({success_rate:.1f}%)"
        total_score_string = f"🏆 Total Score: {total_score} / {max_possible}"
        hints_string = f"💡 Total Hints Used: {total_hints}"
        best_score_string = f"⭐ Best Score (single question): {best_score}"
        average_score_string = f"📊 Average Score Per Question: {average_score:.1f}"

        # Contextual logic block sorting user scores to provide colored feedback comments
        if success_rate >= 90:
            comment_string, comment_colour = "🏆 Amazing! Perfect performance!", "#D5E8D4"
        elif success_rate >= 70:
            comment_string, comment_colour = "🎉 Great job! Really solid quiz!", "#D5E8D4"
        elif success_rate >= 50:
            comment_string, comment_colour = "👍 Good effort! Keep practicing!", "#FFF2CC"
        elif questions_played > 0 and questions_correct == 0:
            comment_string, comment_colour = "💡 No correct answers yet — try using the hints!", "#F8CECC"
            best_score_string = "⭐ Best Score: n/a"
        else:
            comment_string, comment_colour = "📚 Keep going! You'll improve with practice!", "#FFF2CC"

        all_stats_strings = [
            ["📊 QUIZ STATISTICS", ("Arial", 14, "bold"), "w"],
            [success_string, ("Arial", 12), "w"],
            [total_score_string, ("Arial", 12), "w"],
            [hints_string, ("Arial", 12), "w"],
            [comment_string, ("Arial", 11), "w"],
            ["", ("Arial", 12), "w"],
            ["📈 DETAILED BREAKDOWN", ("Arial", 14, "bold"), "w"],
            [best_score_string, ("Arial", 12), "w"],
            [average_score_string, ("Arial", 12), "w"]
        ]

        stats_label_ref_list = []
        for count, item in enumerate(all_stats_strings):
            lbl = Label(self.stats_frame, text=item[0], font=item[1], wraplength=300, anchor="w", justify="left",
                        padx=30, pady=5)
            lbl.grid(row=count, sticky=item[2], padx=10)
            stats_label_ref_list.append(lbl)

        # Apply specific performance accent background color to the feedback text label string
        stats_label_ref_list[4].config(bg=comment_colour)

        self.export_label = Label(self.stats_frame, text="", font=("Arial", 10), fg="#555555", wraplength=300)
        self.export_label.grid(row=9, padx=10, pady=2)

        Button_frame = Frame(self.stats_frame)
        Button_frame.grid(row=10, padx=10, pady=10)

        self.export_Button = Button(Button_frame, font=("Arial", 11, "bold"), text="📁 Export Results", bg="#0057D8",
                                    fg="#FFFFFF", width=14, command=partial(self.export_results, partner))
        self.export_Button.grid(row=0, column=0, padx=5)

        self.dismiss_Button = Button(Button_frame, font=("Arial", 11, "bold"), text="✖ Dismiss", bg="#333333",
                                     fg="#FFFFFF", width=14, command=partial(self.close_stats, partner))
        self.dismiss_Button.grid(row=0, column=1, padx=5)

    def export_results(self, partner):
        """Outputs structural text files containing chronological session records, timestamps, and parameters."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"football_quiz_results_{timestamp}.txt"

        try:
            # explicit utf-8 parsing config setup to natively protect emoji formatting in exports
            with open(filename, "w", encoding="utf-8") as file:
                file.write("=" * 50 + "\n     FOOTBALL NICKNAME QUIZ RESULTS\n" + "=" * 50 + "\n")
                file.write(f"Date: {datetime.datetime.now().strftime('%d %B %Y %H:%M')}\n\n")
                file.write("📋 QUESTION HISTORY\n" + "-" * 50 + "\n")

                # Iterate chronologically backwards through log arrays to construct rows
                for entry in partner.history_list:
                    emoji = "✅" if entry["result"] == "Correct" else "❌"
                    file.write(f"{emoji} Q{entry['question']}: {entry['club']}\n"
                               f"   Answer: {entry['correct_answer']} | You chose: {entry['chosen']}\n"
                               f"   Result: {entry['result']} | Hints: {entry['hints_used']} | Points: {entry['points']}\n\n")

                total = sum(partner.all_scores_list)
                max_p = len(partner.all_scores_list) * 3
                correct = partner.questions_correct.get()
                played = len(partner.all_scores_list)
                acc = (correct / played * 100) if played > 0 else 0

                file.write("\n📊 SUMMARY STATISTICS\n" + "-" * 50 + "\n")
                file.write(
                    f"Correct Answers: {correct} / {played} ({acc:.1f}%)\nTotal Score: {total} / {max_p}\nTotal Hints Used: {sum(partner.all_hints_list)}\n" + "=" * 50 + "\n")

            # Let users know the file successfully hit the disc, then lock out the button to stop multiple file dumps
            self.export_label.config(text=f"✅ Saved as: {filename}", fg="#006600")
            self.export_Button.config(state=DISABLED)
        except OSError:
            self.export_label.config(text="❌ Could not save file. Check folder permissions.", fg="#990000")

    def close_stats(self, partner):
        """Restores state metrics to background control frames prior to window cleanup destruction."""
        try:
            partner.hint1_Button.config(state=NORMAL)
            partner.hint2_Button.config(state=NORMAL)
            if hasattr(partner, 'end_quiz_Button') and partner.end_quiz_Button.winfo_exists():
                partner.end_quiz_Button.config(state=NORMAL)
            partner.stats_Button.config(state=NORMAL)
        except Exception:
            pass
        self.stats_box.destroy()


if __name__ == "__main__":
    # Primary setup architecture initiation script execution block
    root = Tk()
    root.title("Football Nickname Quiz")
    Startquiz()
    root.mainloop()