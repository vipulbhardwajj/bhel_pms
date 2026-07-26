from app.extensions import db

user_projects = db.Table(
    "user_projects",

    db.Column(
        "user_id",
        db.Integer,
        db.ForeignKey("users.id"),
        primary_key=True
    ),

    db.Column(
        "project_id",
        db.Integer,
        db.ForeignKey("projects.id"),
        primary_key=True
    )
)