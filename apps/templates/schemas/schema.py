from .models import Template, TemplateCategory
from graphene_django import DjangoListField, DjangoObjectType
from graphene_file_upload.scalars import Upload
from graphql_jwt.decorators import staff_member_required
from graphene_django_extras import DjangoFilterPaginateListField, LimitOffsetGraphqlPagination
import graphene
from apps.templates.utils import convert_html_to_docx, convert_html_to_jpeg, convert_html_to_pdf, convert_html_to_png
import base64
from fpdf import FPDF


class TemplateType(DjangoObjectType):
    class Meta:
        model = Template
        fields = '__all__'


class TemplateCategoryType(DjangoObjectType):
    class Meta:
        model = TemplateCategory
        fields = '__all__'


class TemplateFilterType(DjangoObjectType):
    class Meta:
        model = Template
        fields = '__all__'
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'summary': ['icontains'],
            'is_active': ['exact'],
            'is_public': ['exact'],
            'is_approved': ['exact'],
        }


class Query(graphene.ObjectType):
    get_template_by_id = graphene.Field(TemplateType, id=graphene.String())
    get_templates_by_administrator_id = graphene.List(TemplateType)
    get_templates = graphene.List(TemplateType)
    get_public_templates = graphene.List(TemplateType)
    get_template_category_id = graphene.Field(TemplateType, id=graphene.String())
    get_template_categories = graphene.List(TemplateType)
    get_filter_templates = DjangoFilterPaginateListField(TemplateFilterType, pagination=LimitOffsetGraphqlPagination())
    

    def resolve_get_template_by_id(self, info, id):
        return Template.objects.filter(id=id).first()
    
    def resolve_get_templates_by_administrator_id(self, info):
        return Template.objects.filter(company__administrator_id=info.context.user.id)
    
    def resolve_get_templates(self, info):
        return Template.objects.all().order_by('-id')

    def resolve_get_public_templates(self, info):
        return Template.objects.filter(is_approved=True,is_public=True).order_by('-id')
    
    def resolve_get_template_category_id(self, info, id):
        return TemplateCategory.objects.filter(id=id)
    
    def resolve_get_template_categories(self, info):
        return TemplateCategory.objects.all()


class CreateTemplate(graphene.Mutation):
    template = graphene.Field(TemplateType)
    verification_message = graphene.String()

    class Arguments:
        company = graphene.Int(required=True)
        name = graphene.String(required=True)
        summary = graphene.String()
        content_html = graphene.String()
        content_json = graphene.String()
        is_active = graphene.Boolean()
        categories = graphene.List(graphene.String)

    def mutate(self, info, *args, **kwargs):
        company = kwargs.get('company')
        name = kwargs.get('name')
        summary = kwargs.get('summary')
        content_html = kwargs.get('content_html')
        content_json = kwargs.get('content_json')
        is_active = kwargs.get('is_active')
        categories = kwargs.get('categories')

        template = Template.objects.create(company_id=company, name=name, summary=summary, content_json=content_json,
                                            image=image, content_html=content_html, is_active=is_active)
        template.categories.add(categories)
        return CreateTemplate(template=template, verification_message="Template created successfully.")


class CopyTemplate(graphene.Mutation):
    template = graphene.Field(TemplateType)
    verification_message = graphene.String()

    class Arguments:
        template = graphene.String(required=True)

    def mutate(self, info, *args, **kwargs):
        template_id = kwargs.get('template')
        template = Template.objects.filter(id=template_id).first()
        if template:
            clone = template
            clone.pk = None
            clone.save()
        return CopyTemplate(template=clone, verification_message="Template copied successfully.")


class UpdateHTMLinTemplate(graphene.Mutation):
    template = graphene.Field(TemplateType)
    verification_message = graphene.String()

    class Arguments:
        id = graphene.String(required=True)
        html = graphene.String(required=True)

    def mutate(self, info, *arg, **kwargs):
        id = kwargs.get('id')
        html = kwargs.get('html')
    
        template = Template.objects.filter(id=id).first()
        if template and html:
            template.content_html = html
            template.save(update_fields=["content_html",])
            return UpdateHTMLinTemplate(template=template, verification_message="Template html updated successfully.")
        else:
            return UpdateHTMLinTemplate(template=None, verification_message="Template not found.")


class UpdateTemplate(graphene.Mutation):
    templates = graphene.Field(TemplateType)
    verification_message = graphene.String()

    class Arguments:
        id = graphene.String(required=True)
        company = graphene.Int(required=True)
        name = graphene.String(required=True)
        summary = graphene.String()
        content_html = graphene.String()
        content_json = graphene.String()
        is_active = graphene.Boolean()
        categories = graphene.List(graphene.String)

    def mutate(self, info, *arg, **kwargs):
        id = kwargs.get('id')
        company = kwargs.get('company')
        name = kwargs.get('name')
        summary = kwargs.get('summary')
        content_html = kwargs.get('content_html')
        content_json = kwargs.get('content_json')
        is_active = kwargs.get('is_active')
        categories = kwargs.get('categories')


        template = Template.objects.filter(id=id).first()
        if template:
            template.company_id = company
            template.name = name
            template.summary = summary
            template.content_json = content_json
            template.content_html = content_html
            template.is_active = is_active
            template.save(update_fields=["name", "summary", "content_html", "content_json", "is_active", "categories"])
            template.categories.add(categories)
            return UpdateTemplate(templates=template, verification_message="Template updated successfully.")
        else:
            return UpdateTemplate(templates=None, verification_message="Template not found.")


