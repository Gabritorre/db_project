import enum as py_enum
from datetime import datetime
from sqlalchemy import Boolean,Float, Integer, LargeBinary, String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# varchars lengths
A_LENGTH = 20
B_LENGTH = 40
C_LENGTH = 60

# CREATE TYPE SexEnum AS ENUM ('male', 'female', 'other')
class SexEnum(py_enum.Enum):
	MALE = "male"
	FEMALE = "female"
	OTHER = "other"

class RelationEnum(py_enum.Enum):
	FOLLOWER = 'follower'
	FOLLOWING = 'following'

class Base(DeclarativeBase):
	pass


class Profile(Base):
	__tablename__ = "profiles"
	id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)

	password: Mapped[str] = mapped_column(nullable=False)
	email: Mapped[str] = mapped_column(nullable=True, unique=True)
	creation_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)



# --- Advertisers ---
class Advertiser(Base):
	__tablename__ = "advertisers"
	id: Mapped[int] = mapped_column(ForeignKey("profiles.id",  ondelete="cascade"), primary_key=True)

	company_handle: Mapped[str] = mapped_column(String(A_LENGTH), nullable=False, unique=True)
	name: Mapped[str] = mapped_column(String(A_LENGTH), nullable=False)
	industry: Mapped[str] = mapped_column(String(A_LENGTH), nullable=False)

	profile: Mapped[Profile] = relationship(backref="profiles", passive_deletes=True)



class AdCampaign(Base):
	__tablename__ = "ad_campaigns"
	id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
	advertiser_id: Mapped[int] = mapped_column(ForeignKey("advertisers.id", ondelete="cascade"))

	name: Mapped[str] = mapped_column(String(A_LENGTH), nullable=False)
	budget: Mapped[float] = mapped_column(Float, nullable=False)
	start: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
	end: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

	advertiser: Mapped[Advertiser] = relationship(backref="advertisers", passive_deletes=True)



class Ad(Base):
	__tablename__ = "ads"
	id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
	ad_campaign_id: Mapped[int] = mapped_column(ForeignKey("ad_campaigns.id", ondelete="cascade"))

	body: Mapped[str] = mapped_column(Text, nullable=True) # aggiungere vincolo (body || media)
	media: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)
	link: Mapped[str] = mapped_column(String(C_LENGTH), nullable=True)
	probability: Mapped[float] = mapped_column(Float, nullable=False)

	ad_campaign: Mapped[AdCampaign] = relationship(backref="ad_campaigns", passive_deletes=True)



class DailyStat(Base):
	__tablename__ = "daily_stats"
	ad_id: Mapped[int] = mapped_column(ForeignKey("ads.id", ondelete="cascade"), primary_key=True)
	date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), primary_key=True)

	impressions: Mapped[int] = mapped_column(Integer)
	readings: Mapped[int] = mapped_column(Integer)
	clicks: Mapped[int] = mapped_column(Integer)

	ad: Mapped[Ad] = relationship(backref="ads", passive_deletes=True)



class TargettedTag(Base):
	__tablename__ = "targetted_tags"
	ad_id: Mapped[int] = mapped_column(ForeignKey("ads.id", ondelete="cascade"), primary_key=True)
	tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("tags.id", ondelete="cascade"), primary_key=True)

	ad: Mapped[Ad] = relationship(backref="ads", passive_deletes=True)
	tag: Mapped[Ad] = relationship(backref="tags", passive_deletes=True)
# ------



class Tag(Base):
	__tablename__ = "tags"
	id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)

	tag: Mapped[str] = mapped_column(String(A_LENGTH), unique=True, nullable=False)



# --- Users ---
class User(Base):
	__tablename__ = "users"
	id: Mapped[int] = mapped_column(ForeignKey("profiles.id", ondelete="cascade"), primary_key=True)

	user_handle: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
	name: Mapped[str] = mapped_column(String(20), nullable=False)
	surname: Mapped[str] = mapped_column(String(20), nullable=False)
	sex: Mapped[SexEnum]
	pfp: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)
	banner: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)
	biography: Mapped[str] = mapped_column(Text, nullable=True)
	followers: Mapped[int] = mapped_column(Integer, nullable=False)
	following: Mapped[int] = mapped_column(Integer, nullable=False)

	profile: Mapped[Profile] = relationship(backref="profiles", passive_deletes=True)



class Interest(Base):
	__tablename__ = "interests"
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="cascade"), primary_key=True)
	tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id", ondelete="cascade"), primary_key=True)

	interest: Mapped[float] = mapped_column(Float, nullable=False)

	user: Mapped[User] = relationship(backref="users", passive_deletes=True)
	tag: Mapped[Tag] = relationship(backref="tags", passive_deletes=True)



class AuthToken(Base):
	__tablename__ = "auth_tokens"
	id: Mapped[str] = mapped_column(String(B_LENGTH), primary_key=True)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="cascade"))

	expiration_date: Mapped[datetime] = mapped_column(DateTime(timezone=False))

	user: Mapped[User] = relationship(backref="users", passive_deletes=True)



class Post(Base):
	__tablename__ = "posts"
	id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
	user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="cascade"))

	body: Mapped[str] = mapped_column(Text, nullable=True) # aggiungere vincolo (body || media)
	media: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)
	date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
	likes: Mapped[int] = mapped_column(Integer, nullable=False)

	user: Mapped[User] = relationship(backref="users", passive_deletes=True)



class PostTag(Base):
	__tablename__ = "post_tags"
	post_id: Mapped[int] = mapped_column(Integer, ForeignKey("posts.id", ondelete="cascade"), primary_key=True)
	tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id", ondelete="cascade"), primary_key=True)

	post: Mapped[Post] = relationship(backref="posts", passive_deletes=True)
	tag: Mapped[Tag] = relationship(backref="tags", passive_deletes=True)



class UserInteraction(Base):
	__tablename__ = "user_interactions"
	user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)
	post_id: Mapped[int] = mapped_column(Integer, ForeignKey("posts.id"), primary_key=True)

	liked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
	comment: Mapped[str] = mapped_column(Text, nullable=True)

	user: Mapped[User] = relationship(backref="users", passive_deletes=True)



class RelationShip(Base):
	__tablename__ = "relationships"
	user1_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)
	user2_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)
	relation: Mapped[RelationEnum]

	user1: Mapped[User] = relationship(backref="users", primaryjoin="user1_id == users.id", passive_deletes=True)
	user2: Mapped[User] = relationship(backref="users", primaryjoin="user2_id == users.id", passive_deletes=True)
