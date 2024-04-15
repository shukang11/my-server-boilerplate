import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Union

from jose import JWTError, jwt

from server_core.database import Session, UserInDB, UserTokenInDB

from .error import AuthenticationException
from .permission import PermissionOpProtocol
from .schema import AuthClaims, CreateUserReq, LoginReq, LoginResp, UserModel

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = os.getenv("JWT_SALT")
ALGORITHM = os.getenv("JWT_ALGORITHM")


# 创建 token
def create_access_token(
    claims: AuthClaims, expires_delta: Union[timedelta, None] = None
):
    to_encode = claims.model_dump()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


class AuthController(PermissionOpProtocol):
    def __init__(self, session: Session, user_id: Optional[int] = None) -> None:
        self.user_id = user_id
        self.session = session

    def create_user(self, req: CreateUserReq) -> UserModel:
        # find user if exists
        user_exists = UserInDB.find_by_username(
            session=self.session, username=req.username
        )
        if user_exists:
            return UserModel.from_db(user_exists)
        # create user
        user = UserInDB(
            username=req.username,
            phone=req.phone,
            email=req.email,
            password=req.password_hash,
        )
        user.add(session=self.session, commit=True)
        return UserModel.from_db(user)

    def login_user(self, req: LoginReq) -> Optional[LoginResp]:
        # find user if exists
        user = UserInDB.find_by_username(session=self.session, username=req.username)
        if not user:
            raise AuthenticationException("user not exists")
        # compare password
        if req.password != user.password:
            raise AuthenticationException("password error")

        # create token
        token_raw = user.token(salt=SECRET_KEY)
        # find token if exists
        user_token = (
            self.session.query(UserTokenInDB).filter_by(customer_id=user.id).first()
        )
        if not user_token:
            user_token = UserTokenInDB(customer_id=user.id, token=token_raw)
        user_token.add(session=self.session)

        jwt_exp = int(os.getenv("JWT_EXP") or 2592000)
        token = create_access_token(
            AuthClaims(
                sub=user_token.token, exp=datetime.now() + timedelta(seconds=jwt_exp)
            )
        )
        return LoginResp(token=token)

    @staticmethod
    def get_current_user(session: Session, jwt_token: str) -> Optional[UserModel]:
        """
        根据提供的令牌获取当前客户。

        Args:
            session (Session): 数据库会话。
            jwt_token (str): 认证令牌。

        Returns:
            Optional[UserModel]: 如果找到当前客户，则返回该客户；否则返回 None。
        """
        user: Optional[UserInDB] = None
        try:
            payload = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
            token: str = payload.get("sub")
            if token is None:
                raise AuthenticationException("Could not validate credentials")

            user = UserInDB.find_by_token(session=session, token=token)
        except JWTError:
            raise AuthenticationException("Could not validate credentials")

        if user is None:
            raise AuthenticationException("Could not validate credentials")

        return UserModel.from_db(user)
