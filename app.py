from inference.gemini import GeminiResponse
from modules.analysis import isNBA
from modules.blogs.getting_new_blogs import GettingNewBlogs
from modules.scraper import get_playoff_bracket, get_standings
from modules.transformer import create_html_bracket
from modules.query import Query
from data.text_data import unsure, non_nba
from flask import Flask, render_template, request, jsonify, redirect

app = Flask(__name__)
blog_list = []


"""
Function to handle routing to home page.

Parameters
----------
n/a

Returns
-------
HTML file
    Rendering of HTML template for home page.
"""
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/home")
def home2():
    return render_template("home.html")

"""
Function to handle routing to chatbox page.

Parameters
----------
n/a

Returns
-------
HTML file
    Rendering of HTML template for chatbox page
"""
@app.route("/chat")
def chat():
    return render_template("chat.html")

"""
Function to render blogs page.

Parameters
----------
n/a

Returns
-------
HTML file
    Rendering of HTML template for blog page
"""
@app.route("/blogs")
def blogs():
    global blog_list
    if len(blog_list) == 0:
        blog_list = GettingNewBlogs().get_new_blogs()
    return render_template("blogs.html", blogs=blog_list)

@app.route("/blog/<slug>")
def blog(slug):
    global blog_list
    # Lấy bài viết theo slug
    blog = next((b for b in blog_list if b['title'] == slug), None)
    if blog is None:
        return jsonify({"error": "Blog not found"}), 404
    return render_template("blog.html", blog=blog)

"""
Function to handle routing to authors page.

Parameters
----------
n/a

Returns
-------
HTML file
    Rendering of HTML template for authors page
"""
@app.route("/authors")
def authors():
    return render_template("authors.html")

"""
Function to handle routing to predictions page.

Parameters
----------
n/a

Returns
-------
HTML file
    Rendering of HTML template for predictions page
"""
@app.route("/predictions")
def predictions():
    bracket = get_playoff_bracket()
    bracket = create_html_bracket(bracket)
    west_standings = get_standings("west")
    east_standings = get_standings("east")
    return render_template("predictions.html", bracket=bracket, west_standings=west_standings, east_standings=east_standings)

"""
Function to download requested blog for user.

Parameters
----------
n/a

Returns
-------
HTML file
    Rendering of HTML template for blog page.
"""
@app.route("/download/<string:id>", methods=['GET', 'POST'])
def download(id):
    if id is None:
        self.Error(400)
    try:
        blog_map ={
            "1" : "https://drive.google.com/uc?export=download&id=13FmzW70fMMfTwrypxzJRG-J6woty8ePz", # Dog pic
            "2" : "https://drive.google.com/uc?export=download&id=13FmzW70fMMfTwrypxzJRG-J6woty8ePz", # Dog pic
            "3" : "https://drive.google.com/uc?export=download&id=13FmzW70fMMfTwrypxzJRG-J6woty8ePz"  # Dog pic
        }
        return redirect(blog_map[id])
    except Exception as e:
        self.log.exception(e)
        self.Error(400)

"""
Function to handle POST request from user
with embedded message. The message is then 
passed to the chatbot and the response is returned 
to user.

Parameters
----------
request : json
    The POST request sent from user sending a message

Returns
-------
Bot response : json
    The chatbot response to user message
"""
@app.route("/bot-msg", methods=['POST'])
def get_bot_response():
    usr_msg = request.form['msg']
    # handler = Query(usr_msg)
    # response = handler.process()
    # return jsonify(response)
    try:
       inference_handler = GeminiResponse(usr_msg)
       response_text = inference_handler.response() 
       return jsonify(response_text) # Structure response as needed
    except Exception as e:
       print(f"Error during inference: {e}")
       return jsonify({"error": "Failed to process request"}), 500


if __name__ == "__main__":
    app.run()