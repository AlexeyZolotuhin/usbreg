from app.api.v1 import bp
from app.models import Department
import json
from app.api.v1.auth import token_auth


@bp.route('/department/all', methods=["GET"])
@token_auth.login_required
def get_departments_all():
    all_departments = {dep.id: dep.name for dep in Department.query.order_by('name').all()}
    return json.dumps(all_departments, ensure_ascii=False).encode('utf8')
