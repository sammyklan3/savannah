import pymysql
import os
import uuid
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    url_for,
    make_response,
    jsonify,
)
import bcrypt
import secrets
import re
from datetime import datetime, timedelta
import random
import string

app = Flask(__name__)
app.secret_key = "@j%&Ge*cW%Vs$5930Jmj"

# Set the permanent session lifetime
app.permanent_session_lifetime = timedelta(days=30)


# Set up database connection parameters
connection = pymysql.connect(
    host="localhost", user="root", password="", database="savannah"
)

# System for profile picture uploading
UPLOAD_FOLDER = "static/profile"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# get profile picture filename for the current user
def get_profile_picture_filename():
    connection = pymysql.connect(
        host="localhost", user="root", password="", database="savannah"
    )
    cursor = connection.cursor()
    cursor.execute(
        "SELECT profile_pic FROM users WHERE username = %s", (session.get("key"),)
    )
    result = cursor.fetchone()
    connection.close()
    return result[0] if result else None


# pass profile picture filename to all templates
@app.context_processor
def inject_profile_picture_filename():
    return dict(profile_picture_filename=get_profile_picture_filename())


# Home route
@app.route("/")
def home():
    if "key" in session:
        cursor = connection.cursor()
        # Fetch current_user information
        cursor.execute(
            "SELECT user_id FROM users WHERE username = %s", (session.get("key"),)
        )
        user = cursor.fetchone()

        return render_template("index.html")
    else:
        return redirect("/login")


@app.route("/edit_profile", methods=["POST", "GET"])
def edit_profile():
    if "key" in session:
        try:
            # Create a cursor object to interact with the database
            with connection.cursor() as cursor:
                # Fetch user information
                cursor.execute(
                    "SELECT * FROM users WHERE username = %s", (session.get("key"),)
                )
                user = cursor.fetchone()

                # Fetch posts by the user
                cursor.execute("SELECT * FROM posts WHERE user_id = %s", (user[1],))
                posts = cursor.fetchall()

            return render_template("edit_profile.html", user=user, posts=posts)

        except:
            # Handle any potential exceptions and provide an error message
            return f"An error occurred: {str(e)}"
    else:
        return redirect("/login")


# Home route
@app.route("/new_post")
def new_post():
    if "key" in session:
        return render_template("new_post.html")
    else:
        return redirect("/login")


@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]
        password2 = request.form["password2"]
        phone = request.form["phone"]

        # Check if the user already exists
        cursor = connection.cursor()
        query = "SELECT COUNT(*) FROM users WHERE email=%s"
        cursor.execute(query, email)
        result = cursor.fetchone()

        if result[0] > 0:
            return render_template("signup.html", msg="Email already exists")

        # check if passwords are the same
        if password != password2:
            return render_template("signup.html", msg="Passwords do not match")
        elif len(password) < 8:
            return render_template("signup.html", msg="Try something longer")
        elif not re.search("[A-Z]", password):
            return render_template("signup.html", msg="Also use uppercase letters")
        elif not re.search("[0-9]", password):
            return render_template("signup.html", msg="Must have numerics")
        elif not re.search("[!@#$%^&*]", password):
            return render_template(
                "signup.html", msg="Must use special symbols such as $*&%#@!"
            )

        # hash the password
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        # generate a user ID
        user_id = secrets.token_hex(16)
        # insert the user
        cursor.execute(
            "INSERT INTO users (user_id, email, username, password, phone) VALUES (%s, %s, %s, %s, %s)",
            (user_id, email, username, hashed_password.decode("utf-8"), phone),
        )

        connection.commit()

        session["key"] = username

        return render_template("index.html", msg="Account created successfully")
    else:
        return render_template("signup.html")


# Maximum number of allowed login attempts
MAX_LOGIN_ATTEMPTS = 5

# Lockout duration in minutes
LOCKOUT_DURATION = 10

# Dictionary to store login attempts and lockout status
login_attempts = {}


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Check if the user is currently locked out
        is_locked_out, remaining_time = is_user_locked_out(username)
        if is_locked_out:
            return render_template(
                "login.html",
                msg="Account locked. Please try again after {0} minutes.".format(
                    remaining_time
                ),
            )

        # Retrieve the user from the database
        cursor = connection.cursor()
        query = "SELECT * FROM users WHERE username=%s"
        cursor.execute(query, username)
        user = cursor.fetchone()

        if user:
            # Check if the password matches
            hashed_password = user[4].encode("utf-8")
            if bcrypt.checkpw(password.encode("utf-8"), hashed_password):
                session["key"] = user[3]

                # Reset the login attempts for the user
                reset_login_attempts(username)

                # Set the session to permanent if the user wants to stay logged in
                if request.form.get("keep_logged_in"):
                    session.permanent = True

                return render_template("index.html", msg="Login successful")

            # Incorrect password
            # Increment the login attempts for the user
            increment_login_attempts(username)
            return render_template("login.html", msg="Incorrect username or password")
        else:
            # User does not exist
            return render_template("signup.html", msg="  User does not exist please create an account")
    else:
        return render_template("login.html")



