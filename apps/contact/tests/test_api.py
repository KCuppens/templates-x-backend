from graphql_jwt.testcases import JSONWebTokenTestCase


class ContactTestCase(JSONWebTokenTestCase):
    def test_create_contact(self):
        query ="""
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
            """
        variables = {
            "question": "Test question",
            "message": "Test message",
            "email": "Test email",
        }
        response = self.client.execute(query, variables)
        assert (
            response.data["createContact"]["verificationMessage"]
            == "Thanks for contacting us. We will get back to you ASAP."
        )
