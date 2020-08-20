import logging
import os
import h5py
import numpy

from bsread.data.serialization import channel_type_deserializer_mapping
from sf_daq_broker import config

_logger = logging.getLogger(__name__)


class BsreadH5Writer(object):

    def __init__(self, output_file, metadata):

        self.output_file = output_file

        path_to_file = os.path.dirname(self.output_file)
        os.makedirs(path_to_file, exist_ok=True)

        self.file = h5py.File(self.output_file, "w")
        _logger.info("File %s created." % self.output_file)

        self._create_metadata_datasets(metadata)

    def _create_metadata_datasets(self, metadata):

        _logger.debug("Initializing metadata datasets.")

        for key, value in metadata.items():
            self.file.create_dataset(key, data=numpy.string_(value))

    def _build_datasets_data(self, json_data):

        _logger.debug("Building numpy arrays with received data.")

        if not isinstance(json_data, list):
            raise ValueError("json_data should be a list, but its %s." % type(json_data))

        pulse_ids = set()

        for channel_data in json_data:
            if not isinstance(channel_data, dict):
                raise ValueError("channel_data should be a dict, but its %s." % type(channel_data))
            
            data = channel_data["data"]

            if not data:
                continue

            for data_point in data:
                pulse_ids.add(data_point["pulseId"])

        pulse_ids = sorted(pulse_ids)
        pulse_id_to_data_index = {data: index for index, data in enumerate(pulse_ids)}
        n_data_points = len(pulse_id_to_data_index)

        _logger.info("Built array of pulse_ids. n_data_points=%d" % n_data_points)

        datasets_data = {}
        
        # Channel data format example
        # channel_data = {
        #     "data": [],
        #     "configs": [{"shape": [2], "type": "float32"}],
        #     "channel": {"name": "ARRAY_NO_DATA", "backend": "sf-databuffer"}
        # }

        for channel_data in json_data:
            try:
                name = channel_data["channel"]["name"]
                _logger.debug("Formatting data for channel %s." % name)

                data = channel_data["data"]

                if not data:
                    if config.ERROR_IF_NO_DATA:
                        raise ValueError("There is no data for channel %s." % name)
                    else:
                        _logger.error("There is no data for channel %s." % name)
                
                channel_type = channel_data["configs"][0]["type"]
                channel_shape = channel_data["configs"][0]["shape"]

                dataset_type, dataset_shape = self._get_dataset_definition(channel_type, channel_shape, n_data_points)

                dataset_values = numpy.zeros(dtype=dataset_type, shape=dataset_shape)
                dataset_value_present = numpy.zeros(shape=(n_data_points,), dtype="bool")
                dataset_global_time = numpy.zeros(shape=(n_data_points,), dtype=h5py.special_dtype(vlen=str))

                if data:
                    for data_point in data:
                        data_index = pulse_id_to_data_index[data_point["pulseId"]]

                        if len(channel_shape) > 1:
                            # Bsread is [X, Y] but numpy is [Y, X].
                            data_point["value"] = numpy.array(data_point["value"], dtype=dataset_type).\
                                reshape(channel_shape[::-1])

                        dataset_values[data_index] = data_point["value"]
                        dataset_value_present[data_index] = 1
                        dataset_global_time[data_index] = data_point["globalDate"]

                datasets_data[name] = {
                    "data": dataset_values,
                    "is_data_present": dataset_value_present,
                    "global_date": dataset_global_time
                }

            except Exception as e:
                _logger.error("Cannot convert channel_name %s." % name)

                if config.ERROR_IF_NO_DATA:
                    raise

        return pulse_ids, datasets_data

    def _get_dataset_definition(self, channel_dtype, channel_shape, n_data_points):

        dataset_type = channel_type_deserializer_mapping[channel_dtype][0]
        dataset_shape = [n_data_points] + channel_shape[::-1]

        if channel_dtype == "string":
            dataset_type = h5py.special_dtype(vlen=str)
            dataset_shape = [n_data_points] + channel_shape[::-1]

        return dataset_type, dataset_shape

    def write_data(self, json_data):

        _logger.info("Writing data to disk.")

        pulse_ids, datasets_data = self._build_datasets_data(json_data)

        for name, data in datasets_data.items():
            self.file["/data/" + name + "/pulse_id"] = pulse_ids
            self.file["/data/" + name + "/global_date"] = data["global_date"]
            self.file["/data/" + name + "/data"] = data["data"]
            self.file["/data/" + name + "/is_data_present"] = data["is_data_present"]

    def close(self):
        self.file.close()


