import graphene
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.models import Group, Permission
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from graphql_jwt.utils import jwt_encode, jwt_payload
from graphql_jwt.decorators import login_required

from apps.company.models import Company
from apps.mail.tasks import send_email
from apps.users.utils import decode_token

User = get_user_model()


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = "__all__"


class GroupType(DjangoObjectType):
    class Meta:
        model = Group
        fields = "__all__"


class PermissionType(DjangoObjectType):
    class Meta:
        model = Permission
        fields = "__all__"


class Query(graphene.ObjectType):
    get_invited_users = graphene.List(
        UserType,
        id=graphene.String(required=True)
    )
    get_user_detail = graphene.Field(UserType, id=graphene.String())
    get_company_permission_groups = graphene.List(
        GroupType, id=graphene.String(required=True)
    )
    get_permissions_for_company = graphene.List(
        PermissionType, id=graphene.String(required=True)
    )
    get_group_users = graphene.List(
        UserType,
        id=graphene.String(required=True)
    )

    @login_required
    def resolve_get_invited_users(self, info, id):
        company = Company.objects.filter(id=id).first()
        if company:
            return company.invited_users.all()
        return []

    @login_required
    def resolve_get_user_detail(self, info, id):
        return User.objects.filter(id=id).first()

    @login_required
    def resolve_get_company_permission_groups(self, info, id):
        return Group.objects.filter(company_id=id)

    @login_required
    def resolve_get_permissions_for_company(self, info, id):
        return Permission.objects.filter(company__id=id)

    @login_required
    def resolve_get_group_users(self, info, id):
        return User.objects.filter(groups__id=id)


class RegisterUser(graphene.Mutation):
    user = graphene.Field(UserType)
    verification_message = graphene.String()

    class Arguments:
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, **kwargs):
        first_name = kwargs.get("first_name")
        last_name = kwargs.get("last_name")
        password = kwargs.get("password")
        email = kwargs.get("email")
        user = get_user_model().objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            is_administrator=True,
        )
        user.set_password(password)
        user.save()
        verification_message = f"Successfully created user, {user}"

        activation_link = user.get_activation_link()
        # TODO create send_activation_email email
        send_email.delay(
            "send_activation_email",
            str(user),
            user.email,
            {"{activation_link}": activation_link},
        )
        return RegisterUser(
            user=user,
            verification_message=verification_message
        )


class ActivateUser(graphene.Mutation):
    user = graphene.Field(UserType)
    verification_message = graphene.String()

    class Arguments:
        uid = graphene.String(required=True)
        token = graphene.String(required=True)

    def mutate(self, info, **kwargs):
        uid = kwargs.get("uid")
        token = kwargs.get("token")
        check, user = decode_token(uid, token)
        if check:
            user.is_active = True
            user.save(update_fields=["is_active"])
            verification_message = "The user has been activated."
        else:
            verification_message = "The user is already activated."
        return ActivateUser(
            user=user,
            verification_message=verification_message
        )


class LoginUser(graphene.Mutation):
    user = graphene.Field(UserType)
    verification_message = graphene.String()
    token = graphene.String()

    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, **kwargs):
        email = kwargs.get("email")
        password = kwargs.get("password")

        if info.context.user.is_authenticated:
            raise GraphQLError("The user is already logged in.")

        user = authenticate(username=email, password=password)
        print(user)
        if user:
            login(info.context, user)
            payload = jwt_payload(user)
            token = jwt_encode(payload)
            verification_message = "You logged in successfully."
            return LoginUser(
                user=user,
                token=token,
                verification_message=verification_message
            )
        else:
            user_exists = User.objects.get(email=email)
            if user_exists.is_active:
                verification_message = "Invalid login credentials."
                raise GraphQLError(verification_message=verification_message)
            else:
                verification_message = "Your email is not verified."
                raise GraphQLError(verification_message=verification_message)


class LogoutUser(graphene.Mutation):
    verification_message = graphene.String()
    is_logged_out = graphene.Boolean()

    @login_required
    def mutate(self, info, **kwargs):
        if not info.context.user.is_authenticated:
            raise GraphQLError("No user is logged in")
        logout(info.context)
        return LogoutUser(
            is_logged_out=True,
            verification_message="User successfully logged out!"
        )


class ResetPassword(graphene.Mutation):
    reset_link = graphene.String()
    verification_message = graphene.String()

    class Arguments:
        email = graphene.String(required=True)

    def mutate(self, info, email):
        if email.strip() == "":
            raise GraphQLError(info.context, "Email can't be blank.")

        user = User.objects.filter(email=email).first()
        if user is None:
            raise GraphQLError(
                info.context, "User with the provided email was not found."
            )

        password_reset_link = user.get_password_reset_link()

        # TODO create reset_password_email
        send_email.delay(
            "reset_password_email",
            str(user),
            user.email,
            {"{password_reset_link}": password_reset_link},
        )
        return ResetPassword(
            reset_link=password_reset_link,
            verification_message="A password reset link was"
            " sent to your email address.",
        )


class ResetPasswordConfirm(graphene.Mutation):
    verification_message = graphene.String()
    is_valid = graphene.Boolean()

    class Arguments:
        uidb64 = graphene.String()
        token = graphene.String()
        password = graphene.String(required=True)

    def mutate(self, info, **kwargs):
        uidb64 = kwargs.get("uidb64")
        token = kwargs.get("token")
        password = kwargs.get("password")

        check, user = decode_token(uidb64, token)
        if check and user:
            user.set_password(password)
            user.save()
        return ResetPasswordConfirm(
            is_valid=False,
            verification_message="Password has been succesfully resetted.",
        )


