from src.admin import admin_bp
from flask import render_template
from src.users.users import User
from src.admin.dto.user_list_dto import UserListDto

@admin_bp.route('/users/list', methods = [ 'GET' ])
def list_users():
    users = User.query.filter_by(type='student').all()

    print(users)

    response = list()

    for user in users:
        print(user.status)
        response.append(
            UserListDto(user.email, f'{user.first_name} {user.last_name}', user.phone_number, "teste", user.status, user.get_initials()) 
        )

    return render_template('admin/users.html', user_list=response)