@app.route("/logout")
def logout():
    # Clear session data
    session.clear()

    # Redirect to login page
    return redirect(url_for("login"))


def is_user_locked_out(username):
    if username in login_attempts:
        # Get the timestamp of the last login attempt
        last_attempt_time = login_attempts[username]["last_attempt_time"]

        # Calculate the lockout end time
        lockout_end_time = last_attempt_time + timedelta(minutes=LOCKOUT_DURATION)

        # Check if the current time is within the lockout period
        if datetime.now() < lockout_end_time:
            remaining_time = (lockout_end_time - datetime.now()).seconds // 60
            return True, remaining_time

    return False, 0


def increment_login_attempts(username):
    if username in login_attempts:
        login_attempts[username]["attempts"] += 1
    else:
        login_attempts[username] = {"attempts": 1, "last_attempt_time": datetime.now()}

    # Check if the maximum login attempts have been reached
    if login_attempts[username]["attempts"] >= MAX_LOGIN_ATTEMPTS:
        lockout_user(username)


def lockout_user(username):
    login_attempts[username]["lockout_time"] = datetime.now()


def reset_login_attempts(username):
    if username in login_attempts:
        del login_attempts[username]


def format_timestamp(timestamp):
    now = datetime.now()
    posted_time = datetime.strptime(str(timestamp), "%Y-%m-%d %H:%M:%S")
    time_diff = now - posted_time

    if time_diff.days > 7:
        return posted_time.strftime("%B %d, %Y")  # Format: Month day, Year
    elif time_diff.days > 0:
        return f"{time_diff.days} days ago"
    elif time_diff.seconds >= 3600:  # Use >= instead of just >
        hours = time_diff.seconds // 3600
        return (
            f"{hours} hour ago" if hours == 1 else f"{hours} hours ago"
        )  # Use singular "hour" if it's exactly 1 hour
    elif time_diff.seconds > 60:
        minutes = time_diff.seconds // 60
        return f"{minutes} minutes ago"
    else:
        return "Just now"


@app.route("/profile", methods=["POST", "GET"])
def profile():
    # Check if the user is authenticated before accessing the profile page.
    if "key" in session:
        try:
            # Get the current user's profile information
            with pymysql.connect(
                host="localhost", user="root", password="", database="savannah"
            ) as connection:
                cursor = connection.cursor()

                # Fetch user information
                cursor.execute(
                    "SELECT * FROM users WHERE username = %s", (session.get("key"),)
                )
                user = cursor.fetchone()

                if not user:
                    # Handle the case where the user is not found
                    return "User not found"

                # Fetch posts by the user
                cursor.execute("SELECT * FROM posts WHERE user_id = %s", (user[1],))
                posts = cursor.fetchall()

                # Convert tuples to lists
                posts = [list(post) for post in posts]

                # Get the number of followers
                cursor.execute(
                    "SELECT COUNT(*) FROM followers WHERE following_id = %s", (user[1],)
                )
                followers_count = cursor.fetchone()[0]

                # Get the number of following
                cursor.execute(
                    "SELECT COUNT(*) FROM followers WHERE follower_id = %s", (user[1],)
                )
                following_count = cursor.fetchone()[0]

            # Convert timestamp to human-readable format
            for post in posts:
                post_timestamp = post[4]
                post[4] = format_timestamp(post_timestamp)

            # Render the profile template
            current_user_id = user[0]
            username = user[3]
            email = user[2]
            bio = user[7]
            return render_template(
                "profile.html",
                current_user_id=current_user_id,
                username=username,
                email=email,
                bio=bio,
                posts=posts,
                followers_count=followers_count,
                following_count=following_count,
            )

        except Exception as e:
            # Handle any potential exceptions and provide an error message
            return f"An error occurred: {str(e)}"

    else:
        return redirect("/login")