class CreateGroup(graphene.Mutation):
    group = graphene.Field(GroupType)
    verification_message = graphene.String()

    class Arguments:
        company = graphene.String(required=True)
        name = graphene.String(required=True)
        permission = graphene.List(graphene.String)

    @login_required
    def mutate(self, info, **kwargs):
        name = kwargs.get("name")
        company = kwargs.get("company")
        permissions = kwargs.get("permission", [])

        group = Group.objects.create(name=name, company_id=company)
        group.edited_by = info.context.user
        group.save(update_fields=["edited_by"])

        permissions = Permission.objects.filter(pk__in=permissions)
        for id_ in list(permissions.values_list("id", flat=True)):
            group.permissions.add(int(id_))

        return CreateGroup(
            group=group, verification_message="Group is created successfully"
        )


class UpdateGroup(graphene.Mutation):
    group = graphene.Field(GroupType)
    verification_message = graphene.String()

    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String(required=True)
        permission = graphene.List(graphene.String)

    @login_required
    def mutate(self, info, **kwargs):
        id = kwargs.get("id")
        name = kwargs.get("name")
        permissions = kwargs.get("permission", [])

        group = Group.objects.get(id=id)
        group.name = name
        group.edited_by = info.context.user
        group.save(update_fields=["edited_by", "name"])

        permissions = Permission.objects.filter(pk__in=permissions)
        for id_ in list(permissions.values_list("id", flat=True)):
            group.permissions.add(int(id_))

        return UpdateGroup(
            group=group, verification_message="Group is updated successfully"
        )


class DeleteGroup(graphene.Mutation):
    verification_message = graphene.String()

    class Arguments:
        id = graphene.Int(required=True)

    @login_required
    def mutate(self, info, id):
        group = Group.objects.get(id=id)
        group.delete()
        return DeleteGroup(verification_message="The group has been deleted.")


class AddUserToGroup(graphene.Mutation):
    user = graphene.Field(UserType)
    group = graphene.Field(GroupType)
    verification_message = graphene.String()

    class Arguments:
        user_id = graphene.String(required=True)
        group_id = graphene.Int(required=True)

    @login_required
    def mutate(self, info, user_id, group_id):
        user = User.objects.filter(id=user_id).first()
        group = Group.objects.filter(id=group_id).first()
        if user and group:
            group.user_set.add(user)
        return AddUserToGroup(
            user=user,
            group=group,
            verification_message="The user has been added to the group.",
        )


class DeleteUserFromGroup(graphene.Mutation):
    group = graphene.Field(GroupType)
    verification_message = graphene.String()

    class Arguments:
        group_id = graphene.Int(required=True)
        user_id = graphene.String(required=True)

    @login_required
    def mutate(self, info, group_id, user_id, **kwargs):
        if not group_id or not user_id:
            raise GraphQLError(
                str(info.context, "Group id and user id both are required!")
            )

        user = User.objects.filter(id=user_id).first()
        if not user:
            raise GraphQLError(
                str(
                    info.context,
                    "No user found by the id provided"
                )
            )

        group = Group.objects.filter(id=group_id).first()
        if not group:
            raise GraphQLError("No group found by the id provided")

        group.user_set.remove(user)
        return DeleteUserFromGroup(
            group=group,
            is_deleted=True,
            verification_message="The user has been removed from the group!",
        )


class ChangePassword(graphene.Mutation):
    user = graphene.Field(UserType, token=graphene.String(required=True))
    verification_message = graphene.String()

    class Arguments:
        password = graphene.String(required=True)
        confirm_password = graphene.String(required=True)

    @login_required
    def mutate(self, info, **kwargs):
        password = kwargs.get("password")
        confirm_password = kwargs.get("confirm_password")

        if password != confirm_password:
            raise GraphQLError("Password and Confirm Passowrd do not match!")

        user = info.context.user
        if user:
            user.set_password(password)
            user.save()
            return ChangePassword(
                user=user,
                verification_message="Password has been changed successfully!",
            )
        raise GraphQLError("User is not logged in, please login to proceed!")


class SetCompanyActiveForUser(graphene.Mutation):
    user = graphene.Field(UserType)
    verification_message = graphene.String()

    class Arguments:
        id = graphene.String(required=True)
        company_id = graphene.String(required=True)

    @login_required
    def mutate(self, info, **kwargs):
        id = kwargs.get("id")
        company_id = kwargs.get("company_id")
        user = User.objects.filter(id=id).first()
        company = Company.objects.filter(id=company_id).first()
        if user and company:
            user.active_company = company.id
            user.save(update_fields=["active_company"])
            return SetCompanyActiveForUser(
                user=user,
                verification_message="Set the company as"
                " active for this user.",
            )
        raise GraphQLError("User or company not found!")


class Mutation(graphene.ObjectType):
    register_user = RegisterUser.Field()
    activate_user = ActivateUser.Field()

    login_user = LoginUser.Field()
    logout_user = LogoutUser.Field()
    reset_password = ResetPassword.Field()
    reset_password_confirm = ResetPasswordConfirm.Field()

    create_group = CreateGroup.Field()
    update_group = UpdateGroup.Field()
    delete_group = DeleteGroup.Field()
    add_user_to_group = AddUserToGroup.Field()
    delete_user_from_group = DeleteUserFromGroup.Field()
    change_password = ChangePassword.Field()
    set_company_active_for_user = SetCompanyActiveForUser.Field()
