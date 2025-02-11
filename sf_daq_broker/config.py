DEFAULT_STREAM_OUTPUT_PORT = 12500
DEFAULT_QUEUE_LENGTH = 100
DEFAULT_BROKER_REST_PORT = 10002
DEFAULT_EPICS_WRITER_URL = "http://localhost:10200/notify"
DEFAULT_LOG_LEVEL = "INFO"

BSDATA_RETRIEVAL_DELAY = 60
DETECTOR_RETRIEVAL_DELAY = 10

AUDIT_FILE_TIME_FORMAT = "%Y%m%d-%H%M%S"

DEFAULT_AUDIT_FILENAME = "/var/log/sf_databuffer_audit.log"

DATA_API_QUERY_ADDRESS = "https://data-api.psi.ch/sf-archiverappliance/query"
# sf-daq-5/6
#IMAGE_API_QUERY_ADDRESS = ["http://172.27.0.14:8380/api/1/query", "http://172.27.0.15:8380/api/1/query"]
# sf-daq-14/15
IMAGE_API_QUERY_ADDRESS = ["http://172.27.0.26:8380/api/1/query", "http://172.27.0.27:8380/api/1/query"]
#DATA_API3_QUERY_ADDRESS = "http://sf-daqbuf-33:8371/api/1"
DATA_API3_QUERY_ADDRESS = "https://data-api.psi.ch/api/1"
EPICS_QUERY_ADDRESS = "https://data-api.psi.ch/sf"
PULSEID2SECONDS_MATCHING_ADDRESS = "https://data-api.psi.ch/api/4/map/pulse/sf-databuffer"

DATA_BACKEND = "sf-databuffer"
IMAGE_BACKEND = "sf-imagebuffer"

ERROR_IF_NO_DATA = False
TRANSFORM_PULSE_ID_TO_TIMESTAMP_QUERY = False 
SEPARATE_CAMERA_CHANNELS = True

OUTPUT_FILE_SUFFIX_DATA_BUFFER = "BSREAD"
OUTPUT_FILE_SUFFIX_DATA3_BUFFER = "BSDATA"
OUTPUT_FILE_SUFFIX_EPICS_BUFFER = "PVDATA"
OUTPUT_FILE_SUFFIX_IMAGE_BUFFER = "CAMERAS"
