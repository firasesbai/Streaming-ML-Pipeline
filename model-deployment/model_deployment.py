from avro_data import *
from confluent_kafka.avro import AvroProducer
from confluent_kafka.avro.cached_schema_registry_client import CachedSchemaRegistryClient
from confluent_kafka.avro.serializer import SerializerError
from confluent_kafka import avro, Consumer
from logger import *
from load_model import *
import datetime
import numpy as np
import os
import pandas as pd

def main():
    logger_name = os.getenv('LOGGER_NAME')

    logger_path = 'logs/' + logger_name + '.log'
    logger_path = logger_name + '.log'
    setup_logger(logger_name, logger_path)
    logger_name = logging.getLogger(logger_name)

    logger_name.info('Loading Configuration...')

    bootstrap_servers = os.getenv('BOOTSTRAP_SERVERS')
    logger_name.info('BOOTSTRAP_SERVERS= ' + str(bootstrap_servers))
    schema_registry_url = os.getenv('SCHEMA_REGISTRY_URL')
    logger_name.info('SCHEMA_REGISTRY_URL= ' + str(schema_registry_url))
    consumer_topic = os.getenv('CONSUMER_TOPIC')
    logger_name.info('CONSUMER_TOPIC= ' + str(consumer_topic))
    producer_topic = os.getenv('PRODUCER_TOPIC')
    logger_name.info('PRODUCER_TOPIC= ' + str(producer_topic))
    group_id = os.getenv('GROUP_ID')
    logger_name.info('GROUP_ID= ' + str(group_id))
    path_key_schema = os.getenv('PATH_KEY_SCHEMA')
    logger_name.info('PATH_KEY_SCHEMA= ' + str(path_key_schema))
    path_value_schema = os.getenv('PATH_VALUE_SCHEMA')
    logger_name.info('PATH_VALUE_SCHEMA= ' + str(path_value_schema))

    path_to_model = os.getenv('PATH_MODEL')
    logger_name.info('MODEL= ' + str(path_to_model))

    path_to_scaler = os.getenv('PATH_SCALER')
    logger_name.info('SCALER= ' + str(path_to_scaler))


    logger_name.info('Loading model and scaler...')
    loaded_model = load_model(path_to_model)
    loaded_scaler = load_scaler(path_to_scaler)

    consumer = Consumer({
    'bootstrap.servers': bootstrap_servers,
    'group.id': group_id
    })
    consumer.subscribe([consumer_topic])

    register_client = CachedSchemaRegistryClient(url=schema_registry_url)

    key_schema = avro.load(path_key_schema)
    value_schema = avro.load(path_value_schema)

    producer = AvroProducer(
    {'bootstrap.servers': bootstrap_servers,
     'schema.registry.url': schema_registry_url},
      default_key_schema=key_schema, default_value_schema=value_schema)

    logger_name.info('Starting Prediction...')
    x_input = []

    while True:
        try:
            msg = consumer.poll()
        except SerializerError as e:
            logger_name.info("Message deserialization failed for {}: {}".format(msg, e))
            raise SerializerError
        if msg.error():
            logger_name.info("AvroConsumer error: {}".format(msg.error()))
            return
        msg_key, msg_value = unpack(msg.key(), 'FALSE', register_client), unpack(msg.value(), 'FALSE', register_client)
			
		observation = [msg_value['item'], msg_value['store'], msg_value['sales']]
        x_input.append(observation)
        if len(x_input)==30:
            x_input = np.array([np.array(element) for element in x_input])
            y_pred = loaded_model.predict(np.reshape(x_input, (1, x_input.shape[0], 3)))
            y_pred_orig = loaded_scaler.inverse_transform(y_pred)
			seconds_since_epoch = datetime.datetime.now().timestamp()
			timestamp = datetime.datetime.fromtimestamp(seconds_since_epoch).strftime('%Y-%m-%d')
            producer.produce(topic=producer_topic, value={'sales_forecast':y_pred_orig[0]}, key={'date':timestamp},
							key_schema=key_schema, value_schema=value_schema)
            producer.flush()
            x_input.pop(0)

if __name__ == '__main__':
    main()
