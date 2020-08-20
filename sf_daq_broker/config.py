DEFAULT_STREAM_OUTPUT_PORT = 12500
DEFAULT_QUEUE_LENGTH = 100
DEFAULT_BROKER_REST_PORT = 10002
DEFAULT_EPICS_WRITER_URL = "http://localhost:10200/notify"
DEFAULT_LOG_LEVEL = "INFO"

DATA_RETRIEVAL_DELAY = 60

AUDIT_FILE_TIME_FORMAT = "%Y%m%d-%H%M%S"

DEFAULT_AUDIT_FILENAME = "/var/log/sf_databuffer_audit.log"

DATA_API_QUERY_ADDRESS = "http://sf-data-api-02.psi.ch/query"
IMAGE_API_QUERY_ADDRESS = "http://172.27.0.14:8080/api/v1/query"
DATA_API3_QUERY_ADDRESS = "http://sf-daqbuf-21:8371/api/1.0.1/query"
EPICS_QUERY_ADDRESS = "https://data-api.psi.ch/sf"

DATA_BACKEND = "sf-databuffer"
IMAGE_BACKEND = "sf-imagebuffer"

ERROR_IF_NO_DATA = False
TRANSFORM_PULSE_ID_TO_TIMESTAMP_QUERY = False 
SEPARATE_CAMERA_CHANNELS = True

OUTPUT_FILE_SUFFIX_DATA_BUFFER = "BSREAD"
OUTPUT_FILE_SUFFIX_IMAGE_BUFFER = "CAMERAS"
OUTPUT_FILE_SUFFIX_EPICS = "PVCHANNELS"
