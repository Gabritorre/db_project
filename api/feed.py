from flask import Blueprint, jsonify, request
from sqlalchemy.sql.expression import func
from config import db, safeguard
from models import Ad, Post, Following, Like, User
from schemas import posts_schema, feed_ad_schema
from .utils import get_auth_token, recommend_ad

feed = Blueprint("feed", __name__, url_prefix="/feed")

POSTS_PER_CHUNK = 6

@feed.route("/explore", methods=["POST"])
@safeguard
def explore():
	token = get_auth_token(request.cookies)
	req = request.get_json()
	last_post_id = req["last_post_id"]
	if last_post_id:
		posts = db.session.query(Post).where(Post.id < last_post_id).order_by(Post.id.desc())
	else:
		posts = db.session.query(Post).order_by(Post.id.desc())
	posts = posts.limit(POSTS_PER_CHUNK)
	posts_data = posts_schema.dump(posts)

	# for each post check if the user liked it or not
	if token:
		for count, post in enumerate(posts):
			posts_data[count]["user_like"] = bool(db.session.query(Like).where(Like.post_id == post.id, Like.user_id == token.profile_id).count())
		recommended_ad = recommend_ad(token.profile_id, 0.8)
	else:
		recommended_ad = db.session.query(Ad).order_by(func.random()).first() # random ad if not logged in
	return jsonify({"error": None, "posts": posts_data, "ad": feed_ad_schema.dump(recommended_ad)})



@feed.route("/friends", methods=["POST"])
@safeguard
def friends_posts():
	token = get_auth_token(request.cookies)
	if not token:
		return jsonify({"error": "Invalid token"})

	followings = db.session.query(Following).where(Following.follower == token.profile_id).all()
	friends_ids = [following.followed for following in followings]

	req = request.get_json()
	last_post_id = req["last_post_id"]
	if last_post_id:
		posts = db.session.query(Post).where(Post.user_id.in_(friends_ids), Post.id < last_post_id).order_by(Post.id.desc())
	else:
		posts = db.session.query(Post).where(Post.user_id.in_(friends_ids)).order_by(Post.id.desc())
	posts = posts.limit(POSTS_PER_CHUNK)
	data = posts_schema.dump(posts)

	# for each post check if the user liked it or not
	for count, post in enumerate(posts):
		data[count]['user_like'] = bool(db.session.query(Like).where(Like.post_id == post.id, Like.user_id == token.profile_id).count())

	return jsonify({"error": None, "posts": data})


@feed.route("/user", methods=["POST"])
@safeguard
def user_posts():
	token = get_auth_token(request.cookies)
	req = request.get_json()
	user_id = req["id"]

	if not db.session.query(User).where(User.id == user_id).first():
		return jsonify({"error": "User not found"})
	posts = db.session.query(Post).where(Post.user_id == user_id).order_by(Post.id.desc()).all()
	data = posts_schema.dump(posts)

	# for each post check if the user liked it or not
	if token:
		for count, post in enumerate(posts):
			data[count]['user_like'] = bool(db.session.query(Like).where(Like.post_id == post.id, Like.user_id == token.profile_id).count())

	return jsonify({"error": None, "posts": data})
