from tkinter import *
from functools import partial  # To prevent unwanted windows


class StartGame:
    """
    Initial Game interface (asks users how many questions they
    would like to answer in the football nickname quiz).
    Final version with updated hint and scoring system.
    """

    def __init__(self):
        """
        Gets number of questions from user
        """

        self.start_frame = Frame(padx=10, pady=10)
        self.start_frame.grid()

        # Strings for labels
        intro_string = ("Each question shows a football club and 4 nickname options. "
                        "Pick the correct answer to score points. "
                        "You can use up to 2 hints per question — each hint "
                        "costs 1 point from your potential score.\n\n"
                        "Correct, no hints used = 3 points\n"
                        "Correct, 1 hint used = 2 point\n"
                        "Correct, 2 hints used = 1 points\n"
                        "Wrong answer (no hints used) = 0 point\n"
                        "Wrong answer (any hints used) = -1 points")

        choose_string = "How many questions do you want to answer?"

        # List of labels to be made (text | font | fg)
        start_labels_list = [
            ["Football Nickname Quiz", ("Arial", 16, "bold"), None],
            [intro_string, ("Arial", 12), None],
            [choose_string, ("Arial", 12, "bold"), "#009900"]
        ]

        # Create labels and add them to the reference list
        start_label_ref = []
        for count, item in enumerate(start_labels_list):
            make_label = Label(self.start_frame, text=item[0], font=item[1],
                               fg=item[2],
                               wraplength=350, justify="left", pady=10, padx=20)
            make_label.grid(row=count)
            start_label_ref.append(make_label)

        # Extract choice label so it can be changed to an error message if necessary
        self.choose_label = start_label_ref[2]

        # Frame so that entry box and button can be in the same row
        self.entry_area_frame = Frame(self.start_frame)
        self.entry_area_frame.grid(row=3)

        self.num_questions_entry = Entry(self.entry_area_frame, font=("Arial", 20, "bold"),
                                         width=10)
        self.num_questions_entry.grid(row=0, column=0, padx=10, pady=10)

        # Create play button
        self.play_button = Button(self.entry_area_frame, font=("Arial", 16, "bold"),
                                  fg="#FFFFFF", bg="#0057D8", text="Play", width=10,
                                  command=self.check_questions)
        self.play_button.grid(row=0, column=1)

        # Create exit button
        self.exit_button = Button(self.start_frame, font=("Arial", 12, "bold"),
                                  fg="#FFFFFF", bg="#990000", text="Exit", width=10,
                                  command=self.start_frame.quit)
        self.exit_button.grid(row=4, pady=10)

    def check_questions(self):
        """
        Checks users have entered a valid number of questions (between 1 and MAX_QUESTIONS).
        Rejects values outside range, negative numbers, zero, and noninteger input.
        """

        # Total questions available in the quiz
        MAX_QUESTIONS = 100

        # Retrieve number entered by user
        questions_wanted = self.num_questions_entry.get()

        # Reset label and entry box (for when users come back to home screen)
        self.choose_label.config(fg="#009900", font=("Arial", 12, "bold"))
        self.num_questions_entry.config(bg="#FFFFFF")

        error = "Oops - Please choose a whole number between 1 and {}.".format(MAX_QUESTIONS)
        has_errors = "no"

        # Check input is a whole number within valid range
        try:
            questions_wanted = int(questions_wanted)
            if 1 <= questions_wanted <= MAX_QUESTIONS:
                # Invoke Play class and pass number of questions across
                Play(questions_wanted)
                # Hide root window (start screen) while quiz is running
                root.withdraw()
            else:
                has_errors = "yes"

        except ValueError:
            has_errors = "yes"

        # Display the error if necessary
        if has_errors == "yes":
            self.choose_label.config(text=error, fg="#990000",
                                     font=("Arial", 10, "bold"))
            self.num_questions_entry.config(bg="#F4CCCC")
            self.num_questions_entry.delete(0, END)


class Play:
    """
    Interface for playing the Football Nickname Quiz.
    Includes heading, score display, End Game button and close logic.
    """

    def __init__(self, how_many):
        self.play_box = Toplevel()
        self.play_box.title("Football Nickname Quiz")

        self.game_frame = Frame(self.play_box)
        self.game_frame.grid(padx=10, pady=10)

        # Track current question number and score
        self.question_number = 1
        self.total_questions = how_many
        self.score = 0

        # Heading label showing current question number
        self.game_heading_label = Label(self.game_frame,
                                        text=f"Question {self.question_number} of {how_many}",
                                        font=("Arial", "16", "bold"))
        self.game_heading_label.grid(row=0)

        # Score label
        self.score_label = Label(self.game_frame,
                                 text="Score: 0",
                                 font=("Arial", "12"),
                                 fg="#0057D8")
        self.score_label.grid(row=1, pady=5)

        # End game button - always available
        self.end_game_button = Button(self.game_frame, text="End Game",
                                      font=("Arial", "16", "bold"),
                                      fg="#FFFFFF", bg="#990000", width=10,
                                      command=self.close_play)
        self.end_game_button.grid(row=2, pady=10)

    def close_play(self):
        """
        Closes the play window and returns to the start screen
        """
        # Re-show start screen and close quiz window
        root.deiconify()
        self.play_box.destroy()


# main routine
if __name__ == "__main__":
    root = Tk()
    root.title("Football Nickname Quiz")
    StartGame()
    root.mainloop()