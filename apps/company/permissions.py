from django.core.exceptions import PermissionDenied


def permission_checker(perm):
    def wrapped_decorator(func):
        def wrapped_mutation(cls, root, info, **input):
            # make sure of these arguments to the wrapped mutation
            user = info.context.user
            if isinstance(perm, str):
                perms = (perm, )
            else:
                perms = perm
            
            if user.has_perms(perms):
                return func(cls, root, info, **input)
            raise PermissionDenied("Permission Denied.")
        return wrapped_mutation
    return wrapped_decorator