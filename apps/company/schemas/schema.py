import graphene
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required, permission_required
from apps.company.models import Company
from apps.company.permissions import is_company_administrator, is_company_administrator_or_invited_user
from apps.mail.tasks import send_email


class CompanyType(DjangoObjectType):
    class Meta:
        model = Company
        fields = "__all__"


class Query(graphene.ObjectType):
    get_company_by_id = graphene.Field(
        CompanyType, id=graphene.String(required=True)
    )
    get_companies_by_administrator_id = graphene.List(
        CompanyType, id=graphene.String(required=True)
    )
    get_companies_by_user_id = graphene.List(
        CompanyType, id=graphene.String(required=True)
    )
    get_company_filtered = graphene.List(CompanyType, name=graphene.String())

    @login_required
    @permission_required("company.view_company")
    def resolve_get_company_by_id(self, info, id):
        company = Company.objects.filter(id=id).first()
        is_company_administrator_or_invited_user(info.context.user, company)
        return company

    @login_required
    @permission_required("company.view_company")
    def resolve_get_companies_by_administrator_id(self, info, id):
        company = Company.objects.filter(administrator_id=id).order_by("-id")
        return company

    @login_required
    @permission_required("company.view_company")
    def resolve_get_companies_by_user_id(self, info, id):
        company = Company.objects.filter(invited_users__id=id).order_by("-id")
        return company

    @login_required
    @permission_required("company.view_company")
    def resolve_get_company_filtered(self, info, name=None):
        if name:
            company = Company.objects.filter(
                name__icontains=name,
                is_administrator=info.context.user
            ).order_by(
                "-id"
            )
        company = Company.objects.all().order_by("-id")
        return company


class CreateCompany(graphene.Mutation):
    company = graphene.Field(CompanyType)
    verification_message = graphene.String()

    class Arguments:
        name = graphene.String(required=True)
        site = graphene.String()

    def mutate(self, info, *args, **kwargs):
        name = kwargs.get("name")
        site = kwargs.get("site", "")
        administrator = info.context.user
        company = Company.objects.create(
            administrator=administrator, name=name, site=site
        )
        return CreateCompany(
            company=company,
            verification_message="Company has been created.",
        )


class UpdateCompany(graphene.Mutation):
    company = graphene.Field(CompanyType)
    verification_message = graphene.String()

    class Arguments:
        id = graphene.String(required=True)
        name = graphene.String(required=True)
        site = graphene.String()

    @permission_required("company.change_company")
    @login_required
    def mutate(self, info, *args, **kwargs):
        id = kwargs.get("id")
        name = kwargs.get("name")
        site = kwargs.get("site", "")
        administrator = info.context.user

        company = Company.objects.filter(id=id).first()
        is_company_administrator(administrator, company)
        if company:
            company.administrator = administrator
            company.name = name
            company.site = site
            company.save()
            verification_message = "Company has been updated."
        else:
            verification_message = "Company doesn't exist."
        return UpdateCompany(
            company=company, verification_message=verification_message
        )


class DeleteCompany(graphene.Mutation):
    verification_message = graphene.String()

    class Arguments:
        id = graphene.String(required=True)

    @permission_required("company.delete_company")
    @login_required
    def mutate(self, info, **kwargs):
        id = kwargs.get("id")
        company = Company.objects.filter(id=id).first()
        is_company_administrator(info.context.user, company)
        if company:
            company.delete()
            verification_message = "Company has been deleted."
        else:
            verification_message = "Company does not exist."
        return DeleteCompany(verification_message=verification_message)


class InviteUser(graphene.Mutation):
    verification_message = graphene.String()
    invited_users = graphene.List(graphene.String)

    class Arguments:
        id = graphene.String(required=True)
        email = graphene.String(required=True)
        first_name = graphene.String()
        last_name = graphene.String()
        permissions = graphene.List(graphene.String)

    @permission_required("company.change_company")
    @login_required
    def mutate(self, info, **kwargs):
        id = kwargs.get("id")
        first_name = kwargs.get("first_name", "")
        last_name = kwargs.get("last_name", "")
        email = kwargs.get("email")
        permissions = kwargs.get("permissions", [])
        company = Company.objects.filter(id=id).first()
        is_company_administrator(info.context.user, company)
        if company:
            user_exists = get_user_model().objects.filter(email=email).first()
            if user_exists:
                company.invited_users.add(user_exists)
                # Sent email to confirm the invite
                # TODO create old_user_invite_email
                # Add permissions to user
                user_exists.user_permissions.add(*permissions)
                send_email.delay(
                    "old_user_invite_email", user_exists, user_exists.email
                )
            else:
                # Create new user
                user = get_user_model().objects.create(
                    email=email,
                    username=email,
                    first_name=first_name,
                    last_name=last_name,
                )
                # Sent email to set password and confirm their invite
                # TODO create new_user_invite_email
                # Add permissions to user
                user.user_permissions.add(*permissions)
                send_email.delay("new_user_invite_email", user, user.email)
                company.invited_users.add(user)
            verification_message = (
                f"User with {email} has been invited to {company.name}."
            )
        else:
            verification_message = "Company does not exist."
        return InviteUser(verification_message=verification_message)


class Mutation(graphene.ObjectType):
    create_company = CreateCompany.Field()
    update_company = UpdateCompany.Field()
    delete_company = DeleteCompany.Field()
    invite_user = InviteUser.Field()
