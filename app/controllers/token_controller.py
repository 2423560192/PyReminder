from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services.token_service import get_tokens, add_token, delete_token, refresh_tokens

# 创建blueprint
token_bp = Blueprint('token', __name__)

@token_bp.route('/manage')
def manage_tokens():
    """息知API令牌管理页面"""
    # 重新从数据源加载最新tokens
    refresh_tokens()
    tokens = get_tokens()

    return render_template('manage_tokens.html', tokens=tokens)


@token_bp.route('/add_token', methods=['POST'])
def add_token_route():
    """添加或更新息知API令牌"""
    token_name = request.form.get('token_name', '').strip()
    token_value = request.form.get('token_value', '').strip()

    # 验证输入
    if not token_name:
        flash("账号名称不能为空", "danger")
        return redirect(url_for('token.manage_tokens'))

    if not token_value or not token_value.startswith('XZ'):
        flash("息知令牌格式不正确，应以XZ开头", "danger")
        return redirect(url_for('token.manage_tokens'))

    # 检查是否已存在同名账号
    tokens = get_tokens()
    is_new = token_name not in tokens

    # 保存Token
    if add_token(token_name, token_value):
        if is_new:
            flash(f"已添加新通知账号「{token_name}」", "success")
        else:
            flash(f"已更新通知账号「{token_name}」的令牌", "success")
    else:
        flash(f"保存账号失败，请检查数据库连接", "danger")

    return redirect(url_for('token.manage_tokens'))


@token_bp.route('/delete_token/<token_name>', methods=['POST'])
def delete_token_route(token_name):
    """删除息知API令牌"""
    # 不允许删除"默认"账号
    if token_name == '默认':
        flash("不能删除默认通知账号", "danger")
        return redirect(url_for('token.manage_tokens'))

    # 从字典中删除
    tokens = get_tokens()
    if token_name in tokens:
        if delete_token(token_name):
            flash(f"已删除通知账号「{token_name}」", "success")
        else:
            flash(f"删除账号失败，请检查数据库连接", "danger")
    else:
        flash(f"通知账号「{token_name}」不存在", "warning")

    return redirect(url_for('token.manage_tokens')) 