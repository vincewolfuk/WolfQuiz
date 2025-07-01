from flask import Flask, render_template, request, redirect, url_for, session
from quiz_data import quiz  # Default quiz import

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this to a real secret key in production

@app.route("/")
def home_redirect():
    return redirect(url_for("home"))

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/quiz/<theme>")
def quiz_theme(theme):
    # Initialize quiz data based on theme
    if theme == "capitals":
        from quiz_data import quiz as selected_quiz
    # elif theme == "animals":
    #     from animals_quiz import quiz as selected_quiz
    else:
        return "Quiz theme not found", 404
    
    # Store the selected quiz in session
    session['current_quiz'] = selected_quiz
    session['current_theme'] = theme
    return redirect(url_for("quiz_page"))

@app.after_request
def disable_cache(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route("/restart")
def restart():
    session.clear()
    return redirect(url_for("home"))  # Changed to redirect to home

@app.route("/quiz", methods=["GET", "POST"])
def quiz_page():
    # Check if quiz is selected
    if 'current_quiz' not in session:
        return redirect(url_for("home"))
    
    current_quiz = session['current_quiz']
    
    if request.method == "GET" and "question_index" not in session:
        session["question_index"] = 0
        session["results"] = []

    if request.method == "POST":
        user_answer = request.form.get("answer")
        if not user_answer:
            return redirect(url_for("quiz_page"))
            
        question = current_quiz[session["question_index"]]
        correct = user_answer == question["answer"]

        # Store the result
        result = {
            "question": question["question"],
            "your_answer": user_answer,
            "correct_answer": question["answer"],
            "is_correct": correct,
            "image": question.get("image", ""),
            "feedback_image": question.get("feedback_image", "")
        }
        session["results"].append(result)

        # Store feedback data
        session["feedback_data"] = {
            "is_correct": correct,
            "message": "Correct!" if correct else f"Wrong! The correct answer was: {question['answer']}",
            "feedback_image": question.get("feedback_image", ""),
            "next_index": session["question_index"] + 1,
            "theme": session.get("current_theme", "capitals")
        }
        return redirect(url_for("feedback_page"))

    index = session["question_index"]
    if index >= len(current_quiz):
        results = session["results"]
        theme = session.get("current_theme", "capitals")
        session.clear()
        return render_template("result.html", results=results, theme=theme)

    return render_template("single_question.html", 
                         question=current_quiz[index], 
                         index=index,
                         total_questions=len(current_quiz),
                         theme=session.get("current_theme", "capitals"))

@app.route("/feedback", methods=["GET", "POST"])
def feedback_page():
    if "feedback_data" not in session:
        return redirect(url_for("quiz_page"))

    if request.method == "POST":
        session["question_index"] = session["feedback_data"]["next_index"]
        return redirect(url_for("quiz_page"))

    return render_template("feedback.html", 
                         feedback=session["feedback_data"],
                         theme=session.get("current_theme", "capitals"))

if __name__ == "__main__":
    app.run(debug=True)