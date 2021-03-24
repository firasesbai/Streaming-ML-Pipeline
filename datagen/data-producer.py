from confluent_kafka.avro import AvroProducer
from confluent_kafka.avro.cached_schema_registry_client import CachedSchemaRegistryClient
from confluent_kafka import avro
from logger import *
import csv
import os

def main():
    logger_name = os.getenv('LOGGER_NAME')

    logger_path = logger_name + '.log'
    setup_logger(logger_name, logger_path)
    logger_name = logging.getLogger(logger_name)

    logger_name.info('Loading Configuration...')

    bootstrap_servers = os.getenv('BOOTSTRAP_SERVERS')
    logger_name.info('BOOTSTRAP_SERVERS= ' + str(bootstrap_servers))
    schema_registry_url = os.getenv('SCHEMA_REGISTRY_URL')
    logger_name.info('SCHEMA_REGISTRY_URL= ' + str(schema_registry_url))
    producer_topic = os.getenv('PRODUCER_TOPIC')
    logger_name.info('PRODUCER_TOPIC= ' + str(producer_topic))
    path_key_schema = os.getenv('PATH_KEY_SCHEMA')
    logger_name.info('PATH_KEY_SCHEMA= ' + str(path_key_schema))
    path_value_schema = os.getenv('PATH_VALUE_SCHEMA')
    logger_name.info('PATH_VALUE_SCHEMA= ' + str(path_value_schema))

    path_test_data = os.getenv('PATH_TEST_DATA')
    logger_name.info('PATH_TEST_DATA= ' + str(path_test_data))

    register_client = CachedSchemaRegistryClient(url=schema_registry_url)

    key_schema = avro.load(path_key_schema)
    value_schema = avro.load(path_value_schema)

    producer = AvroProducer(
    {'bootstrap.servers': bootstrap_servers,
     'schema.registry.url': schema_registry_url},
      default_key_schema=key_schema, default_value_schema=value_schema)


    logger_name.info('Starting Data Generation...')
    with open(path_test_data, newline='\n') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            producer.produce(topic=producer_topic, value={'id':int(row['id']), 'date':row['date'], 'store':int(row['store']),
                'item':int(row['item']), 'sales':int(row['sales'])}, key={'id':int(row['id'])}, key_schema=key_schema, value_schema=value_schema)
            producer.flush()
        logger_name.info('Data Generation finished')

if __name__ == '__main__':
    main()