# Profile picture
@app.route("/upload_profile_pic", methods=["POST"])
def upload_profile_pic():
    if "key" in session:
        file = request.files["profile_pic"]
        if file and allowed_file(file.filename):
            filename = str(uuid.uuid4()) + "." + file.filename.rsplit(".", 1)[1].lower()
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            # delete old profile pic if it exists
            connection = pymysql.connect(
                host="localhost", user="root", password="", database="savannah"
            )
            cursor = connection.cursor()
            cursor.execute(
                "SELECT profile_pic FROM users WHERE username=%s",
                (session.get("key"),),
            )
            result = cursor.fetchone()
            if result and result[0]:
                old_profile_pic_path = os.path.join(
                    app.config["UPLOAD_FOLDER"], result[0]
                )
                if os.path.exists(old_profile_pic_path):
                    os.remove(old_profile_pic_path)

            # update profile_pic field in database
            cursor.execute(
                "UPDATE users SET profile_pic=%s WHERE username=%s",
                (filename, session.get("key")),
            )
            connection.commit()

            return redirect("/profile")
        else:
            return render_template("profile.html", msg="Only image files are allowed")
    else:
        return redirect("/login")


import os


@app.route("/delete_account", methods=["POST", "GET"])
def delete_account():
    if "key" in session:
        # Retrieve the current user ID from the session
        cursor = connection.cursor()
        query_user_id = "SELECT user_id FROM users WHERE username = %s"
        cursor.execute(query_user_id, (session.get("key"),))
        current_user_id = cursor.fetchone()[0]

        # Check if the current user is logged in
        if not current_user_id:
            return "Unauthorized", 401

        try:
            # Create a cursor object to interact with the database
            with connection.cursor() as cursor:
                # Retrieve the user's profile picture file path
                query_profile_picture = (
                    "SELECT profile_pic FROM users WHERE user_id = %s"
                )
                cursor.execute(query_profile_picture, (current_user_id,))
                profile_pic = cursor.fetchone()[0]

                # Delete the user's posts and related files
                query_posts = "SELECT user_id, filename FROM posts WHERE user_id = %s"
                cursor.execute(query_posts, (current_user_id,))
                posts = cursor.fetchall()

                for post in posts:
                    user_id, filename = post
                    # Delete the post's image file
                    if filename:
                        file_path = os.path.join("static/posts", filename)
                        os.remove(file_path)
                    else:
                        pass

                    # Delete the post record from the database
                    query_delete_post = "DELETE FROM posts WHERE user_id = %s"
                    cursor.execute(query_delete_post, (user_id,))

                # Delete the user's profile picture file
                if profile_pic and profile_pic != "default.png":
                    file_path = os.path.join("static/profile", profile_pic)
                    os.remove(file_path)
                else:
                    pass

                # Delete the user's record from the users table
                query_delete_user = "DELETE FROM users WHERE user_id = %s"
                cursor.execute(query_delete_user, (current_user_id,))

                # Delete the user's records from the followers table
                query_delete_followers = (
                    "DELETE FROM followers WHERE follower_id = %s OR following_id = %s"
                )
                cursor.execute(
                    query_delete_followers, (current_user_id, current_user_id)
                )

            # Commit the changes to the database
            connection.commit()

            # Perform any additional cleanup or logout operations
            session.clear()

            # Redirect to a landing page or login page
            return redirect(url_for("login"))

        except Exception as e:
            # Handle any potential exceptions and provide an error message
            return "An error occurred: " + str(e)
    else:
        return redirect("/login")


@app.route("/messages", methods=["POST", "GET"])
def messages():
    if "key" in session:
        return render_template("messages.html")
    else:
        return redirect("/login")


@app.route("/search", methods=["GET", "POST"])
def search():
    if "key" in session:
        if request.method == "POST":
            # Get the search query from the form
            search_query = request.form["q"]

            # Create a cursor object to interact with the database
            cursor = connection.cursor()

            # Prepare the SQL query
            query = "SELECT * FROM users WHERE username LIKE %s"

            # Execute the query with the search query as a parameter
            cursor.execute(query, f"%{search_query}%")

            # Fetch all the results
            results = cursor.fetchall()

            # Close the cursor
            cursor.close()

            # Render the template with the search results
            return render_template("search.html", results=results)
        else:
            # If it's a GET request, render the search form
            return render_template("search.html")
    else:
        return redirect("/login")


