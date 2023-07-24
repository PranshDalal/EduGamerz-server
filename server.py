from flask import Flask, jsonify, request
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

board = [' '] * 9
current_player = 'X'

questions = {
    "What color is the sky?": "blue",
    "What is 2 + 2?": "four",
    "What is the capital of France?": "paris"
}

current_question = None

def check_win(player):
    for i in range(0, 9, 3):
        if board[i] == board[i + 1] == board[i + 2] == player:
            return True

    for i in range(3):
        if board[i] == board[i + 3] == board[i + 6] == player:
            return True

    if board[0] == board[4] == board[8] == player:
        return True
    if board[2] == board[4] == board[6] == player:
        return True

    return False


def is_board_full():
    return all(cell != ' ' for cell in board)


def computer_move():
    empty_cells = [index for index, cell in enumerate(board) if cell == ' ']
    if empty_cells:
        return random.choice(empty_cells)
    return None


@app.route("/api/tictactoe/response", methods=['GET', 'POST'])
def tictactoe_response():
    global current_player, current_question, board

    if current_question is None or request.method == 'GET':
        current_question = random.choice(list(questions.keys()))

    if request.method == 'POST':
        data = request.get_json()
        question = data.get('question')
        answer = data.get('answer')

        if question == current_question:
            correct_answer = questions.get(question)
            if answer.lower() == correct_answer.lower():
                current_player = 'X'
                current_question = None

                empty_cells = [index for index, cell in enumerate(board) if cell == ' ']
                if empty_cells:
                    random_position = random.choice(empty_cells)
                    board[random_position] = 'X'

                    if check_win('X'):
                        return jsonify({
                            'message': 'You win!',
                            'board': board,
                            'question': None
                        }), 200

                    if is_board_full():
                        return jsonify({
                            'message': 'It\'s a draw!',
                            'board': board,
                            'question': None
                        }), 200

                    current_player = 'O'
                    computer_position = computer_move()
                    if computer_position is not None:
                        board[computer_position] = 'O'

                        if check_win('O'):
                            return jsonify({
                                'message': 'Computer wins!',
                                'board': board,
                                'question': None
                            }), 200

                    current_player = 'X'
                    current_question = random.choice(list(questions.keys()))
                else:
                    return jsonify({
                        'message': 'It\'s a draw!',
                        'board': board,
                        'question': None
                    }), 200
            else:
                return jsonify({
                    'message': 'Incorrect answer. Try again.',
                    'board': board,
                    'question': current_question
                }), 400

    return jsonify({
        'message': 'Answer the question to place your X or O.',
        'question': current_question,
        'board': board,
        'currentPlayer': current_player
    })


crossword_data = {
    "grid": [
        [" ", " ", " ", " "],
        [" ", " ", " "],
        [" ", " ", " ", " ", " "],            
        [" ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", " "],
        [" ", " "],
    ],
    "clues": {
        "1 Across": "What color is the sky?",
        "2 Across": "What is 1 + 1",
        "3 Across": "What is the capital of France?",
        "4 Across": "What color is grass?",
        "5 Across": "What is my name?",
        "6 Across": "Who will win the hackathon?"
    },
    "answers": {
        "1 Across": None,
        "2 Across": None,
        "3 Across": None,
        "4 Across": None,
        "5 Across": None,
        "6 Across": None
    },
}

current_game = None


@app.route("/api/crossword/game", methods=['GET', 'POST'])
def crossword_game():
    global current_game

    if current_game is None:
        current_game = crossword_data.copy()

    if request.method == 'POST':
        data = request.get_json()
        clue = data.get('clue')
        answer = data.get('answer')

        if not clue or not answer:
            return jsonify({"error": "Invalid data format."}), 400

        if clue not in current_game['answers']:
            return jsonify({"error": "Invalid clue."}), 400

        correct_answer = current_game['answers'][clue]
        if correct_answer is not None:
            return jsonify({"message": "This clue has already been answered."}), 400

        correct_answer = current_game['answers'][clue]
        if answer.upper() == current_game['answers'][clue]:
            current_game['answers'][clue] = answer.upper()
            return jsonify({"message": "Correct answer!", "clue": clue}), 200
        else:
            return jsonify({"message": "Incorrect answer. Try again.", "clue": clue}), 400

    return jsonify(current_game)


words = ["PYTHON", "JAVASCRIPT", "HTML", "CSS", "JAVA", "RUBY", "PHP", "C++", "SWIFT", "GO"]

hangman_word = None
hangman_word_state = None
hangman_figure = [
    " ________     ",
    "|        |    ",
    "|        0    ",
    "|       /|\   ",
    "|       / \   ",
    "|             ",
    "=============="
]
incorrect_guesses = 0
max_attempts = 6

def start_new_game():
    global hangman_word, hangman_word_state, hangman_figure, incorrect_guesses
    hangman_word = random.choice(words)
    hangman_word_state = ['_'] * len(hangman_word)
    incorrect_guesses = 0

def make_guess(guess):
    global hangman_word, hangman_word_state, incorrect_guesses
    if guess in hangman_word:
        for i in range(len(hangman_word)):
            if hangman_word[i] == guess:
                hangman_word_state[i] = guess
        return True
    else:
        incorrect_guesses += 1
        return False

@app.route("/api/hangman/start", methods=['GET'])
def start_game():
    start_new_game()
    return jsonify({"message": "New game started.", "hangman_word_state": hangman_word_state})

@app.route("/api/hangman/start_with_question", methods=['GET'])
def start_game_with_question():
    global hangman_word, hangman_word_state, hangman_figure, incorrect_guesses

    question, answer = random.choice(list(questions.items()))

    hangman_word = answer.upper()
    hangman_word_state = ['_'] * len(hangman_word)
    incorrect_guesses = 0

    return jsonify({"message": "New game started with a question.", "question": question, "hangman_word_state": hangman_word_state})

@app.route("/api/hangman/guess", methods=['POST'])
def guess():
    global hangman_word, hangman_word_state, hangman_figure, incorrect_guesses
    data = request.get_json()
    guess = data.get('guess', '').upper()

    if not guess.isalpha() or len(guess) != 1:
        return jsonify({"error": "Invalid guess. Please enter a single letter."}), 400

    if not hangman_word:
        return jsonify({"error": "Game has not started. Please start a new game."}), 400

    if guess in hangman_word_state:
        return jsonify({"message": "You already guessed that letter.", "hangman_word_state": hangman_word_state}), 200

    if make_guess(guess):
        if '_' not in hangman_word_state:
            return jsonify({"message": "Congratulations! You won!", "hangman_word": hangman_word, "hangman_word_state": hangman_word_state}), 200
        else:
            return jsonify({"message": "Correct guess!", "hangman_word_state": hangman_word_state}), 200
    else:
        if incorrect_guesses >= max_attempts:
            return jsonify({"message": "Game over. You lost!", "hangman_word": hangman_word, "hangman_word_state": hangman_word_state, "hangman_figure": hangman_figure}), 200
        else:
            return jsonify({"message": "Incorrect guess!", "hangman_word_state": hangman_word_state, "hangman_figure": hangman_figure[:incorrect_guesses + 1]}), 200
        
if __name__ == "__main__":
    app.run(debug=True)
