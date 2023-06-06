from google.cloud import bigquery
from google.oauth2 import service_account


class bigqueryConnection(object):

    def __init__(self):
        credentials = service_account.Credentials.from_service_account_file(
            'credentials/service account_key.json')

        project_id = 'thunderz-344909'
        self.client = bigquery.Client(credentials=credentials, project=project_id)
        pass

    def import_data_to_bq_file(self, file_path, table_id):

        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON)

        with open(file_path, "rb") as source_file:
            job = self.client.load_table_from_file(source_file, table_id,
                                                   job_config=job_config)

        job.result()  # Waits for the job to complete.

        table = self.client.get_table(table_id)  # Make an API request.
        print(
            "Loaded {} rows and {} columns to {}".format(
                table.num_rows, len(table.schema), table_id
            )
        )

    def import_data_to_bq_df(self, df, table_id):

        # Define a job config object, with a subset of the schema
        job_config = bigquery.LoadJobConfig(
            schema=[bigquery.SchemaField("Company_Name", "STRING"),
                    bigquery.SchemaField("AppBrain_Site_Link", "STRING"),
                    bigquery.SchemaField("Rating", "STRING"),
                    bigquery.SchemaField("Installs", "STRING"),
                    bigquery.SchemaField("Title", "STRING"),
                    bigquery.SchemaField("Link_to_Store", "STRING"),
                    bigquery.SchemaField("Link_to_Developer", "STRING"),
                    bigquery.SchemaField("LinkedIn_profiles", "RECORD",
                                         mode='REPEATED',
                                         fields=[
                                             bigquery.SchemaField("LinkedIn_position", "STRING"),
                                             bigquery.SchemaField("LinkedIn_link", "STRING")
                                         ]),
                    bigquery.SchemaField("Screenshot_bytes", "BYTES"),
                    bigquery.SchemaField("mail", "STRING"),
                    ]

        )

        # Load data to BQ
        job = self.client.load_table_from_dataframe(df, table_id, job_config=job_config)

        return job

    def import_data_to_bq_df(self, data):

        # Define the dataset and table you want to load the data into
        dataset_id = 'LinkedIn_contacts'
        table_id = 'apps_contact'

        # Get a reference to the table
        table_ref = self.client.dataset(dataset_id).table(table_id)

        table = self.client.get_table(table_ref)
        errors = self.client.insert_rows_json(table, data)

        return errors

    def bq_query(self, query):
        query_job = self.client.query(query)

        results = query_job.result()

        return results
