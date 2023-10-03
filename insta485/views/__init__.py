"""Views, one for each Insta485 page."""
from insta485.views.index import show_index, get_users_data, \
    get_posts_data, get_likes_data, get_comments_data
from insta485.views.accounts import create, login, logout, delete, edit, \
    password, auth, accounts
from insta485.views.likes import likes
from insta485.views.comments import comments
from insta485.views.users import show_users, follow_user, followers, following
from insta485.views.posts import show_post
from insta485.views.explore import explore
