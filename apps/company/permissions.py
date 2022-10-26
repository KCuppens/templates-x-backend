from django.core.exceptions import PermissionDenied


def is_company_administrator(user, company):
    if not user == company.administrator:
        raise PermissionDenied("You are not the company administrator.")


def is_company_invited_users(user, company):
    if user not in company.invited_users.all():
        raise PermissionDenied("You are not invited to this company.")


def is_company_administrator_or_invited_user(user, company):
    print(not user == company.administrator)
    print(user not in company.invited_users.all())
    if (
        not user == company.administrator
        and
        user not in company.invited_users.all()
    ):
        raise PermissionDenied("You are not the company administrator or invited user.")