from tkinter import *
from tkinter import messagebox
from functools import partial
import pandas as pd
import random
import datetime


def get_questions():
    """
    Grabs football club data from an Excel file.
    Returns a list of lists: [club, nickname, hint_team, hint_nick]
    Shows an error if the file isn't there.
    """
    try:
        df = pd.read_excel("football.xlsx")
        questions = []
        for _, row in df.iterrows():
            questions.append([
                str(row["Football Team"]),
                str(row["Football Nickname"]),
                str(row["Hint for Football Team"]),
                str(row["Hint for Nickname"])
            ])
        return questions
    except FileNotFoundError:
        messagebox.showerror("Error", "Could not find football.xlsx.\n"
                                      "Please make sure it is in the same folder as this program.")
        return []


class Startquiz:
    """
    First screen that asks how many questions the user wants to answer.
    """

    def __init__(self):
        """
        Sets up the starting frame and widgets.
        """
        self.start_frame = Frame(padx=10, pady=10)
        self.start_frame.grid()

        # Text for the intro label
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

        # List of labels to create (text, font, fg)
        start_labels_list = [
            ["Football Nickname Quiz ⚽", ("Arial", 16, "bold"), None],
            [intro_string, ("Arial", 12), None],
            [choose_string, ("Arial", 12, "bold"), "#009900"]
        ]

        # Make all the labels and save references
        start_label_ref = []
        for count, item in enumerate(start_labels_list):
            make_label = Label(self.start_frame, text=item[0], font=item[1],
                               fg=item[2],
                               wraplength=350, justify="left", pady=10, padx=20)
            make_label.grid(row=count)
            start_label_ref.append(make_label)

        # Save the label that might show error messages
        self.choose_label = start_label_ref[2]

        # Frame to hold entry box and button on the same row
        self.entry_area_frame = Frame(self.start_frame)
        self.entry_area_frame.grid(row=3)

        self.num_questions_entry = Entry(self.entry_area_frame, font=("Arial", 20, "bold"),
                                         width=10)
        self.num_questions_entry.grid(row=0, column=0, padx=10, pady=10)

        # Play button
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
        Checks if the number of questions entered is valid (1 to 100).
        Loads questions from the Excel file.
        """
        max_questions = 100

        questions_wanted = self.num_questions_entry.get()

        # Reset label and entry box in case this is a retry
        self.choose_label.config(fg="#009900", font=("Arial", 12, "bold"),
                                 text="How many questions do you want to answer?")
        self.num_questions_entry.config(bg="#FFFFFF")

        error = "Oops - Please choose a whole number between 1 and {}.".format(max_questions)
        has_errors = "no"

        try:
            questions_wanted = int(questions_wanted)
            if 1 <= questions_wanted <= max_questions:
                all_questions = get_questions()

                # Make sure we have enough questions in the file
                if len(all_questions) < questions_wanted:
                    self.choose_label.config(
                        text="Not enough questions in the data file. "
                             "Please choose {} or fewer.".format(len(all_questions)),
                        fg="#990000", font=("Arial", 10, "bold"))
                    self.num_questions_entry.config(bg="#F4CCCC")
                    self.num_questions_entry.delete(0, END)
                    return

                self.num_questions_entry.delete(0, END)

                # Start the actual quiz
                Play(questions_wanted, all_questions)
                root.withdraw()
            else:
                has_errors = "yes"

        except ValueError:
            has_errors = "yes"

        # Show error if needed
        if has_errors == "yes":
            self.choose_label.config(text=error, fg="#990000",
                                     font=("Arial", 10, "bold"))
            self.num_questions_entry.config(bg="#F4CCCC")
            self.num_questions_entry.delete(0, END)


class Play:
    """
    Main quiz gameplay screen.
    """

    def __init__(self, how_many, all_questions):
        self.play_box = Toplevel()
        self.play_box.title("Football Nickname Quiz")

        # If user closes the window, end everything
        self.play_box.protocol('WM_DELETE_WINDOW', root.destroy)

        self.quiz_frame = Frame(self.play_box)
        self.quiz_frame.grid(padx=10, pady=10)

        # Track game state
        self.total_questions = how_many
        self.question_number = 0
        self.score = 0
        self.hints_used = 0
        self.hint1_used = False
        self.hint2_used = False
        self.current_answer = ""
        self.answer_buttons_ref = []

        # Instance attributes that will be set later
        self.current_club = ""
        self.current_hint_team = ""
        self.current_hint_nick = ""
        self.current_options = []
        self.results_frame = None

        # Store data for stats
        self.all_scores_list = []
        self.all_hints_list = []
        self.all_correct_list = []
        self.history_list = []
        self.questions_correct = IntVar()
        self.questions_correct.set(0)

        # Pick random questions and save them
        self.question_list = random.sample(all_questions, how_many)
        self.all_questions = all_questions

        body_font = ("Arial", 12)

        # Labels for the quiz screen
        play_labels_list = [
            ["Question 1 of {}".format(how_many), ("Arial", 16, "bold"), None, 0],
            ["Score: 0", body_font, "#FFF2CC", 1],
            ["Guess the nickname of the football club below. Good luck. ⚽", body_font, "#D5E8D4", 2],
            ["", body_font, None, 5]
        ]

        play_labels_ref = []
        for item in play_labels_list:
            self.make_label = Label(self.quiz_frame, text=item[0], font=item[1],
                               bg=item[2], wraplength=300, justify="left", padx=10)
            self.make_label.grid(row=item[3], pady=10, padx=10)
            play_labels_ref.append(self.make_label)

        # Save references so I can update these later
        self.heading_label = play_labels_ref[0]
        self.score_label = play_labels_ref[1]
        self.instruction_label = play_labels_ref[2]
        self.results_label = play_labels_ref[3]

        # Club name label
        self.club_label = Label(self.quiz_frame, text="",
                                font=("Arial", 14, "bold"),
                                bg="#FFFFFF", relief="solid", width=25)
        self.club_label.grid(row=3, pady=10, padx=10)

        # Hint display label
        self.hint_label = Label(self.quiz_frame, text="Use the hints below if you're stuck! 💡",
                                font=body_font, bg="#FFF2CC",
                                wraplength=300, justify="left")
        self.hint_label.grid(row=4, pady=5, padx=10)

        # Answer buttons in a 2x2 grid
        self.answer_frame = Frame(self.quiz_frame)
        self.answer_frame.grid(row=6)

        for item in range(0, 4):
            self.answer_button = Button(self.answer_frame, font=("Arial", 12),
                         text="", width=15, bg="#FFFFFF",
                         command=partial(self.check_answer, item))
            self.answer_button.grid(row=item // 2, column=item % 2, padx=5, pady=5)
            self.answer_buttons_ref.append(self.answer_button)

        # Frame to hold hint and stats buttons
        self.hints_stats_frame = Frame(self.quiz_frame)
        self.hints_stats_frame.grid(row=8)

        # List of buttons to create
        control_button_list = [
            [self.quiz_frame, "Next Question", "#0057D8", self.next_question, 21, 7, None],
            [self.hints_stats_frame, "Club Hint", "#FF8000", self.show_hint_1, 15, 0, 0],
            [self.hints_stats_frame, "Nickname Hint", "#FF8000", self.show_hint_2, 15, 0, 1],
            [self.hints_stats_frame, "Stats", "#333333", self.to_stats, 12, 0, 2],
            [self.quiz_frame, "End quiz", "#990000", self.end_quiz_early, 21, 9, None]
        ]

        control_ref_list = []
        for item in control_button_list:
            make_control_button = Button(item[0], text=item[1], bg=item[2],
                         command=item[3], font=("Arial", 10, "bold"),
                         fg="#FFFFFF", width=item[4])
            make_control_button.grid(row=item[5], column=item[6], padx=5, pady=5)
            control_ref_list.append(make_control_button)

        # Save button references
        self.next_button = control_ref_list[0]
        self.hint1_button = control_ref_list[1]
        self.hint2_button = control_ref_list[2]
        self.stats_button = control_ref_list[3]
        self.end_quiz_button = control_ref_list[4]

        # Disable next and stats at the start
        self.next_button.config(state=DISABLED)
        self.stats_button.config(state=DISABLED)

        # Start the first question
        self.new_question()

    def new_question(self):
        """
        Loads a new question with club name and answer options.
        Resets hint tracking and button states.
        """
        # Reset for this question
        self.hints_used = 0
        self.hint1_used = False
        self.hint2_used = False

        self.hint_label.config(text="Use the hints below if you're stuck! 💡")
        self.results_label.config(text="", bg=self.quiz_frame.cget("bg"))
        self.next_button.config(state=DISABLED)

        # Reset hint buttons
        self.hint1_button.config(state=NORMAL, text="Club Hint")
        self.hint2_button.config(state=NORMAL, text="Nickname Hint")

        for item in self.answer_buttons_ref:
            item.config(state=NORMAL, bg="#FFFFFF")

        # Get current question data
        current = self.question_list[self.question_number]
        self.current_club = current[0]
        self.current_answer = current[1]
        self.current_hint_team = current[2]
        self.current_hint_nick = current[3]

        # Update labels
        self.heading_label.config(
            text="Question {} of {}".format(self.question_number + 1, self.total_questions))
        self.club_label.config(text=self.current_club)

        # Make 3 wrong answers + 1 correct
        wrong_options = [q[1] for q in self.all_questions if q[1] != self.current_answer]
        wrong_choices = random.sample(wrong_options, 3)
        options = wrong_choices + [self.current_answer]
        random.shuffle(options)
        self.current_options = options

        # Set button texts
        for count, item in enumerate(self.answer_buttons_ref):
            item.config(text=options[count])

    def show_hint_1(self):
        """
        Shows the club hint. Costs 1 potential point.
        """
        if not self.hint1_used:
            self.hint1_used = True
            self.hints_used += 1
            self.hint1_button.config(state=DISABLED, text="Club Hint ✓")

            if self.hint2_used:
                self.hint_label.config(
                    text="💡 Club Hint: {}\n🔍 Nickname Hint: {}".format(
                        self.current_hint_team, self.current_hint_nick))
            else:
                self.hint_label.config(
                    text="💡 Club Hint: {}".format(self.current_hint_team))

    def show_hint_2(self):
        """
        Shows the nickname hint. Costs 1 potential point.
        """
        if not self.hint2_used:
            self.hint2_used = True
            self.hints_used += 1
            self.hint2_button.config(state=DISABLED, text="Nickname Hint ✓")

            if self.hint1_used:
                self.hint_label.config(
                    text="💡 Club Hint: {}\n🔍 Nickname Hint: {}".format(
                        self.current_hint_team, self.current_hint_nick))
            else:
                self.hint_label.config(
                    text="🔍 Nickname Hint: {}".format(self.current_hint_nick))

    def check_answer(self, button_index):
        """
        Checks if the selected answer is correct, updates score,
        highlights correct/wrong answers, and records data.
        """
        chosen = self.current_options[button_index]

        # Disable all answer buttons and hint buttons
        for item in self.answer_buttons_ref:
            item.config(state=DISABLED)
        self.hint1_button.config(state=DISABLED)
        self.hint2_button.config(state=DISABLED)

        # Find the index of the correct answer
        correct_index = self.current_options.index(self.current_answer)

        if chosen == self.current_answer:
            # Calculate points (3 - hints used)
            points = 3 - self.hints_used
            self.score += points
            self.all_scores_list.append(points)
            self.all_correct_list.append(True)
            correct_so_far = self.questions_correct.get()
            self.questions_correct.set(correct_so_far + 1)
            # Highlight selected answer green
            self.answer_buttons_ref[button_index].config(bg="#D5E8D4")
            result_text = "✅ Correct! {} was right. +{} point/s".format(chosen, points)
            self.results_label.config(text=result_text, bg="#D5E8D4")
            result_word = "Correct"
        else:
            # Wrong answer - apply penalty if hints were used
            if self.hints_used > 0:
                self.score -= 1
                self.all_scores_list.append(-1)
                penalty_text = " -1 point penalty for using hints."
            else:
                self.all_scores_list.append(0)
                penalty_text = ""
            self.all_correct_list.append(False)
            # Highlight wrong answer in red
            self.answer_buttons_ref[button_index].config(bg="#F4CCCC")
            # Highlight correct answer in green
            self.answer_buttons_ref[correct_index].config(bg="#D5E8D4")
            result_text = "❌ Wrong! The answer was {}.{}".format(
                self.current_answer, penalty_text)
            self.results_label.config(text=result_text, bg="#F4CCCC")
            result_word = "Wrong"

        # Save to history
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
        self.score_label.config(text="Score: {}".format(self.score))

        # Check if this was the last question
        if self.question_number + 1 == self.total_questions:
            self.quiz_over(early=False)
        else:
            self.next_button.config(state=NORMAL)
            self.stats_button.config(state=NORMAL)

    def next_question(self):
        """
        Moves to the next question.
        """
        self.question_number += 1
        self.new_question()

    def end_quiz_early(self):
        """
        Called when user clicks 'End quiz' button during the quiz.
        Shows results based on questions answered so far.
        """
        # Only end if quiz hasn't already finished
        if self.next_button.winfo_exists() and self.next_button.winfo_ismapped():
            self.quiz_over(early=True)

    def quiz_over(self, early=False):
        """
        Ends the quiz, hides gameplay widgets, and shows a styled results frame.
        early=True means we ended before answering all questions.
        """
        # Hide all gameplay elements
        self.answer_frame.grid_remove()
        self.hints_stats_frame.grid_remove()
        self.next_button.grid_remove()
        self.end_quiz_button.grid_remove()
        self.results_label.grid_remove()
        self.score_label.grid_remove()
        self.instruction_label.grid_remove()
        self.club_label.grid_remove()
        self.hint_label.grid_remove()

        # Calculate stats based on answered questions
        answered_count = len(self.all_scores_list)
        if answered_count == 0:
            # No questions answered - show a simple message
            self.results_frame = Frame(self.quiz_frame, bg="#f0f0f0", bd=2, relief="groove")
            self.results_frame.grid(row=6, column=0, pady=10, padx=10)
            Label(self.results_frame, text="No questions were answered.", font=("Arial", 12), bg="#f0f0f0").grid(row=0, pady=10)
            btn_frame = Frame(self.results_frame, bg="#f0f0f0")
            btn_frame.grid(row=1, pady=10)
            Button(btn_frame, text="Play Again", bg="#006600", fg="#FFFFFF",
                   font=("Arial", 11, "bold"), width=12, command=self.play_again).grid(row=0, column=0, padx=5)
            Button(btn_frame, text="Exit", bg="#990000", fg="#FFFFFF",
                   font=("Arial", 11, "bold"), width=12, command=self.close_play).grid(row=0, column=1, padx=5)
            self.heading_label.config(text="Quiz Ended Early")
            return

        correct_answers = self.questions_correct.get()
        total_possible_score = answered_count * 3
        accuracy_percent = (correct_answers / answered_count) * 100 if answered_count > 0 else 0
        incorrect_answers = answered_count - correct_answers
        total_hints_used = sum(self.all_hints_list)

        # Create a results frame in the same spot as answer_frame used to be
        self.results_frame = Frame(self.quiz_frame, bg="#f0f0f0", bd=2, relief="groove")
        self.results_frame.grid(row=6, column=0, pady=10, padx=10)

        # Build the results display
        Label(self.results_frame, text="RESULTS", font=("Arial", 14, "bold"), bg="#f0f0f0").grid(row=0, column=0, columnspan=2, pady=8)

        Label(self.results_frame, text=f"Final Score: {self.score} / {total_possible_score}", font=("Arial", 12), bg="#f0f0f0").grid(row=1, column=0, sticky="w", padx=10, pady=4)
        Label(self.results_frame, text=f"Accuracy: {accuracy_percent:.1f}%", font=("Arial", 12), bg="#f0f0f0").grid(row=2, column=0, sticky="w", padx=10, pady=4)
        Label(self.results_frame, text=f"Correct Answers: {correct_answers}", font=("Arial", 12), bg="#f0f0f0").grid(row=3, column=0, sticky="w", padx=10, pady=4)
        Label(self.results_frame, text=f"Incorrect Answers: {incorrect_answers}", font=("Arial", 12), bg="#f0f0f0").grid(row=4, column=0, sticky="w", padx=10, pady=4)
        Label(self.results_frame, text=f"Total Hints Used: {total_hints_used}", font=("Arial", 12), bg="#f0f0f0").grid(row=5, column=0, sticky="w", padx=10, pady=4)

        # Button frame for Play Again, Statistics, Exit
        btn_frame = Frame(self.results_frame, bg="#f0f0f0")
        btn_frame.grid(row=6, column=0, columnspan=2, pady=10)

        Button(btn_frame, text="Play Again", bg="#006600", fg="#FFFFFF",
               font=("Arial", 11, "bold"), width=12, command=self.play_again).grid(row=0, column=0, padx=5)
        Button(btn_frame, text="Statistics", bg="#333333", fg="#FFFFFF",
               font=("Arial", 11, "bold"), width=12, command=self.to_stats).grid(row=0, column=1, padx=5)
        Button(btn_frame, text="Exit", bg="#990000", fg="#FFFFFF",
               font=("Arial", 11, "bold"), width=12, command=self.close_play).grid(row=0, column=2, padx=5)

        # Update heading
        if early:
            self.heading_label.config(text="Quiz Ended Early")
        else:
            self.heading_label.config(text="Quiz Complete!")

    def play_again(self):
        """
        Returns to the start screen (question count selection) instead of restarting the same quiz.
        """
        root.deiconify()
        self.play_box.destroy()

    def to_stats(self):
        """
        Opens the statistics popup.
        """
        questions_correct = self.questions_correct.get()
        stats_bundle = [questions_correct, self.all_scores_list,
                        self.all_hints_list, self.all_correct_list]
        Stats(self, stats_bundle)

    def close_play(self):
        """
        Returns to the start screen and closes the quiz.
        """
        root.deiconify()
        self.play_box.destroy()


class Stats:
    """
    Statistics popup showing quiz performance.
    """

    def __init__(self, partner, all_stats_info):
        # Disable buttons while stats are open
        partner.hint1_button.config(state=DISABLED)
        partner.hint2_button.config(state=DISABLED)
        if hasattr(partner, 'end_quiz_button'):
            partner.end_quiz_button.config(state=DISABLED)
        partner.stats_button.config(state=DISABLED)

        # Extract data
        questions_correct = all_stats_info[0]
        all_scores = all_stats_info[1]
        all_hints = all_stats_info[2]

        self.partner = partner
        sorted_scores = sorted(all_scores) if all_scores else [0]

        self.stats_box = Toplevel()
        self.stats_box.title("Statistics")
        self.stats_box.protocol('WM_DELETE_WINDOW',
                                partial(self.close_stats, partner))

        self.stats_frame = Frame(self.stats_box, width=350)
        self.stats_frame.grid()

        # Calculate statistics
        questions_played = len(all_scores)
        total_score = sum(all_scores)
        max_possible = questions_played * 3 if questions_played > 0 else 0
        best_score = sorted_scores[-1] if sorted_scores else 0
        average_score = total_score / questions_played if questions_played > 0 else 0
        total_hints = sum(all_hints)
        success_rate = (questions_correct / questions_played * 100) if questions_played > 0 else 0

        # Format strings with better spacing
        success_string = f"✅ Correct Answers: {questions_correct} / {questions_played}  ({success_rate:.1f}%)"
        total_score_string = f"🏆 Total Score: {total_score} / {max_possible}"
        hints_string = f"💡 Total Hints Used: {total_hints}"
        best_score_string = f"⭐ Best Score (single question): {best_score}"
        average_score_string = f"📊 Average Score Per Question: {average_score:.1f}"

        # Performance comment with colour coding
        comment_alignment = "W"
        if success_rate >= 90:
            comment_string = "🏆 Amazing! Perfect performance!"
            comment_colour = "#D5E8D4"
        elif success_rate >= 70:
            comment_string = "🎉 Great job! Really solid quiz!"
            comment_colour = "#D5E8D4"
        elif success_rate >= 50:
            comment_string = "👍 Good effort! Keep practicing!"
            comment_colour = "#FFF2CC"
        elif questions_played > 0 and questions_correct == 0:
            comment_string = "💡 No correct answers yet — try using the hints!"
            comment_colour = "#F8CECC"
            best_score_string = "⭐ Best Score: n/a"
        else:
            comment_string = "📚 Keep going! You'll improve with practice!"
            comment_colour = "#FFF2CC"

        heading_font = ("Arial", 14, "bold")
        normal_font = ("Arial", 12)
        comment_font = ("Arial", 11)

        # Labels with colour coding
        all_stats_strings = [
            ["📊 QUIZ STATISTICS", heading_font, ""],
            [success_string, normal_font, "W"],
            [total_score_string, normal_font, "W"],
            [hints_string, normal_font, "W"],
            [comment_string, comment_font, comment_alignment],
            ["", normal_font, ""],
            ["📈 DETAILED BREAKDOWN", heading_font, ""],
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

        # Colour the comment label
        if len(stats_label_ref_list) > 4:
            stats_comment_label = stats_label_ref_list[4]
            stats_comment_label.config(bg=comment_colour)

        # Export label
        self.export_label = Label(self.stats_frame, text="",
                                  font=("Arial", 10), fg="#555555",
                                  wraplength=300)
        self.export_label.grid(row=9, padx=10, pady=2)

        # Button frame
        button_frame = Frame(self.stats_frame)
        button_frame.grid(row=10, padx=10, pady=10)

        self.export_button = Button(button_frame,
                                    font=("Arial", 11, "bold"),
                                    text="📁 Export Results", bg="#0057D8",
                                    fg="#FFFFFF", width=14,
                                    command=partial(self.export_results, partner))
        self.export_button.grid(row=0, column=0, padx=5)

        self.dismiss_button = Button(button_frame,
                                     font=("Arial", 11, "bold"),
                                     text="✖ Dismiss", bg="#333333",
                                     fg="#FFFFFF", width=14,
                                     command=partial(self.close_stats, partner))
        self.dismiss_button.grid(row=0, column=1, padx=5)

    def export_results(self, partner):
        """
        Saves quiz history to a text file.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = "football_quiz_results_{}.txt".format(timestamp)

        try:
            with open(filename, "w") as file:
                file.write("=" * 50 + "\n")
                file.write("     FOOTBALL NICKNAME QUIZ RESULTS\n")
                file.write("=" * 50 + "\n")
                file.write(f"Date: {datetime.datetime.now().strftime('%d %B %Y %H:%M')}\n\n")

                # Write each question
                file.write("📋 QUESTION HISTORY\n")
                file.write("-" * 50 + "\n")
                for entry in partner.history_list:
                    emoji = "✅" if entry["result"] == "Correct" else "❌"
                    file.write(f"{emoji} Q{entry['question']}: {entry['club']}\n")
                    file.write(f"   Answer: {entry['correct_answer']} | You chose: {entry['chosen']}\n")
                    file.write(f"   Result: {entry['result']} | Hints: {entry['hints_used']} | Points: {entry['points']}\n\n")

                # Summary stats
                file.write("\n📊 SUMMARY STATISTICS\n")
                file.write("-" * 50 + "\n")
                total = sum(partner.all_scores_list)
                max_p = len(partner.all_scores_list) * 3 if partner.all_scores_list else 0
                correct = partner.questions_correct.get()
                played = len(partner.all_scores_list)
                acc = (correct / played * 100) if played > 0 else 0
                file.write(f"Correct Answers: {correct} / {played} ({acc:.1f}%)\n")
                file.write(f"Total Score: {total} / {max_p}\n")
                file.write(f"Total Hints Used: {sum(partner.all_hints_list)}\n")
                file.write("=" * 50 + "\n")

            self.export_label.config(
                text="✅ Saved as: {}".format(filename), fg="#006600")
            self.export_button.config(state=DISABLED)

        except OSError:
            self.export_label.config(
                text="❌ Could not save file. Check folder permissions.", fg="#990000")

    def close_stats(self, partner):
        """
        Closes stats window and re-enables buttons.
        """
        try:
            partner.hint1_button.config(state=NORMAL)
            partner.hint2_button.config(state=NORMAL)
            if hasattr(partner, 'end_quiz_button'):
                partner.end_quiz_button.config(state=NORMAL)
            partner.stats_button.config(state=NORMAL)
        except Exception:
            pass
        self.stats_box.destroy()


# Main program
if __name__ == "__main__":
    root = Tk()
    root.title("Football Nickname Quiz")
    Startquiz()
    root.mainloop()