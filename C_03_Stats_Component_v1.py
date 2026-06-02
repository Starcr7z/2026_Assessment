from tkinter import *
from functools import partial  # To prevent unwanted windows


class StartQuiz:
    """
    Simplified start interface for testing the Stats component.
    Launches Play with hardcoded test data (no real quiz logic needed here).
    """

    def __init__(self):
        """
        Gets number of questions from user
        """

        self.start_frame = Frame(padx=10, pady=10)
        self.start_frame.grid()

        # Create play button (simplified — just for testing Stats)
        self.play_button = Button(self.start_frame, font=("Arial", 16, "bold"),
                                  fg="#FFFFFF", bg="#0057D8", text="Play", width=10,
                                  command=self.check_questions)
        self.play_button.grid(row=0, column=1, padx=20, pady=20)

    def check_questions(self):
        """
        Launches Play class with 5 hardcoded questions for testing.
        """
        Play(5)
        root.withdraw()


class Play:
    """
    Simplified game interface for testing the Stats class.
    Uses hardcoded test data so Stats can be developed independently.
    """

    def __init__(self, how_many):

        self.rounds_won = IntVar()

        # --- Test Data Sets (uncomment one set at a time for testing) ---

        # Perfect Score Test Data
        # self.all_scores_list = [3, 3, 3, 3, 3]
        # self.all_hints_list = [0, 0, 0, 0, 0]
        # self.all_correct_list = [True, True, True, True, True]
        # self.rounds_won.set(5)

        # Zero Score Test Data
        # self.all_scores_list = [-1, -1, 0, -1, 0]
        # self.all_hints_list = [2, 1, 0, 1, 0]
        # self.all_correct_list = [False, False, False, False, False]
        # self.rounds_won.set(0)

        # Mixed Score Test Data
        self.all_scores_list = [3, 0, 2, -1, 1]
        self.all_hints_list = [0, 0, 1, 2, 2]
        self.all_correct_list = [True, False, True, False, True]
        self.rounds_won.set(3)

        self.play_box = Toplevel()
        self.play_box.title("Football Nickname Quiz")

        self.game_frame = Frame(self.play_box)
        self.game_frame.grid(padx=10, pady=10)

        self.heading_label = Label(self.game_frame,
                                   text="Football Nickname Quiz ⚽",
                                   font=("Arial", 16, "bold"),
                                   padx=5, pady=5)
        self.heading_label.grid(row=0)

        # Stats button — the only control needed for this test component
        self.stats_button = Button(self.game_frame, font=("Arial", 14, "bold"),
                                   text="Stats", width=15, fg="#FFFFFF",
                                   bg="#333333", padx=10, pady=10,
                                   command=self.to_stats)
        self.stats_button.grid(row=1, pady=20)

    def to_stats(self):
        """
        Bundles all stats data and passes to Stats class.
        """
        rounds_won = self.rounds_won.get()
        stats_bundle = [rounds_won, self.all_scores_list,
                        self.all_hints_list, self.all_correct_list]
        Stats(self, stats_bundle)


class Stats:
    """
    Displays statistics popup for the Football Nickname Quiz.
    Shows: questions answered, correct answers, score summary,
    hints used, best score, and average score.
    Disables Stats button in parent while open to prevent crashes.
    """

    def __init__(self, partner, all_stats_info):

        # Disable stats button to prevent multiple stats windows opening
        partner.stats_button.config(state=DISABLED)

        # Extract data from bundle
        questions_correct = all_stats_info[0]
        all_scores = all_stats_info[1]
        all_hints = all_stats_info[2]
        all_correct = all_stats_info[3]

        # Sort scores to find best
        sorted_scores = sorted(all_scores)

        background = "#DAE8FC"

        self.stats_box = Toplevel()
        self.stats_box.title("Statistics")

        # If users press cross at top, close stats and re-enable button
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

        # Success rate
        success_rate = questions_correct / questions_played * 100

        # --- Build label strings ---
        success_string = (f"Correct Answers: {questions_correct} / {questions_played}"
                          f" ({success_rate:.0f}%)")
        total_score_string = f"Total Score: {total_score} / {max_possible}"
        hints_string = f"Total Hints Used: {total_hints}"
        best_score_string = f"Best Score: {best_score}"
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
            ["\nRound Stats", heading_font, ""],
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

        # Colour the comment label based on result
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
        Closes the stats window and re-enables the Stats button in Play.
        """
        partner.stats_button.config(state=NORMAL)
        self.stats_box.destroy()


# main routine
if __name__ == "__main__":
    root = Tk()
    root.title("Football Nickname Quiz")
    StartQuiz()
    root.mainloop()