class DeleteTemplate(graphene.Mutation):
    verification_message = graphene.String()

    class Arguments:
        id = graphene.String(required=True)

    def mutate(self, info, id):
        template = Template.objects.filter(id=id).first()
        if template:
            template.delete()
            return DeleteTemplate(verification_message="Template deleted successfully.")
        else:
            return DeleteTemplate(verification_message="Template not found.")


class BatchDeleteTemplate(graphene.Mutation):
    verification_message = graphene.String()

    class Arguments:
        objects = graphene.List(graphene.String, required=True)

    def mutate(self, info, id):
        objects = kwargs.get('objects')
        templates = Template.objects.filter(id__in=objects).delete()
        return DeleteTemplate(verification_message="Templates in batch deleted.")


class ActivateTemplate(graphene.Mutation):
    verification_message = graphene.String()

    class Arguments:
        id = graphene.String(required=True)

    def mutate(self,info,id):
        template = Template.objects.filter(id=id).first()
        if template:
            template.is_active = not template.is_active
            template.save(update_fields=["is_active"])
            return ActivateTemplate(verification_message="Template activated successfully.")
        else:
            return ActivateTemplate(verification_message="Template not found.")



class MakeTemplatePublic(graphene.Mutation):
    verification_message = graphene.String()

    class Arguments:
        id = graphene.String(required=True)

    @staff_member_required
    def mutate(self,info,id):
        template = Template.objects.filter(id=id).first()
        if template:
            template.is_public = not template.is_public
            template.save(update_fields=["is_public"])
            return MakeTemplatePublic(verification_message="Template made public successfully.")
        else:
            return MakeTemplatePublic(verification_message="Template not found.")


class ApprovePublicTemplate(graphene.Mutation):
    verification_message = graphene.String()

    class Arguments:
        id = graphene.String(required=True)

    @staff_member_required
    def mutate(self,info,id):
        template = Template.objects.filter(id=id).first()
        if template:
            template.is_approved = not template.is_approved
            template.save(update_fields=["is_approved"])
            return ApprovePublicTemplate(verification_message="Template approved successfully.")
        else:
            return ApprovePublicTemplate(verification_message="Template not found.")
        

class CreateTemplateCategory(graphene.Mutation):
    template_category = graphene.Field(TemplateCategoryType)
    verification_message = graphene.String()

    class Arguments:
        name = graphene.String(required=True)
        company = graphene.String(required=True)

    def mutate(self, info):
        name = kwargs.get('name')
        company = kwargs.get('company')

        template_category = TemplateCategory.objects.create(
            company_id=company,category=category)
        return CreateTemplateCategory(template_category=template_category, verification_message="Template category created successfully.")


class UpdateTemplateCategory(graphene.Mutation):
    template_category = graphene.Field(TemplateCategoryType)
    verification_message = graphene.String()

    class Arguments:
        id = graphene.String(required=True)
        name = graphene.String(required=True)
        company = graphene.String(required=True)

    def mutate(self, info, id):
        id = kwargs.get('id')
        name = kwargs.get('name')
        company = kwargs.get('company')

        template_category = TemplateCategory.objects.filter(id=id).first()
        if template_category:
            template_category.company_id = company
            template_category.category = category
            template_category.save(update_fields=["company_id", "category"])
            return UpdateTemplateCategory(template_category=template_category, verification_message="Template category updated successfully.")
        else:
            return UpdateTemplateCategory(template_category=None, verification_message="Template category not found.")


class DeleteTemplateCategory(graphene.Mutation):
    verification_message = graphene.String()

    class Arguments:
        id = graphene.String(required=True)

    def mutate(self, info, id):
        template_category = TemplateCategory.objects.filter(id=id).first()
        if template_category:
            template_category.delete()
            return DeleteTemplateCategory(verification_message="Template category deleted successfully.")
        else:
            return DeleteTemplateCategory(verification_message="Template category not found.")


class ExportTemplate(graphene.Mutation):
    verification_message = graphene.String()
    file_url = graphene.String()

    class Arguments:
        id = graphene.String(required=True)
        type = graphene.String(required=True)

    def mutate(self, info, id):
        template = Template.objects.filter(id=id).first()
        if template:
            if type == "pdf":
                file = convert_html_to_pdf(template.content_html)
            elif type == "png":
                file = convert_html_to_png(template.content_html)
            elif type == "docx":
                file = convert_html_to_docx(template.content_html)
            elif type == "jpeg":
                file = convert_html_to_jpeg(template.content_html)
            else:
                file = None                 
            return ExportTemplate(verification_message="Template exported successfully.", file=file)
        else:
            return ExportTemplate(verification_message="Template not found.")


class TemplateMutation(graphene.ObjectType):
    create_template = CreateTemplate.Field()
    update_template = UpdateTemplate.Field()
    update_html_in_template = UpdateHTMLinTemplate.Field()
    delete_template = DeleteTemplate.Field()
    copy_template = CopyTemplate.Field()
    export_template = ExportTemplate.Field()
    batch_delete_template = BatchDeleteTemplate.Field()
    activate_template = ActivateTemplate.Field()
    make_template_public = MakeTemplatePublic.Field()
    approve_public_template = ApprovePublicTemplate.Field()
    create_template_category = CreateTemplateCategory.Field()
    update_template_category = UpdateTemplateCategory.Field()
    delete_template_category = DeleteTemplateCategory.Field()