class CompactBsreadH5Writer(BsreadH5Writer):

    def _build_datasets_data(self, json_data):

        _logger.debug("Building numpy arrays with received data.")

        datasets_data = {}

        if not isinstance(json_data, list):
            raise ValueError("json_data should be a list, but its %s." % type(json_data))

        for channel_data in json_data:
            
            if not isinstance(channel_data, dict):
                raise ValueError("channel_data should be a dict, but its %s." % type(channel_data))

            try:
                name = channel_data["channel"]["name"]
                _logger.debug("Formatting data for channel %s." % name)

                data = channel_data["data"]
                if not data:
                    if config.ERROR_IF_NO_DATA:
                        raise ValueError("There is no data for channel %s." % name)
                    else:
                        _logger.error("There is no data for channel %s." % name)

                channel_type = channel_data["configs"][0]["type"]
                channel_shape = channel_data["configs"][0]["shape"]

                n_data_points = len(data)
                dataset_type, dataset_shape = self._get_dataset_definition(channel_type, channel_shape, n_data_points)

                dataset_values = numpy.zeros(dtype=dataset_type, shape=dataset_shape)
                dataset_value_present = numpy.zeros(shape=(n_data_points,), dtype="bool")
                dataset_pulse_ids = numpy.zeros(shape=(n_data_points,), dtype="<i8")
                dataset_global_time = numpy.zeros(shape=(n_data_points,), dtype=h5py.special_dtype(vlen=str))

                if data:
                    for data_index, data_point in enumerate(data):

                        if len(channel_shape) > 1:
                            # Bsread is [X, Y] but numpy is [Y, X].
                            data_point["value"] = numpy.array(data_point["value"], dtype=dataset_type).\
                                reshape(channel_shape[::-1])

                        dataset_values[data_index] = data_point["value"]
                        dataset_value_present[data_index] = 1
                        dataset_pulse_ids[data_index] = data_point["pulseId"]
                        dataset_global_time[data_index] = data_point["globalDate"]

                datasets_data[name] = {
                    "data": dataset_values,
                    "is_data_present": dataset_value_present,
                    "pulse_id": dataset_pulse_ids,
                    "global_date": dataset_global_time
                }

            except Exception as e:
                _logger.error("Cannot convert channel_name %s." % name)

                if config.ERROR_IF_NO_DATA:
                    raise

        return datasets_data

    def write_data(self, json_data):

        _logger.info("Writing data to disk.")

        datasets_data = self._build_datasets_data(json_data)

        for name, data in datasets_data.items():
            self.file["/data/" + name + "/pulse_id"] = data["pulse_id"]
            self.file["/data/" + name + "/global_date"] = data["global_date"]
            self.file["/data/" + name + "/data"] = data["data"]
            self.file["/data/" + name + "/is_data_present"] = data["is_data_present"]


def write_from_databuffer(data_api_request, parameters):
    data, data_len = get_data_from_buffer(data_api_request)
    _logger.info("Data retrieval (%d bytes) took %s seconds." % (data_len, time() - start_time))

    start_time = time()
    write_data_to_file(parameters, data)
    _logger.info("Data writing took %s seconds." % (time() - start_time))


def write_from_imagebuffer(data_api_request_pulseid, parameters):
    import data_api3.h5 as h5
    import pytz

    data_api_request = utils.transform_range_from_pulse_id_to_timestamp(data_api_request_pulseid)

    channels = [channel["name"] for channel in data_api_request["channels"]]

    filename = parameters["output_file"]

    start = datetime.fromtimestamp(float(data_api_request["range"]["startSeconds"])).astimezone(pytz.timezone('UTC')).strftime("%Y-%m-%dT%H:%M:%S.%fZ")  # isoformat()  # "2019-12-13T09:00:00.00
    end   = datetime.fromtimestamp(float(data_api_request["range"]["endSeconds"])).astimezone(pytz.timezone('UTC')).strftime("%Y-%m-%dT%H:%M:%S.%fZ")  # isoformat()  # "2019-12-13T09:00:00.00

    query = {
        "channels": channels,
        "range": {
            "type": "date",
            "startDate": start,
            "endDate": end
        }
    }

    _logger.info("Going to make query %s to write file %s from %s " % (query, filename, config.IMAGE_API_QUERY_ADDRESS))

    h5.request(query, filename, url=config.IMAGE_API_QUERY_ADDRESS)


def write_data_to_file(parameters, json_data):

    if not parameters:
        raise ValueError("Received parameters from broker are empty. parameters=%s" % parameters)

    output_file = parameters["output_file"]

    writer = CompactBsreadH5Writer(output_file, parameters)

    writer.write_data(json_data)
    writer.close()


def get_data_from_buffer(data_api_request):

    _logger.info("Loading data for range: %s" % data_api_request["range"])

    _logger.debug("Data API request: %s", data_api_request)

    response = requests.post(url=config.DATA_API_QUERY_ADDRESS, json=data_api_request)

    data, data_len = json.loads(response.content), len(response.content)

    if not data:
        raise ValueError("Received data from data_api is empty. data=%s" % data)

    # The response is a list if status is OK, otherwise its a dictionary, of course.
    if isinstance(data, dict):
        if data.get("status") == 500:
            raise Exception("Server returned error: %s" % data)

        raise Exception("Server returned a dict (keys: %s), but a list was expected." % list(data.keys()))

    return data, data_len
