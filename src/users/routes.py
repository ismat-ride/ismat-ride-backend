from src.users import users_bp

@users_bp.route("/")
def test():
    return "<h1>Main user endpoint<h1>"