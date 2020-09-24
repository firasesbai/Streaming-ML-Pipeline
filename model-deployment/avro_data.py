from avro.io import BinaryDecoder, DatumReader
import io
import struct

MAGIC_BYTES = 0

def unpack(payload, windowed, register_client):
    magic, schema_id = struct.unpack('>bi', payload[:5])

    # Get Schema registry
    # Avro value format
    if magic == MAGIC_BYTES:
        schema = register_client.get_by_id(schema_id)
        reader = DatumReader(schema)
        output = BinaryDecoder(io.BytesIO(payload[5:]))
        abc = reader.read(output)
        return abc
    # String key
    else:
        # If Windowed KSQL payload
        if windowed=='TRUE':
            return payload[:-8].decode()
        elif windowed=='FALSE':
            return payload.decode()
