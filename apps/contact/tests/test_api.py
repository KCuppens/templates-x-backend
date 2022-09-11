from graphene_django.utils.testing import GraphQLTestCase


class ContactTestCase(GraphQLTestCase):
    def test_create_contact(self):
        response = self.query(
            """
            mutation createContact(
                $question: String!,
                $message: String!,
                $email: String!) {
                createContact(
                    question: $question,
                    message: $message,
                    email: $email) {
                    verificationMessage
                }
            }
            """,
            variables={
                "question": "Test question",
                "message": "Test message",
                "email": "Test email",
            }
        )
        assert (
            response.json()["data"]["createContact"]
            ["verificationMessage"]
            ==
            "Thanks for contacting us. "
            "We will get back to you ASAP."
        )
