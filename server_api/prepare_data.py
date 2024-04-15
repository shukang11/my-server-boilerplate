# 准备一些数据
import os
from typing import Dict, Optional

from fastapi import FastAPI

from server_core.authentication import DEF_PERMISSIONS, DEF_ROLES
from server_core.database import Session


def __prepare_permission_data(session: Session) -> Dict[str, Optional[str]]:
    from server_core.authentication.permission import (create_permission, create_role,
                                                       update_role_permissions)

    # 初始化权限
    perm_map_id: Dict[str, int] = {}
    for perm in DEF_PERMISSIONS.all_permissions():
        p = create_permission(
            session=session,
            identifier=perm,
            name=DEF_PERMISSIONS.get_name_of_permission(perm),
            remark="",
        )
        perm_map_id.update({perm: p.id})
    session.commit()

    # 初始化角色
    for role in DEF_ROLES.all_roles():
        r = create_role(
            session=session, identifier=role, name=DEF_ROLES.get_name_of_role(role)
        )
        session.commit()
        permissions = DEF_ROLES.get_permissions_of_role(role)
        # 从 perm_map_id 中获取权限的 id
        permission_ids = [perm_map_id.get(p) for p in permissions]
        _ = update_role_permissions(
            session=session,
            role_id=r.id,
            pendding_permission_ids=permission_ids,
            action="add",
        )


def __prepare_admin_user(session: Session) -> None:
    from server_core.authentication import AuthController, CreateUserReq
    from server_core.authentication.permission import grant_user_role
    from server_core.database import RoleInDB, UserInDB
    from server_core.utils import getmd5

    admin_role_idf = DEF_ROLES.ROLE_SUPER_ADMIN
    admin_role = session.query(RoleInDB).filter_by(identifier=admin_role_idf).first()
    if admin_role is None:
        raise ValueError("未找到超级管理员角色")
    username = os.getenv("SUPER_ADMIN_USERNAME", "admin")
    password = os.getenv("SUPER_ADMIN_PASSWORD", "admin")
    phone = os.getenv("SUPER_ADMIN_PHONE", "")
    admin = UserInDB.find_by_username(session=session, username=username)
    if not admin:
        req = CreateUserReq(
            username=username, phone=phone, password_hash=getmd5(password)
        )
        handler = AuthController(session=session)
        handler.skip_permission_check = True
        admin = handler.create_user(req=req)
        _ = grant_user_role(session=session, admin_id=admin.id, role_id=admin_role.id)


def init_app(app: FastAPI) -> None:
    from server_core.database._session import SessionLocal

    with SessionLocal() as session:
        # 准备权限数据
        __prepare_permission_data(session)
        # 准备超级管理员
        __prepare_admin_user(session)

    print("初始化数据完成")
    return None