@app.route("/follow/<username>", methods=["POST"])
def follow(username):
    if "key" in session:
        # Retrieve the current user ID from the session
        current_username = session.get("key")

        # Check if the current user is logged in
        if not current_username:
            return "Unauthorized", 401

        try:
            # Create a cursor object to interact with the database
            with connection.cursor() as cursor:
                # Retrieve the user ID of the user being followed
                query_user_id = "SELECT user_id FROM users WHERE username = %s"
                cursor.execute(query_user_id, (username,))
                user_id = cursor.fetchone()[0]

                # Retrieve the user ID of the current user
                query_current_user_id = "SELECT user_id FROM users WHERE username = %s"
                cursor.execute(query_current_user_id, (current_username,))
                current_user_id = cursor.fetchone()[0]

                # Check if the current user is already following the user
                query_check_following = "SELECT COUNT(*) FROM followers WHERE follower_id = %s AND following_id = %s"
                cursor.execute(query_check_following, (current_user_id, user_id))
                already_following = cursor.fetchone()[0] > 0

                if already_following:
                    return "Already following", 400

                # Insert the follow relationship into the database
                query_follow = (
                    "INSERT INTO followers (follower_id, following_id) VALUES (%s, %s)"
                )
                cursor.execute(query_follow, (current_user_id, user_id))

            # Commit the changes to the database
            connection.commit()

            # Redirect to the user's profile page
            return redirect(url_for("user_profile", username=username))

        except Exception as e:
            # Handle any potential exceptions and provide an error message
            return "An error occurred: " + str(e)
    else:
        return redirect("/login")


@app.route("/unfollow/<username>", methods=["POST"])
def unfollow(username):
    if "key" in session:
        # Retrieve the current user ID from the session
        current_username = session.get("key")

        # Check if the current user is logged in
        if not current_username:
            return "Unauthorized", 401

        try:
            # Create a cursor object to interact with the database
            with connection.cursor() as cursor:
                # Retrieve the user ID of the user being unfollowed
                query_user_id = "SELECT user_id FROM users WHERE username = %s"
                cursor.execute(query_user_id, (username,))
                user_id = cursor.fetchone()[0]

                # Retrieve the user ID of the current user
                query_current_user_id = "SELECT user_id FROM users WHERE username = %s"
                cursor.execute(query_current_user_id, (current_username,))
                current_user_id = cursor.fetchone()[0]

                # Check if the current user is already following the user
                query_check_following = "SELECT COUNT(*) FROM followers WHERE follower_id = %s AND following_id = %s"
                cursor.execute(query_check_following, (current_user_id, user_id))
                already_following = cursor.fetchone()[0] > 0

                if not already_following:
                    return "Not following", 400

                # Delete the follow relationship from the database
                query_unfollow = (
                    "DELETE FROM followers WHERE follower_id = %s AND following_id = %s"
                )
                cursor.execute(query_unfollow, (current_user_id, user_id))

            # Commit the changes to the database
            connection.commit()

            # Redirect to the user's profile page
            return redirect(url_for("user_profile", username=username))

        except Exception as e:
            # Handle any potential exceptions and provide an error message
            return "An error occurred: " + str(e)
    else:
        return redirect("/login")


@app.route("/profile/<username>")
def user_profile(username):
    if "key" in session:
        try:
            cursor = connection.cursor()
            # Fetch current_user information
            cursor.execute(
                "SELECT user_id FROM users WHERE username = %s", (session.get("key"),)
            )
            current_user_id = cursor.fetchone()

            # Create a cursor object to interact with the database
            with connection.cursor() as cursor:
                # Prepare the SQL query to fetch the user profile
                query_profile = "SELECT * FROM users WHERE username = %s"
                cursor.execute(query_profile, (username,))
                user_profile = cursor.fetchone()

                if not user_profile:
                    # Handle the case where the username is not found
                    return "User not found"

                # Check if the current user is following the profile user
                is_following = False
                if current_user_id:
                    query_follower = "SELECT COUNT(*) FROM followers WHERE follower_id = %s AND following_id = %s"
                    cursor.execute(query_follower, (current_user_id, user_profile[1]))
                    is_following = cursor.fetchone()[0] > 0

                # Prepare the SQL queries to fetch the follower and following counts
                query_followers_count = (
                    "SELECT COUNT(*) FROM followers WHERE following_id = %s"
                )
                cursor.execute(query_followers_count, (user_profile[1],))
                followers_count = cursor.fetchone()[0]

                query_following_count = (
                    "SELECT COUNT(*) FROM followers WHERE follower_id = %s"
                )
                cursor.execute(query_following_count, (user_profile[1],))
                following_count = cursor.fetchone()[0]

                # Prepare the SQL query to fetch the user's posts
                query_posts = "SELECT * FROM posts WHERE user_id = %s"
                cursor.execute(query_posts, (user_profile[1],))
                user_posts = cursor.fetchall()

                # Convert tuples to lists
                user_posts = [list(post) for post in user_posts]

                # Convert timestamp to human-readable format
                for post in user_posts:
                    post_timestamp = post[4]
                    post[4] = format_timestamp(post_timestamp)

            # Render the template with the user profile data, following information, and posts
            return render_template(
                "user_profile.html",
                user=user_profile,
                is_following=is_following,
                followers_count=followers_count,
                following_count=following_count,
                posts=user_posts,
                current_user_id=current_user_id,
            )

        except Exception as e:
            # Handle any potential exceptions and provide an error message
            return "An error occurred: " + str(e)
    else:
        return redirect("/login")


