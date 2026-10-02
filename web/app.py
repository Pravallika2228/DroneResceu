import os
import sys
import json
import numpy as np

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    session,
    redirect,
    url_for
)

from werkzeug.utils import secure_filename


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.insert(
    0,
    PROJECT_ROOT
)


# ============================================================
# AI PIPELINE
# ============================================================

from src.drone_analysis import (
    analyze_drone_image
)


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)

app.secret_key = (
    "drone-rescue-project-secret-key"
)


# ============================================================
# UPLOAD CONFIGURATION
# ============================================================

UPLOAD_FOLDER = os.path.join(
    PROJECT_ROOT,
    "web",
    "static",
    "uploads"
)

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

app.config["UPLOAD_FOLDER"] = (
    UPLOAD_FOLDER
)


# ============================================================
# DATA STORAGE
# ============================================================

DATA_FOLDER = os.path.join(
    PROJECT_ROOT,
    "web",
    "data"
)

os.makedirs(
    DATA_FOLDER,
    exist_ok=True
)

HISTORY_FILE = os.path.join(
    DATA_FOLDER,
    "analysis_history.json"
)


# ============================================================
# HISTORY HELPERS
# ============================================================

def load_history():

    if not os.path.exists(
        HISTORY_FILE
    ):
        return []

    try:

        with open(
            HISTORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if isinstance(
            data,
            list
        ):
            return data

    except Exception as error:

        print(
            "History load error:",
            error
        )

    return []


def save_history(
    history
):

    try:

        with open(
            HISTORY_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                history,
                file,
                indent=2,
                ensure_ascii=False
            )

        return True

    except Exception as error:

        print(
            "History save error:",
            error
        )

        return False


# ============================================================
# FILE VALIDATION
# ============================================================

def allowed_file(
    filename
):

    return (
        "." in filename
        and
        filename.rsplit(
            ".",
            1
        )[1].lower()
        in ALLOWED_EXTENSIONS
    )


# ============================================================
# JSON SAFE CONVERSION
# ============================================================

def make_json_safe(
    data
):

    if isinstance(
        data,
        np.ndarray
    ):
        return None

    if isinstance(
        data,
        np.integer
    ):
        return int(data)

    if isinstance(
        data,
        np.floating
    ):
        return float(data)

    if isinstance(
        data,
        np.bool_
    ):
        return bool(data)

    if isinstance(
        data,
        dict
    ):

        return {
            str(key):
                make_json_safe(value)
            for key, value in data.items()
        }

    if isinstance(
        data,
        list
    ):

        return [
            make_json_safe(item)
            for item in data
        ]

    if isinstance(
        data,
        tuple
    ):

        return [
            make_json_safe(item)
            for item in data
        ]

    if isinstance(
        data,
        set
    ):

        return [
            make_json_safe(item)
            for item in data
        ]

    return data


# ============================================================
# TEMPLATE USER CONTEXT
# ============================================================

@app.context_processor
def inject_user():

    return {
        "username":
            session.get(
                "username",
                "Project User"
            )
    }


# ============================================================
# LOGIN
# ============================================================

@app.route(
    "/",
    methods=["GET"]
)
def index():

    if session.get(
        "logged_in"
    ):

        return redirect(
            url_for("home")
        )

    return render_template(
        "login.html"
    )


@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    # --------------------------------------------------------
    # SHOW LOGIN PAGE
    # --------------------------------------------------------

    if request.method == "GET":

        if session.get(
            "logged_in"
        ):

            return redirect(
                url_for("home")
            )

        return render_template(
            "login.html"
        )


    # --------------------------------------------------------
    # PROCESS LOGIN
    # --------------------------------------------------------

    username = request.form.get(
        "username",
        ""
    ).strip()

    password = request.form.get(
        "password",
        ""
    )

    remember = (
        request.form.get(
            "remember"
        )
        == "on"
    )


    if not username or not password:

        return render_template(
            "login.html",
            error=(
                "Please enter "
                "username and password."
            )
        )


    session["logged_in"] = True
    session["username"] = username
    session["remember_me"] = remember


    if remember:

        session.permanent = True

    else:

        session.permanent = False


    return redirect(
        url_for("home")
    )


# ============================================================
# HOME
# ============================================================

@app.route(
    "/home"
)
def home():

    if not session.get(
        "logged_in"
    ):

        return redirect(
            url_for("login")
        )

    return render_template(
        "home.html"
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.route(
    "/dashboard"
)
def dashboard():

    if not session.get(
        "logged_in"
    ):

        return redirect(
            url_for("login")
        )

    return render_template(
        "dashboard.html"
    )


# ============================================================
# ANALYZE IMAGE
# ============================================================

@app.route(
    "/analyze-image"
)
def analyze_image_page():

    if not session.get(
        "logged_in"
    ):

        return redirect(
            url_for("login")
        )

    return render_template(
        "analyze_image.html"
    )


# ============================================================
# REPORTS
# ============================================================

@app.route(
    "/reports"
)
def reports():

    if not session.get(
        "logged_in"
    ):

        return redirect(
            url_for("login")
        )

    return render_template(
        "reports.html"
    )


# ============================================================
# ANALYSIS HISTORY
# ============================================================

@app.route(
    "/analysis-history"
)
def analysis_history():

    if not session.get(
        "logged_in"
    ):

        return redirect(
            url_for("login")
        )

    return render_template(
        "analysis_history.html"
    )


# Keep old URL working too
@app.route(
    "/history"
)
def history():

    return redirect(
        url_for(
            "analysis_history"
        )
    )


# ============================================================
# SETTINGS
# ============================================================

@app.route(
    "/settings"
)
def settings():

    if not session.get(
        "logged_in"
    ):

        return redirect(
            url_for("login")
        )

    return render_template(
        "settings.html"
    )


# ============================================================
# HELP
# ============================================================

@app.route(
    "/help"
)
def help_page():

    if not session.get(
        "logged_in"
    ):

        return redirect(
            url_for("login")
        )

    return render_template(
        "help.html"
    )


# ============================================================
# ACCOUNT API
# ============================================================

@app.route(
    "/api/account",
    methods=["GET"]
)
def get_account():

    if not session.get(
        "logged_in"
    ):

        return jsonify({
            "success": False,
            "error": "Not authenticated."
        }), 401


    return jsonify({

        "success": True,

        "username":
            session.get(
                "username",
                "Project User"
            )

    })


@app.route(
    "/api/account",
    methods=["POST"]
)
def update_account():

    if not session.get(
        "logged_in"
    ):

        return jsonify({
            "success": False,
            "error": "Not authenticated."
        }), 401


    data = request.get_json(
        silent=True
    ) or {}

    username = str(
        data.get(
            "username",
            ""
        )
    ).strip()


    if not username:

        return jsonify({
            "success": False,
            "error": "Username cannot be empty."
        }), 400


    session["username"] = username


    return jsonify({

        "success": True,

        "username":
            username,

        "message":
            "Account updated successfully."

    })


# ============================================================
# PASSWORD API
# ============================================================

@app.route(
    "/api/password",
    methods=["POST"]
)
def update_password():

    if not session.get(
        "logged_in"
    ):

        return jsonify({
            "success": False,
            "error": "Not authenticated."
        }), 401


    data = request.get_json(
        silent=True
    ) or {}


    current_password = str(
        data.get(
            "current_password",
            ""
        )
    )

    new_password = str(
        data.get(
            "new_password",
            ""
        )
    )


    if not current_password:

        return jsonify({
            "success": False,
            "error": "Current password is required."
        }), 400


    if not new_password:

        return jsonify({
            "success": False,
            "error": "New password is required."
        }), 400


    if len(new_password) < 4:

        return jsonify({
            "success": False,
            "error": (
                "New password must contain "
                "at least 4 characters."
            )
        }), 400


    # --------------------------------------------------------
    # Demo-project password handling
    #
    # The currently entered login password is kept in the
    # session for this local mini-project.
    # --------------------------------------------------------

    saved_password = session.get(
        "demo_password"
    )


    if saved_password is None:

        saved_password = (
            session.get(
                "login_password"
            )
        )


    if (
        saved_password is not None
        and
        current_password != saved_password
    ):

        return jsonify({
            "success": False,
            "error": "Current password is incorrect."
        }), 400


    session["demo_password"] = (
        new_password
    )

    session["login_password"] = (
        new_password
    )


    return jsonify({

        "success": True,

        "message":
            "Password updated successfully."

    })


# ============================================================
# SESSION API
# ============================================================

@app.route(
    "/api/session",
    methods=["GET"]
)
def get_session():

    if not session.get(
        "logged_in"
    ):

        return jsonify({
            "success": False,
            "error": "Not authenticated."
        }), 401


    return jsonify({

        "success": True,

        "status": "Active",

        "username":
            session.get(
                "username",
                "Project User"
            ),

        "remember_me":
            bool(
                session.get(
                    "remember_me",
                    False
                )
            )

    })


# ============================================================
# ANALYSIS HISTORY API
# ============================================================

@app.route(
    "/api/history",
    methods=["GET"]
)
def get_history():

    if not session.get(
        "logged_in"
    ):

        return jsonify({
            "success": False,
            "error": "Not authenticated."
        }), 401


    return jsonify({

        "success": True,

        "history":
            load_history()

    })


@app.route(
    "/api/history",
    methods=["DELETE"]
)
def delete_history():

    if not session.get(
        "logged_in"
    ):

        return jsonify({
            "success": False,
            "error": "Not authenticated."
        }), 401


    save_history([])


    return jsonify({

        "success": True,

        "message":
            "Analysis history cleared."

    })


@app.route(
    "/api/latest",
    methods=["GET"]
)
def get_latest():

    if not session.get(
        "logged_in"
    ):

        return jsonify({
            "success": False,
            "error": "Not authenticated."
        }), 401


    history = load_history()


    if not history:

        return jsonify({
            "success": True,
            "record": None
        })


    return jsonify({

        "success": True,

        "record":
            history[0]

    })


# ============================================================
# AI IMAGE ANALYSIS
# ============================================================

@app.route(
    "/analyze",
    methods=["POST"]
)
def analyze():

    if not session.get(
        "logged_in"
    ):

        return jsonify({
            "success": False,
            "error": (
                "Please sign in before "
                "analyzing an image."
            )
        }), 401


    if "image" not in request.files:

        return jsonify({
            "success": False,
            "error": "No image was uploaded."
        }), 400


    file = request.files["image"]


    if file.filename == "":

        return jsonify({
            "success": False,
            "error": "No image was selected."
        }), 400


    if not allowed_file(
        file.filename
    ):

        return jsonify({
            "success": False,
            "error": "Unsupported image format."
        }), 400


    filename = secure_filename(
        file.filename
    )


    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )


    file.save(
        filepath
    )


    print()
    print(
        "DroneRescue AI"
    )

    print(
        "Analyzing:",
        filename
    )


    try:

        # ----------------------------------------------------
        # RUN COMPLETE AI PIPELINE
        # ----------------------------------------------------

        result = analyze_drone_image(
            filepath
        )


        # ----------------------------------------------------
        # CONVERT TO JSON SAFE DATA
        # ----------------------------------------------------

        safe_result = make_json_safe(
            result
        )


        assessment = (
            safe_result.get(
                "assessment",
                {}
            )
        )


        vehicle_breakdown = (
            safe_result.get(
                "vehicle_breakdown",
                {}
            )
        )


        segmentation_image = (
            safe_result.get(
                "segmentation_image",
                ""
            )
        )


        pipeline = (
            safe_result.get(
                "pipeline",
                {}
            )
        )


        # ----------------------------------------------------
        # SAVE ANALYSIS HISTORY
        # ----------------------------------------------------

        history = load_history()


        record = {

            "filename":
                filename,

            "image_url":
                (
                    "/static/uploads/"
                    + filename
                ),

            "timestamp":
                __import__(
                    "datetime"
                ).datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

            "report":
                assessment,

            "vehicle_breakdown":
                vehicle_breakdown,

            "segmentation_image":
                segmentation_image,

            "pipeline":
                pipeline

        }


        history.insert(
            0,
            record
        )


        # Keep history manageable
        history = history[:50]


        save_history(
            history
        )


        print(
            "Analysis completed successfully."
        )


        # ----------------------------------------------------
        # IMPORTANT
        #
        # Keep the exact structure expected by
        # your working dashboard.js
        # ----------------------------------------------------

        return jsonify({

            "success": True,

            "result": safe_result,

            "assessment":
                assessment,

            "vehicle_breakdown":
                vehicle_breakdown,

            "segmentation_image":
                segmentation_image,

            "pipeline":
                pipeline

        })


    except Exception as error:

        print()
        print(
            "Analysis error:"
        )

        print(
            error
        )


        return jsonify({

            "success": False,

            "error":
                str(error)

        }), 500


# ============================================================
# LOGOUT
# ============================================================

@app.route(
    "/logout"
)
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )