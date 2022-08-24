from apps.company.models import Company
from apps.mail.tasks import send_email
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model
from graphene_django_extras import DjangoFilterPaginateListField, LimitOffsetGraphqlPagination
import graphene


class CompanySearchType(DjangoObjectType):
    class Meta:
        model = Company
        fields = ['id', 'administrator', 'invited_users', 'name', 'site']
        filter_fields = {
            "name": ["icontains"],
        }
            
            
class CompanyType(DjangoObjectType):
    class Meta:
        model = Company
        fields = ['id', 'administrator', 'invited_users', 'name', 'site']


class CompanyQuery(graphene.ObjectType):
    get_company_by_id = graphene.Field(CompanyType, id=graphene.String(required=True))
    get_companies_by_administrator_id = graphene.List(CompanyType, id=graphene.String(required=True))
    get_companies_by_user_id = graphene.List(CompanyType, id=graphene.String(required=True))
    search_company = DjangoFilterPaginateListField(CompanySearchType, pagination=LimitOffsetGraphqlPagination())

    def resolve_get_company_by_id(self, info, id):
        return Company.objects.filter(id=id)

    def resolve_get_companies_by_administrator_id(self, info, id):
        return Company.objects.filter(administrator_id=id).order_by('-id')

    def resolve_get_companies_by_user_id(self, info, id):
        return Company.objects.filter(invited_users__id=id).order_by('-id')


class CreateCompany(graphene.Mutation):
    company = graphene.Field(CompanyType)
    message = graphene.String()

    class Arguments:
        name = graphene.String(required=True)
        site = graphene.String()

    def mutate(self, info, *args, **kwargs):
        name = kwargs.get('name')
        site = kwargs.get('site', '')
        administrator = info.context.user
        company = Company.objects.create(
            administrator=administrator,
            name=name,
            site=site
        )
        return CreateCompany(company=company, message="Company has been created.")


class UpdateCompany(graphene.Mutation):
    company = graphene.Field(CompanyType)
    message = graphene.String()

    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String(required=True)
        site = graphene.String()

    def mutate(self, info, *args, **kwargs):
        name = kwargs.get('name')
        site = kwargs.get('site', '')
        administrator = info.context.user

        company = Company.objects.filter(id=id).first()
        if company:
            company.administrator = administrator
            company.name = name
            company.site = site
            company.save()
            message = "Company has been updated."
        else:
            message = "Company doesn\'t exist."
        return UpdateCompany(company=company, message=message)


class DeleteCompany(graphene.Mutation):
    message = graphene.String()

    class Arguments:
        id = graphene.Int(required=True)

    def mutate(self, info, id):
        company = Company.objects.filter(id=id).first()
        if company:
            company.delete()
            message = "Company has been deleted."
        else:
            message = "Company does not exist."
        return DeleteCompany(message=message)


class InviteUser(graphene.Mutation):
    message = graphene.String()
    invited_users = graphene.List(graphene.String)

    class Arguments:
        id = graphene.Int(required=True)
        email = graphene.String(required=True)
        first_name = graphene.String()
        last_name = graphene.String()
        permissions = graphene.List(graphene.String)

    def mutate(self, info, **kwargs):
        id = kwargs.get('id')
        first_name = kwargs.get('first_name', '')
        last_name = kwargs.get('last_name', '')
        email = kwargs.get('email')
        permissions = kwargs.get('permissions', [])
        company = Company.objects.filter(id=id).first()
        if company:
            user_exists = get_user_model().objects.filter(email=email).first()
            if user_exists:
                company.invited_users.add(user_exists)
                # Sent email to confirm the invite
                # TODO create old_user_invite_email
                # Add permissions to user
                user_exists.permissions.add(*permissions)
                send_email.delay("old_user_invite_email", user_exists, user_exists.email)
            else:
                # Create new user
                user = get_user_model().objects.create(email=email, username=email, first_name=first_name, last_name=last_name)
                # Sent email to set password and confirm their invite
                # TODO create new_user_invite_email
                # Add permissions to user
                user.permissions.add(*permissions)
                send_email.delay("new_user_invite_email", user_exists, user_exists.email)
                company.invited_users.add(user)
            message = f"User with {email} has been invited to {company.name}."
        else:
            message = "Company does not exist."
        return InviteUser(message=message)


class Mutation(graphene.ObjectType):
    create_company = CreateCompany.Field()
    update_company = UpdateCompany.Field()
    delete_company = DeleteCompany.Field()
    invite_user = InviteUser.Field()