# Function to generate a random string for the file name
def generate_random_string(length):
    letters = string.ascii_letters
    return "".join(random.choice(letters) for _ in range(length))


# Define upload folder for post upload
app.config["UPLOAD_FOLDER2"] = "static/posts/"


# Route for handling the file upload
@app.route("/upload", methods=["POST", "GET"])
def upload_file():
    if "key" not in session:
        return redirect("/login")

    file = request.files.get("file")
    title = request.form.get("title")
    caption = request.form.get("caption")

    if not (file and title and caption):
        return "Please fill in all the required fields"

    # Check if the file has an allowed extension
    allowed_extensions = {"jpg", "jpeg", "png", "gif", "mp4", "mov"}
    file_extension = file.filename.rsplit(".", 1)[1].lower()
    if file_extension not in allowed_extensions:
        return "Invalid file extension. Allowed extensions are: jpg, jpeg, png, gif, mp4, mov."

    # Generate a random file name
    random_filename = generate_random_string(10) + "." + file_extension
    file_path = os.path.join(app.config["UPLOAD_FOLDER2"], random_filename)

    try:
        file.save(file_path)
    except Exception as e:
        return f"Error saving file: {str(e)}"

    # Get file type and size
    file_type = file.content_type
    file_size = os.path.getsize(file_path)

    # Get the current user's ID (replace this with your own authentication logic)
    # Get the following_id from the session
    cursor = connection.cursor()
    cursor.execute(
        "SELECT user_id FROM users WHERE username = %s",
        (session.get("key"),),
    )
    user_id = cursor.fetchone()[0]

    # Insert the file name, file type, file size, user ID, title, and caption into the database
    with connection.cursor() as cursor:
        sql = "INSERT INTO posts (filename, file_type, file_size, user_id, title, caption) VALUES (%s, %s, %s, %s, %s, %s)"
        try:
            cursor.execute(
                sql,
                (
                    random_filename,
                    file_type,
                    file_size,
                    user_id,
                    title,
                    caption,
                ),
            )
            connection.commit()
        except Exception as e:
            return f"Error inserting into database: {str(e)}"

    return "File uploaded successfully."
    return redirect("/profile")


@app.route("/delete_post/<int:post_id>", methods=["POST"])
def delete_post(post_id):
    # Check if the user is authenticated before deleting the post.
    if "key" in session:
        # Delete the post with the given post_id from the database
        with pymysql.connect(
            host="localhost", user="root", password="", database="savannah"
        ) as connection:
            cursor = connection.cursor()

            # Fetch the post to ensure it belongs to the current user
            cursor.execute("SELECT * FROM posts WHERE id = %s", (post_id,))
            post = cursor.fetchone()

            # Check if the post exists and belongs to the current user
            if post and post[1] == session.get("key"):
                # Delete the post
                cursor.execute("DELETE FROM posts WHERE id = %s", (post_id,))
                connection.commit()
                flash("Post deleted successfully.", "success")
            else:
                flash("Unable to delete the post.", "error")
    else:
        flash("Please login to delete the post.", "error")


@app.route("/like", methods=["POST"])
def like_post():
    if "key" in session:
        try:
            post_id = request.form.get("post_id")

            # Update the database to increment the like count for the post
            with connection.cursor() as cursor:
                query_update_likes = "UPDATE posts SET likes = likes + 1 WHERE id = %s"
                cursor.execute(query_update_likes, (post_id,))
                connection.commit()

            # Fetch the updated like count from the database
            with pymysql.connect(
                host="localhost", user="root", password="", database="savannah"
            ) as connection:
                cursor = connection.cursor()

                # Fetch the updated like count
                cursor.execute("SELECT likes FROM posts WHERE post_id = %s", (post_id,))
                updated_likes = cursor.fetchone()[0]

            return jsonify({"likes": updated_likes})

        except Exception as e:
            # Handle any potential exceptions and provide an error response
            return jsonify({"error": str(e)}), 500
    else:
        return redirect("/login")


# Running the app...
if __name__ == "__main__":
    app.run(debug=True)  # Debugging fixes errors
