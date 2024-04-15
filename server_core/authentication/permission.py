from typing import Dict, List, Literal, Optional, Protocol, runtime_checkable

from server_core.database import (PermissionInDB, PermissionRoleInDB, RoleInDB, Session,
                                  UserRoleInDB)

from .error import PermissionException


# === 角色标识符 ===
class DEF_ROLES:
    # 超级管理员
    ROLE_SUPER_ADMIN = "role.super.admin"

    @classmethod
    def all_roles(cls) -> list[str]:
        return [cls.ROLE_SUPER_ADMIN]

    @classmethod
    def get_name_of_role(cls, role: str) -> str:
        names = {
            cls.ROLE_SUPER_ADMIN: "超级管理员",
        }
        return names.get(role, "未知角色")

    @classmethod
    def get_permissions_of_role(cls, role: str) -> list[str]:
        permissions: Dict[str, List[str]] = {
            cls.ROLE_SUPER_ADMIN: DEF_PERMISSIONS.all_permissions(),
        }
        return permissions.get(role, [])


class DEF_PERMISSIONS:
    # === 关于子账户的权限 ==
    # 创建子账户
    PERMISSION_CREATE_SUB_ADMIN = "com.sub.admin.create"

    @classmethod
    def all_permissions(cls) -> list[str]:
        return [
            cls.PERMISSION_CREATE_SUB_ADMIN,
        ]

    @classmethod
    def get_name_of_permission(cls, permission: str) -> str:
        names = {
            cls.PERMISSION_CREATE_SUB_ADMIN: "创建子账户",
        }
        return names.get(permission, "未知权限")


# 创建权限
def create_permission(
    session: Session, identifier: str, name: str, remark: Optional[str] = None
) -> PermissionInDB:
    # 查询权限是否存在
    is_exist = (
        session.query(PermissionInDB)
        .filter(PermissionInDB.identifier == identifier)
        .first()
    )
    if is_exist:
        return is_exist
    permission = PermissionInDB(
        identifier=identifier, permission_name=name, remark=remark
    )
    permission.add(session=session)
    return permission


# 创建一个角色
def create_role(session: Session, identifier: str, name: str) -> RoleInDB:
    # 查询角色是否存在
    is_exist = session.query(RoleInDB).filter(RoleInDB.identifier == identifier).first()
    if is_exist:
        return is_exist
    role = RoleInDB(identifier=identifier, role_name=name)
    role.add(session=session)
    return role


# 获取用户角色
def get_user_role(session: Session, user_id: int) -> List[RoleInDB]:
    # RoleInDB join UserRoleInDB
    roles = (
        session.query(RoleInDB)
        .join(UserRoleInDB, UserRoleInDB.role_id == RoleInDB.id)
        .filter(UserRoleInDB.user_id == user_id)
        .all()
    )
    return roles


def grant_user_role(session: Session, admin_id: int, role_id: int) -> UserRoleInDB:
    # 赋予某一个用户的角色
    is_exist = (
        session.query(UserRoleInDB)
        .filter(UserRoleInDB.user_id == admin_id, UserRoleInDB.role_id == role_id)
        .first()
    )
    if is_exist:
        return is_exist
    user_role = UserRoleInDB(user_id=admin_id, role_id=role_id)
    user_role.add(session=session)
    return user_role


def revoke_user_role(session: Session, admin_id: int, role_id: int) -> UserRoleInDB:
    # 移除某一个用户的角色
    user_role = (
        session.query(UserRoleInDB)
        .filter(UserRoleInDB.user_id == admin_id, UserRoleInDB.role_id == role_id)
        .first()
    )
    if not user_role:
        raise ValueError("user role not exists")
    session.delete(user_role)
    return user_role


def update_role_permissions(
    session: Session,
    role_id: int,
    pendding_permission_ids: List[int],
    action: Literal["add", "remove"] = "add",
) -> List[PermissionRoleInDB]:
    # pendding_permission_ids 不能为空，不能包含空
    if not pendding_permission_ids:
        raise ValueError("permission ids can not be empty")
    pendding_permission_ids = list(set(pendding_permission_ids))
    pendding_permission_ids = [p for p in pendding_permission_ids if p]
    if not pendding_permission_ids:
        raise ValueError("permission ids can not be empty")
    # 更新角色的权限 / 新增 / 删除
    permissions = []
    for permission_id in pendding_permission_ids:
        if action == "add":
            is_exist = (
                session.query(PermissionRoleInDB)
                .filter(
                    PermissionRoleInDB.role_id == role_id,
                    PermissionRoleInDB.permission_id == permission_id,
                )
                .first()
            )
            if is_exist:
                continue

            permission = PermissionRoleInDB(
                role_id=role_id, permission_id=permission_id
            )
            permission.add(session=session)
            permissions.append(permission)
        elif action == "remove":
            permission = (
                session.query(PermissionRoleInDB)
                .filter(
                    PermissionRoleInDB.role_id == role_id,
                    PermissionRoleInDB.permission_id == permission_id,
                )
                .first()
            )
            if permission:
                session.delete(permission)
                permissions.append(permission)
    session.commit()
    return permissions


# 获取用户权限
def get_user_permissions(session: Session, user_id: int) -> List[PermissionInDB]:
    # RoleInDB join UserRoleInDB join PermissionRoleInDB
    permissions = (
        session.query(PermissionInDB)
        .join(PermissionRoleInDB, PermissionRoleInDB.role_id == RoleInDB.id)
        .join(UserRoleInDB, UserRoleInDB.role_id == RoleInDB.id)
        .filter(UserRoleInDB.user_id == user_id)
        .all()
    )
    return permissions


# 判断用户是否有权限
def user_has_permission(session: Session, user_id: int, permission: str) -> bool:
    # RoleInDB join UserRoleInDB join PermissionRoleInDB
    permissions = get_user_permissions(session=session, user_id=user_id)
    for p in permissions:
        if p.permission_name == permission:
            return True
    return False


@runtime_checkable
class PermissionOpProtocol(Protocol):
    user_id: int
    session: Session
    skip_permission_check: bool = False


# 装饰器方法来判断权限
def permission_required(permission: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            self = args[0]
            if not isinstance(self, PermissionOpProtocol):
                raise TypeError("self must implement PermissionOpProtocol")
            session = self.session
            user_id = self.user_id
            if not self.skip_permission_check:
                if not user_has_permission(
                    session=session, user_id=user_id, permission=permission
                ):
                    raise PermissionException("permission denied")
            return func(*args, **kwargs)

        return wrapper

    return decorator
