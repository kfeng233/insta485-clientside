"""REST API for resources"""
import flask
import insta485


@insta485.app.route('/api/v1/')
def get_services():
    """Return a list of services available."""
    context = {
        "posts": "/api/v1/posts/",
        "comments": "/api/v1/comments/",
        "likes": "/api/v1/likes/",
        "url": "/api/v1/",
    }
    return flask.jsonify(**context)
