import google.auth
from google.oauth2 import service_account
from google.cloud import firestore


class FirestoreClient:
    """Wrapper around a database"""

    client: firestore.Client

    def __init__(self) -> None:
        """Init the client."""
        #credentials, _ = google.auth.default()
        credentials = service_account.Credentials.from_service_account_file(
            'TP2and3/careful-maxim-443609-j6-bbedea89fd10.json'  # Remplacez par le chemin réel vers votre fichier de clé
        )
        self.client = firestore.Client(credentials=credentials)

    def get(self, collection_name: str, document_id: str) -> dict:
        """Find one document by ID.
        Args:
            collection_name: The collection name
            document_id: The document id
        Return:
            Document value.
        """
        doc = self.client.collection(
            collection_name).document(document_id).get()
        if doc.exists:
            return doc.to_dict()
        raise FileExistsError(
            f"No document found at {collection_name} with the id {document_id}"
        )

    def create_parameters_document(self, n_estimators: int, criterion: str) -> str:
        """Create the 'parameters' document in the 'parameters' collection.

        Args:
            n_estimators (int): The number of estimators parameter.
            criterion (str): The criterion parameter.
        
        Returns:
            str: A message indicating whether the document was successfully created.
        """
        # Define the data to be written
        parameters_data = {
            'n_estimators': n_estimators,
            'criterion': criterion
        }

        # Create the collection and document
        try:
            self.client.collection('parameters').document('parameters').set(parameters_data)
            return "Document 'parameters' created successfully in 'parameters' collection."
        except Exception as e:
            return f"Error creating document: {e}"
        
# Initialize the FirestoreClient
#firestore_client = FirestoreClient()
# Call the create_parameters_document method and print the result
#result = firestore_client.create_parameters_document(n_estimators=100, criterion='gini')
#print(result)


